"""Tests for configuration loader."""

import os
import tempfile
from pathlib import Path
from fmc_agent.config import load_config, AppConfig


def test_load_config_defaults():
    """Test loading configuration with defaults."""
    # Clear any environment variables that might interfere
    env_vars = ["FMC_RVS_SERVER", "FMC_DRY_RUN", "FMC_JSON_LOGGING"]
    old_values = {}
    for var in env_vars:
        old_values[var] = os.environ.pop(var, None)
    
    try:
        config = load_config()
        
        assert config.rv_s_server is None
        assert config.dry_run is False
        assert config.json_logging is False
        
    finally:
        # Restore environment variables
        for var, value in old_values.items():
            if value is not None:
                os.environ[var] = value


def test_load_config_environment_override():
    """Test that environment variables override defaults."""
    # Set environment variables
    os.environ["FMC_RVS_SERVER"] = "test-server.example.com"
    os.environ["FMC_DRY_RUN"] = "true"
    os.environ["FMC_JSON_LOGGING"] = "1"
    
    try:
        config = load_config()
        
        assert config.rv_s_server == "test-server.example.com"
        assert config.dry_run is True
        assert config.json_logging is True
        
    finally:
        # Clean up environment variables
        os.environ.pop("FMC_RVS_SERVER", None)
        os.environ.pop("FMC_DRY_RUN", None)
        os.environ.pop("FMC_JSON_LOGGING", None)


def test_load_config_environment_false_values():
    """Test environment variables with false-like values."""
    os.environ["FMC_DRY_RUN"] = "false"
    os.environ["FMC_JSON_LOGGING"] = "0"
    
    try:
        config = load_config()
        
        assert config.dry_run is False
        assert config.json_logging is False
        
    finally:
        os.environ.pop("FMC_DRY_RUN", None)
        os.environ.pop("FMC_JSON_LOGGING", None)


def test_load_config_environment_yes_values():
    """Test environment variables with 'yes' values."""
    os.environ["FMC_DRY_RUN"] = "yes"
    os.environ["FMC_JSON_LOGGING"] = "YES"
    
    try:
        config = load_config()
        
        assert config.dry_run is True
        assert config.json_logging is True
        
    finally:
        os.environ.pop("FMC_DRY_RUN", None)
        os.environ.pop("FMC_JSON_LOGGING", None)


def test_load_config_from_file():
    """Test loading configuration from file."""
    # Create a temporary config file
    config_content = '''
# FMC Agent Configuration
rv_s_server = "config-server.example.com"
dry_run = true
json_logging = false
'''
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory and create config file
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            config_path = Path("fmc.toml")
            config_path.write_text(config_content)
            
            config = load_config()
            
            assert config.rv_s_server == "config-server.example.com"
            assert config.dry_run is True
            assert config.json_logging is False
            
        finally:
            os.chdir(original_cwd)


def test_load_config_file_with_quotes():
    """Test loading configuration file with quoted values."""
    config_content = '''
rv_s_server="quoted-server.example.com"
dry_run='true'
json_logging = "false"
'''
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            config_path = Path("fmc.toml")
            config_path.write_text(config_content)
            
            config = load_config()
            
            assert config.rv_s_server == "quoted-server.example.com"
            assert config.dry_run is True
            assert config.json_logging is False
            
        finally:
            os.chdir(original_cwd)


def test_load_config_dotfile():
    """Test loading configuration from .fmc.toml file."""
    config_content = '''
rv_s_server = dotfile-server.example.com
'''
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            config_path = Path(".fmc.toml")
            config_path.write_text(config_content)
            
            config = load_config()
            
            assert config.rv_s_server == "dotfile-server.example.com"
            
        finally:
            os.chdir(original_cwd)


def test_load_config_file_precedence():
    """Test that fmc.toml takes precedence over .fmc.toml."""
    fmc_content = '''
rv_s_server = fmc-server.example.com
'''
    
    dotfmc_content = '''
rv_s_server = dotfmc-server.example.com
'''
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Create both files
            Path("fmc.toml").write_text(fmc_content)
            Path(".fmc.toml").write_text(dotfmc_content)
            
            config = load_config()
            
            # fmc.toml should take precedence
            assert config.rv_s_server == "fmc-server.example.com"
            
        finally:
            os.chdir(original_cwd)


def test_load_config_env_overrides_file():
    """Test that environment variables override file configuration."""
    config_content = '''
rv_s_server = file-server.example.com
dry_run = false
'''
    
    os.environ["FMC_RVS_SERVER"] = "env-server.example.com"
    os.environ["FMC_DRY_RUN"] = "true"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            config_path = Path("fmc.toml")
            config_path.write_text(config_content)
            
            config = load_config()
            
            # Environment should override file
            assert config.rv_s_server == "env-server.example.com"
            assert config.dry_run is True
            
        finally:
            os.chdir(original_cwd)
            os.environ.pop("FMC_RVS_SERVER", None)
            os.environ.pop("FMC_DRY_RUN", None)


def test_load_config_invalid_file():
    """Test that invalid config file is silently ignored."""
    config_content = '''
invalid toml content
this should be ignored
'''
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            config_path = Path("fmc.toml")
            config_path.write_text(config_content)
            
            # Should not raise exception, just use defaults
            config = load_config()
            
            assert config.rv_s_server is None
            assert config.dry_run is False
            assert config.json_logging is False
            
        finally:
            os.chdir(original_cwd)


def test_app_config_dataclass():
    """Test AppConfig dataclass functionality."""
    # Test with defaults
    config = AppConfig()
    assert config.rv_s_server is None
    assert config.dry_run is False
    assert config.json_logging is False
    
    # Test with custom values
    config = AppConfig(
        rv_s_server="test-server",
        dry_run=True,
        json_logging=True
    )
    assert config.rv_s_server == "test-server"
    assert config.dry_run is True
    assert config.json_logging is True