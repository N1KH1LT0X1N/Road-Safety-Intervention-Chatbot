"""Configuration manager for CLI."""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manage CLI configuration."""

    def __init__(self):
        """Initialize config manager."""
        self.config_dir = Path.home() / ".road-safety-cli"
        self.config_file = self.config_dir / "config.json"

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load config
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_config(self):
        """Save configuration to file."""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str) -> Optional[str]:
        """Get configuration value."""
        return self.config.get(key)

    def set(self, key: str, value: str):
        """Set configuration value."""
        self.config[key] = value
        self._save_config()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self.config.copy()

    def clear(self):
        """Clear all configuration."""
        self.config = {}
        self._save_config()
