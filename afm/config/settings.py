import os

DATA_DIR = 'data'
REGISTRY_PATH = f"{DATA_DIR}/registry.json"
LOCKFILE_PATH = f"{DATA_DIR}/lock.json"
PLUGIN_DIR = 'afm/plugins'

# 遠端 registry 路徑（桌面資料夾）
REMOTE_REGISTRY_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "af-registry")
REMOTE_PLUGINS_DIR = os.path.join(REMOTE_REGISTRY_DIR, "plugins")
REMOTE_INDEX_PATH = os.path.join(REMOTE_REGISTRY_DIR, "index.json")
