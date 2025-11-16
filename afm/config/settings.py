import os
from pathlib import Path

DATA_DIR = 'data'
REGISTRY_PATH = f"{DATA_DIR}/registry.json"
LOCKFILE_PATH = f"{DATA_DIR}/lock.json"
PLUGIN_DIR = 'afm/plugins'

# Remote registry path (Desktop folder) - Legacy support
REMOTE_REGISTRY_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "af-registry")
REMOTE_PLUGINS_DIR = os.path.join(REMOTE_REGISTRY_DIR, "plugins")
REMOTE_INDEX_PATH = os.path.join(REMOTE_REGISTRY_DIR, "index.json")

# Plugin Registry API configuration
# Priority: user_config.py > environment variable > default
USER_CONFIG_PATH = Path(__file__).parent / 'user_config.py'
_default_api_url = 'https://agent-foundry.org/api/v1'

# Try to load from user_config.py first
PLUGIN_REGISTRY_API_URL = None
if USER_CONFIG_PATH.exists():
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("user_config", USER_CONFIG_PATH)
        user_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_config)
        if hasattr(user_config, 'PLUGIN_REGISTRY_API_URL'):
            PLUGIN_REGISTRY_API_URL = user_config.PLUGIN_REGISTRY_API_URL
    except Exception:
        pass

# Fallback to environment variable if not set in user_config.py
if PLUGIN_REGISTRY_API_URL is None:
    PLUGIN_REGISTRY_API_URL = os.getenv('PLUGIN_REGISTRY_API_URL', _default_api_url)
