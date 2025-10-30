import json, os
from afm.config.settings import REGISTRY_PATH, LOCKFILE_PATH
from rich.console import Console
from rich.table import Table

console = Console()

def list_plugins():
    path = REGISTRY_PATH
    if not os.path.exists(path):
        console.print("🚫 No plugins installed yet", style="yellow")
        return
    with open(path, "r", encoding="utf-8") as fh:
        registry = json.load(fh)
    lock_path = LOCKFILE_PATH
    lock = {}
    if os.path.exists(lock_path):
        with open(lock_path, "r", encoding="utf-8") as lf:
            lock = json.load(lf)
    table = Table(title="Installed Plugins")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("Locked", style="magenta")
    for name, meta in registry.items():
        ver = str(meta.get("version"))
        locked = str(lock.get(name, {}).get("version", ""))
        table.add_row(name, ver, locked)
    console.print(table)
