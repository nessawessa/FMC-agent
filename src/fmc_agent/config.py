"""Configuration loader for FMC Agent."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration."""
    rv_s_server: Optional[str] = None
    dry_run: bool = False
    json_logging: bool = False


def load_config() -> AppConfig:
    """Load configuration from files and environment variables."""
    config = AppConfig()
    
    # Search for config files in current working directory
    config_files = ["fmc.toml", ".fmc.toml"]
    
    for config_file in config_files:
        config_path = Path.cwd() / config_file
        if config_path.exists():
            # For now, we'll implement a simple parser
            # In a full implementation, we'd use tomllib (Python 3.11+) or tomli
            try:
                config_text = config_path.read_text()
                # Simple parsing for basic key=value pairs
                for line in config_text.split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        if key == "rv_s_server":
                            config.rv_s_server = value
                        elif key == "dry_run":
                            config.dry_run = value.lower() in ("true", "1", "yes")
                        elif key == "json_logging":
                            config.json_logging = value.lower() in ("true", "1", "yes")
            except Exception:
                # Silently ignore config file parsing errors for now
                pass
            break
    
    # Overlay environment variables
    if os.getenv("FMC_RVS_SERVER"):
        config.rv_s_server = os.getenv("FMC_RVS_SERVER")
    
    if os.getenv("FMC_DRY_RUN"):
        config.dry_run = os.getenv("FMC_DRY_RUN", "").lower() in ("true", "1", "yes")
    
    if os.getenv("FMC_JSON_LOGGING"):
        config.json_logging = os.getenv("FMC_JSON_LOGGING", "").lower() in ("true", "1", "yes")
    
    return config