import psutil
import ctypes
from ctypes import wintypes
import os
from typing import Dict, List, Optional

# Windows API Constants
PROCESS_SET_QUOTA = 0x0100
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
SYSTEM_MEMORY_LIST_INFORMATION = 80
MEMORY_PURGE_STANDBY_LIST = 4

# Windows API Structures
class SYSTEM_MEMORY_LIST_COMMAND(ctypes.Structure):
    _fields_ = [("Command", ctypes.c_int)]

class LUID(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD),
                ("HighPart", wintypes.LONG)]

class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Luid", LUID),
                ("Attributes", wintypes.DWORD)]

class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [("PrivilegeCount", wintypes.DWORD),
                ("Privileges", LUID_AND_ATTRIBUTES * 1)]

class MemoryManager:
    """
    Handles system memory operations using Windows API (ctypes) and psutil.
    Provides functionality to clean Working Sets and Standby List.
    """
    
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.psapi = ctypes.windll.psapi
        self.ntdll = ctypes.windll.ntdll
        
        # Attempt to enable SeProfileSingleProcessPrivilege for advanced operations
        self._enable_debug_privilege()

    def _enable_debug_privilege(self) -> None:
        """
        Enables SeProfileSingleProcessPrivilege to allow cleaning other processes' memory.
        Failures are silently ignored as this is an enhancement, not a requirement.
        """
        try:
            SE_PRIVILEGE_ENABLED = 0x00000002
            TOKEN_ADJUST_PRIVILEGES = 0x0020
            TOKEN_QUERY = 0x0008
            
            process = self.kernel32.GetCurrentProcess()
            token = ctypes.c_void_p()
            
            if not self.kernel32.OpenProcessToken(process, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(token)):
                return

            luid = LUID()
            if not self.kernel32.LookupPrivilegeValueW(None, "SeProfileSingleProcessPrivilege", ctypes.byref(luid)):
                self.kernel32.CloseHandle(token)
                return

            tp = TOKEN_PRIVILEGES()
            tp.PrivilegeCount = 1
            tp.Privileges[0].Luid = luid
            tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED

            self.kernel32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)
            self.kernel32.CloseHandle(token)
        except Exception:
            # Privilege escalation is optional; failure is acceptable
            pass

    def is_admin(self) -> bool:
        """Checks if the application is running with administrative privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def get_memory_info(self) -> Dict[str, float]:
        """Returns current memory usage statistics in GB and percentage."""
        mem = psutil.virtual_memory()
        return {
            "total": round(mem.total / (1024**3), 2),
            "available": round(mem.available / (1024**3), 2),
            "used": round(mem.used / (1024**3), 2),
            "percent": mem.percent
        }

    def clean_ram(self, clean_working_sets: bool = True, clean_standby_list: bool = True) -> Dict[str, float]:
        """
        Executes the memory optimization process.
        
        Args:
            clean_working_sets: Whether to trim working sets of running processes.
            clean_standby_list: Whether to clear the system standby list (Requires Admin).
            
        Returns:
            Dictionary with freed memory amount and count of cleaned processes.
        """
        mem_before = psutil.virtual_memory().available
        processes_cleaned = 0
        
        # 1. Clean Working Sets (Safe Operation)
        if clean_working_sets:
            processes_cleaned = self._clean_working_sets()

        # 2. Clean Standby List (Advanced Operation - Admin Only)
        if clean_standby_list and self.is_admin():
            self._clean_standby_list()
        
        mem_after = psutil.virtual_memory().available
        freed_bytes = mem_after - mem_before
        freed_mb = max(0.0, round(freed_bytes / (1024**2), 2))
        
        return {
            "freed_mb": freed_mb,
            "processes_cleaned": processes_cleaned
        }

    def _clean_working_sets(self) -> int:
        """Iterates through processes and empties their working set."""
        count = 0
        current_pid = os.getpid()
        
        # Safe-list or critical processes could be skipped here if needed
        # Windows handles EmptyWorkingSet gracefully, but skipping our own process prevents UI stutter
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                # Skip System Idle (0), System (4), and Self
                if pid in [0, 4, current_pid]:
                    continue
                
                handle = self.kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid)
                if handle:
                    if self.psapi.EmptyWorkingSet(handle):
                        count += 1
                    self.kernel32.CloseHandle(handle)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception:
                continue
                
        return count

    def _clean_standby_list(self) -> bool:
        """Invokes NtSetSystemInformation to purge the standby list."""
        try:
            command = SYSTEM_MEMORY_LIST_COMMAND()
            command.Command = MEMORY_PURGE_STANDBY_LIST
            
            result = self.ntdll.NtSetSystemInformation(
                SYSTEM_MEMORY_LIST_INFORMATION,
                ctypes.byref(command),
                ctypes.sizeof(command)
            )
            return result == 0  # NTSTATUS 0 is STATUS_SUCCESS
        except Exception:
            return False

    def get_top_processes(self, limit: int = 10) -> List[Dict]:
        """Returns a list of processes consuming the most memory."""
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                mem_info = proc.info['memory_info']
                # Use RSS (Resident Set Size) for physical memory usage
                mem_mb = round(mem_info.rss / (1024**2), 2)
                procs.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "memory": mem_mb
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        procs.sort(key=lambda x: x['memory'], reverse=True)
        return procs[:limit]
