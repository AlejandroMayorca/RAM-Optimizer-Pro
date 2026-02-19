import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

class ConfigManager:
    """
    Manages application configuration and history persistence using JSON.
    Stores data in %APPDATA%/RAMOptimizerPro/config.json.
    """
    
    def __init__(self):
        # Use APPDATA for storing user configuration
        self.app_data_dir = Path(os.environ.get('APPDATA', Path.home())) / "RAMOptimizerPro"
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
            
        self.config_file = self.app_data_dir / "config.json"
        
        self.default_config = {
            "auto_clean": False,
            "threshold": 80.0,
            "minimize_to_tray": True,
            "start_with_windows": False,
            "clean_working_sets": True,
            "clean_standby_list": True,
            "history": []
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Loads configuration from JSON file, falling back to defaults if needed."""
        if not self.config_file.exists():
            return self.default_config.copy()
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in self.default_config.items():
                    if key not in data:
                        data[key] = value
                return data
        except (json.JSONDecodeError, IOError):
            return self.default_config.copy()

    def save_config(self) -> None:
        """Saves current configuration to JSON file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get(self, key: str) -> Any:
        """Retrieves a configuration value."""
        return self.config.get(key, self.default_config.get(key))

    def set(self, key: str, value: Any) -> None:
        """Sets a configuration value and saves to disk."""
        self.config[key] = value
        self.save_config()

    def add_history_entry(self, freed_mb: float) -> None:
        """Adds a cleaning record to history (keeps last 50 entries)."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "freed_mb": freed_mb
        }
        # Maintain only the last 50 records
        if "history" not in self.config:
            self.config["history"] = []
            
        self.config["history"].insert(0, entry)
        self.config["history"] = self.config["history"][:50]
        self.save_config()
