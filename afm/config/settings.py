import os

DATA_DIR = 'data'
REGISTRY_PATH = f"{DATA_DIR}/registry.json"
LOCKFILE_PATH = f"{DATA_DIR}/lock.json"
PLUGIN_DIR = 'afm/plugins'

# Remote registry path (Desktop folder) - Legacy support
REMOTE_REGISTRY_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "af-registry")
REMOTE_PLUGINS_DIR = os.path.join(REMOTE_REGISTRY_DIR, "plugins")
REMOTE_INDEX_PATH = os.path.join(REMOTE_REGISTRY_DIR, "index.json")

# Plugin Registry API configuration
# Set via environment variable PLUGIN_REGISTRY_API_URL or use default
PLUGIN_REGISTRY_API_URL = os.getenv('PLUGIN_REGISTRY_API_URL', 'http://localhost:8089/api/v1')
