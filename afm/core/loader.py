import importlib.util
import os
from afm.config.settings import PLUGIN_DIR

def run_plugin(name, args):
    plugin_path = f"{PLUGIN_DIR}/{name}/plugin.py"
    if not os.path.isfile(plugin_path):
        raise RuntimeError(f"Plugin file not found: {plugin_path}")
    spec = importlib.util.spec_from_file_location("plugin", plugin_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load plugin module from: {plugin_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "run"):
        raise RuntimeError(f"Plugin '{name}' missing required function: run(args)")
    mod.run(args)
