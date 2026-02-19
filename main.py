import customtkinter as ctk
import threading
import time
import sys
import ctypes
import winreg
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Third-party imports
import pystray
from PIL import Image, ImageDraw

# Local imports
from memory_manager import MemoryManager
from config_manager import ConfigManager

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.environ.get('APPDATA', '.'), 'RAMOptimizerPro', 'app.log')
)

# Constants
AUTO_CLEAN_COOLDOWN = 60  # Seconds
HIGH_MEMORY_THRESHOLD = 500.0  # MB
SYSTEM_PROCESSES = ["MemCompression", "System", "Registry", "System Idle Process"]

# Appearance Setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RAMApp(ctk.CTk):
    """
    Main Application Class for RAM Optimizer Pro.
    Handles UI, System Tray integration, and coordination of memory operations.
    """
    
    def __init__(self):
        # 1. Admin Privilege Check
        if not self.is_admin():
            self.run_as_admin()
            sys.exit(0)

        super().__init__()
        
        # 2. Managers Initialization
        self.config_manager = ConfigManager()
        self.memory_manager = MemoryManager()
        
        # 3. Window Configuration
        self.title("RAM Optimizer Pro")
        self.setup_icon()
        self.geometry("550x700")
        self.resizable(False, False)
        
        # 4. State Variables
        self.is_cleaning = False
        self.last_auto_clean_time = 0
        
        # UI Variables (Linked to Config)
        self.auto_clean_var = ctk.BooleanVar(value=self.config_manager.get("auto_clean"))
        self.threshold_var = ctk.DoubleVar(value=self.config_manager.get("threshold"))
        self.minimize_to_tray_var = ctk.BooleanVar(value=self.config_manager.get("minimize_to_tray"))
        self.start_with_windows_var = ctk.BooleanVar(value=self.config_manager.get("start_with_windows"))
        self.clean_working_sets_var = ctk.BooleanVar(value=self.config_manager.get("clean_working_sets"))
        self.clean_standby_list_var = ctk.BooleanVar(value=self.config_manager.get("clean_standby_list"))

        # 5. UI Setup
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.create_widgets()
        
        # 6. System Tray & Events
        self.tray_icon = None
        self.protocol('WM_DELETE_WINDOW', self.on_closing)
        
        # 7. Start Background Monitoring
        self.start_monitoring()

    def setup_icon(self):
        """Sets the application icon safely."""
        try:
            # Look for icon in assets folder or root
            icon_path = Path(__file__).parent / "assets" / "app.ico"
            if not icon_path.exists():
                icon_path = Path(__file__).parent / "app.ico"
            
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception as e:
            logging.warning(f"Could not load icon: {e}")

    def is_admin(self) -> bool:
        """Checks if the script is running with administrative privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def run_as_admin(self):
        """Relaunches the application with administrative privileges."""
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    def create_widgets(self):
        """Initializes the TabView and all sub-tabs."""
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_dashboard = self.tab_view.add("Dashboard")
        self.tab_processes = self.tab_view.add("Procesos")
        self.tab_history = self.tab_view.add("Historial")
        self.tab_settings = self.tab_view.add("Ajustes")
        
        self.setup_dashboard_tab()
        self.setup_processes_tab()
        self.setup_history_tab()
        self.setup_settings_tab()

    # --- Dashboard Tab ---
    def setup_dashboard_tab(self):
        self.tab_dashboard.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.tab_dashboard, 
            text="MONITOR DE SISTEMA", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=(10, 10))

        # Stats Container
        self.stats_frame = ctk.CTkFrame(self.tab_dashboard, fg_color=("gray90", "gray13"), corner_radius=15)
        self.stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.percent_label = ctk.CTkLabel(
            self.stats_frame, 
            text="0%", 
            font=ctk.CTkFont(size=60, weight="bold"),
            text_color="#3B8ED0"
        )
        self.percent_label.pack(pady=(20, 5))
        
        ctk.CTkLabel(self.stats_frame, text="Uso de RAM", font=ctk.CTkFont(size=14)).pack(pady=(0, 15))

        self.details_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        self.details_frame.pack(fill="x", padx=20, pady=10)
        
        self.lbl_total = self.create_stat_row(self.details_frame, "Total:", "0 GB")
        self.lbl_used = self.create_stat_row(self.details_frame, "Usada:", "0 GB")
        self.lbl_free = self.create_stat_row(self.details_frame, "Disponible:", "0 GB")

        # Optimization Button
        self.btn_optimize = ctk.CTkButton(
            self.tab_dashboard, 
            text="OPTIMIZAR AHORA", 
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            corner_radius=22,
            command=self.run_optimization_thread,
            fg_color="#1F6AA5",
            hover_color="#144870"
        )
        self.btn_optimize.pack(fill="x", padx=40, pady=30)

        # Result Label
        self.result_label = ctk.CTkLabel(
            self.tab_dashboard, 
            text="Listo", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.result_label.pack(pady=(0, 20))

    def create_stat_row(self, parent, title, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        lbl_value = ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=14))
        lbl_value.pack(side="right")
        return lbl_value

    # --- Processes Tab ---
    def setup_processes_tab(self):
        self.tab_processes.grid_columnconfigure(0, weight=1)
        self.tab_processes.grid_rowconfigure(1, weight=1)
        
        header = ctk.CTkFrame(self.tab_processes, height=30)
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(header, text="PID", width=60).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Nombre", width=150, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header, text="RAM (MB)", width=80, anchor="e").pack(side="right", padx=15)
        
        self.scroll_frame_procs = ctk.CTkScrollableFrame(self.tab_processes)
        self.scroll_frame_procs.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.btn_refresh = ctk.CTkButton(
            self.tab_processes,
            text="Actualizar Lista",
            command=self.update_process_list
        )
        self.btn_refresh.grid(row=2, column=0, pady=10)
        
        self.process_widgets = []

    # --- History Tab ---
    def setup_history_tab(self):
        self.tab_history.grid_columnconfigure(0, weight=1)
        self.tab_history.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.tab_history, height=30)
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(header, text="Fecha y Hora", width=150, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Liberado (MB)", width=100, anchor="e").pack(side="right", padx=10)

        self.scroll_frame_history = ctk.CTkScrollableFrame(self.tab_history)
        self.scroll_frame_history.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.btn_refresh_history = ctk.CTkButton(
            self.tab_history,
            text="Refrescar Historial",
            command=self.load_history
        )
        self.btn_refresh_history.grid(row=2, column=0, pady=10)
        
        self.history_widgets = []
        self.load_history()

    # --- Settings Tab ---
    def setup_settings_tab(self):
        self.tab_settings.grid_columnconfigure(0, weight=1)
        
        settings_frame = ctk.CTkFrame(self.tab_settings)
        settings_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(settings_frame, text="Automatización", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.switch_auto = ctk.CTkSwitch(
            settings_frame, 
            text="Limpieza Automática (Inteligente)", 
            variable=self.auto_clean_var,
            command=self.save_settings
        )
        self.switch_auto.pack(pady=10, padx=20, anchor="w")

        ctk.CTkLabel(
            settings_frame, 
            text="Se activará si la RAM supera el umbral.\nTiene una espera de 60s entre limpiezas.",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=(0, 10), padx=20, anchor="w")

        self.lbl_threshold = ctk.CTkLabel(settings_frame, text=f"Umbral de limpieza: {int(self.threshold_var.get())}%")
        self.lbl_threshold.pack(pady=(10,0))
        
        self.slider_threshold = ctk.CTkSlider(
            settings_frame, 
            from_=50, 
            to=95, 
            number_of_steps=45,
            variable=self.threshold_var,
            command=self.update_threshold_label
        )
        self.slider_threshold.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(settings_frame, text="Opciones de Limpieza", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.chk_working_sets = ctk.CTkCheckBox(
            settings_frame,
            text="Limpiar Working Sets (Procesos)",
            variable=self.clean_working_sets_var,
            command=self.save_settings
        )
        self.chk_working_sets.pack(pady=5, padx=20, anchor="w")
        
        self.chk_standby_list = ctk.CTkCheckBox(
            settings_frame,
            text="Limpiar Standby List (Caché)",
            variable=self.clean_standby_list_var,
            command=self.save_settings
        )
        self.chk_standby_list.pack(pady=5, padx=20, anchor="w")

        if not self.memory_manager.is_admin():
            ctk.CTkLabel(
                settings_frame, 
                text="⚠️ Ejecuta como Administrador para limpiar Standby List",
                text_color="#E5B800",
                font=ctk.CTkFont(size=11)
            ).pack(pady=5)

        ctk.CTkLabel(settings_frame, text="Comportamiento", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.switch_tray = ctk.CTkSwitch(
            settings_frame, 
            text="Minimizar a la bandeja al cerrar", 
            variable=self.minimize_to_tray_var,
            command=self.save_settings
        )
        self.switch_tray.pack(pady=10, padx=20, anchor="w")

        self.switch_startup = ctk.CTkSwitch(
            settings_frame,
            text="Iniciar con Windows (Minimizado)",
            variable=self.start_with_windows_var,
            command=self.save_settings
        )
        self.switch_startup.pack(pady=10, padx=20, anchor="w")

        ctk.CTkLabel(
            self.tab_settings,
            text="RAM Optimizer Pro v1.0\nCreated by zPcho",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray50"
        ).pack(side="bottom", pady=20)

    # --- Logic & Events ---
    def set_start_with_windows(self, enable):
        """Adds or removes registry key for startup."""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "RAMOptimizerPro"
        exe_path = sys.executable
        
        if not getattr(sys, 'frozen', False):
            return

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}"')
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            logging.error(f"Registry error: {e}")

    def update_threshold_label(self, value):
        self.lbl_threshold.configure(text=f"Umbral de limpieza: {int(value)}%")
        self.save_settings()

    def save_settings(self):
        self.config_manager.set("auto_clean", self.auto_clean_var.get())
        self.config_manager.set("threshold", self.threshold_var.get())
        self.config_manager.set("minimize_to_tray", self.minimize_to_tray_var.get())
        self.config_manager.set("start_with_windows", self.start_with_windows_var.get())
        self.config_manager.set("clean_working_sets", self.clean_working_sets_var.get())
        self.config_manager.set("clean_standby_list", self.clean_standby_list_var.get())
        
        self.set_start_with_windows(self.start_with_windows_var.get())

    def update_process_list(self):
        for widget in self.process_widgets:
            widget.destroy()
        self.process_widgets.clear()
        threading.Thread(target=self._fetch_processes, daemon=True).start()

    def _fetch_processes(self):
        top_procs = self.memory_manager.get_top_processes(limit=20)
        self.after(0, lambda: self._render_processes(top_procs))

    def _render_processes(self, procs):
        for proc in procs:
            row = ctk.CTkFrame(self.scroll_frame_procs, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=str(proc['pid']), width=60, text_color="gray").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=proc['name'], anchor="w").pack(side="left", padx=5, fill="x", expand=True)
            
            mem_mb = float(proc['memory'])
            color = "#2CC985" # Default Green
            
            # Logic for color coding
            if proc['name'] in SYSTEM_PROCESSES:
                color = "#3B8ED0" # Blue for System
            elif mem_mb > HIGH_MEMORY_THRESHOLD:
                color = "#FF5555" # Red for High Usage
                
            ctk.CTkLabel(row, text=f"{proc['memory']} MB", width=80, anchor="e", font=ctk.CTkFont(weight="bold"), text_color=color).pack(side="right", padx=15)
            
            self.process_widgets.append(row)

    def load_history(self):
        for widget in self.history_widgets:
            widget.destroy()
        self.history_widgets.clear()
        
        history = self.config_manager.get("history")
        for entry in history:
            row = ctk.CTkFrame(self.scroll_frame_history, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=entry['timestamp'], anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"+ {entry['freed_mb']} MB", anchor="e", text_color="#2CC985").pack(side="right", padx=10)
            
            self.history_widgets.append(row)

    def update_stats(self):
        if not self.is_cleaning:
            info = self.memory_manager.get_memory_info()
            
            self.percent_label.configure(text=f"{info['percent']}%")
            self.lbl_total.configure(text=f"{info['total']} GB")
            self.lbl_used.configure(text=f"{info['used']} GB")
            self.lbl_free.configure(text=f"{info['available']} GB")
            
            if info['percent'] > 80:
                self.percent_label.configure(text_color="#C92C2C")
            else:
                self.percent_label.configure(text_color="#3B8ED0")

            if self.minimize_to_tray_var.get() and self.tray_icon:
                self.update_tray_status(info)

            # Auto Clean Logic
            if self.auto_clean_var.get():
                current_time = time.time()
                if (info['percent'] > self.threshold_var.get() and 
                    current_time - self.last_auto_clean_time > AUTO_CLEAN_COOLDOWN):
                    
                    self.last_auto_clean_time = current_time
                    self.run_optimization_thread(auto=True)

        self.after(1000, self.update_stats)

    def start_monitoring(self):
        self.update_stats()
        self.update_process_list()

    def run_optimization_thread(self, auto=False):
        if self.is_cleaning:
            return
        self.is_cleaning = True
        
        if not auto:
            self.btn_optimize.configure(state="disabled", text="OPTIMIZANDO...", fg_color="gray")
            self.result_label.configure(text="Liberando memoria...", text_color="white")
        
        threading.Thread(target=self.optimize_logic, args=(auto,), daemon=True).start()

    def optimize_logic(self, auto):
        time.sleep(0.5)
        
        clean_ws = self.clean_working_sets_var.get()
        clean_sl = self.clean_standby_list_var.get()
        
        result = self.memory_manager.clean_ram(
            clean_working_sets=clean_ws,
            clean_standby_list=clean_sl
        )
        self.after(0, lambda: self.finish_optimization(result, auto))

    def finish_optimization(self, result, auto):
        self.is_cleaning = False
        
        if result['freed_mb'] > 0:
            self.config_manager.add_history_entry(result['freed_mb'])
            self.load_history()

        if not auto:
            self.btn_optimize.configure(state="normal", text="OPTIMIZAR AHORA", fg_color="#1F6AA5")
            msg = f"¡Éxito! Se liberaron {result['freed_mb']} MB"
            self.result_label.configure(text=msg, text_color="#2CC985")
        
        self.update_stats()

    # --- System Tray Integration ---
    def create_tray_image(self):
        """Loads tray icon image with fallback."""
        try:
            icon_path = Path(__file__).parent / "assets" / "app.ico"
            if not icon_path.exists():
                icon_path = Path(__file__).parent / "app.ico"
            
            image = Image.open(str(icon_path))
            return image.convert("RGBA")
        except Exception:
            # Fallback generated icon
            width = 64
            height = 64
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((0, 0, width, height), radius=10, fill="#1F6AA5")
            return image

    def on_closing(self):
        if self.minimize_to_tray_var.get():
            self.withdraw()
            self.show_tray_icon()
        else:
            self.quit_app()

    def show_tray_icon(self):
        if self.tray_icon:
            return
            
        image = self.create_tray_image()
        menu = (
            pystray.MenuItem('Abrir', self.show_window, default=True), 
            pystray.MenuItem('Salir', self.quit_app)
        )
        self.tray_icon = pystray.Icon("RAMOptimizerPro", image, "RAM Optimizer Pro", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def update_tray_status(self, info):
        if self.tray_icon:
            self.tray_icon.title = f"RAM: {info['percent']}% | Libre: {info['available']} GB"

    def show_window(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.after(0, self.deiconify)

    def quit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = RAMApp()
    app.mainloop()
