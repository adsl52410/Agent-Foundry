import os, shutil, json
from afm.config.settings import REGISTRY_PATH, LOCKFILE_PATH, PLUGIN_DIR, DATA_DIR
from rich.console import Console

console = Console()


# paths are provided by settings


def _read_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return default


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _ensure_manifest(plugin_dir, name, version):
    manifest = {
        "name": name,
        "version": version,
        "description": f"Auto-generated manifest for {name}",
        "author": "unknown",
        "dependencies": {},
    }
    with open(f"{plugin_dir}/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def _resolve_dependencies(manifest, registry):
    deps = manifest.get("dependencies", {}) or {}
    # Simplified: if dependency is missing or version does not satisfy, raise immediately
    conflicts = []
    for dep_name, constraint in deps.items():
        installed = registry.get(dep_name)
        if not installed:
            conflicts.append(f"Missing dependency: {dep_name} {constraint}")
            continue
        installed_ver = str(installed.get("version", "0"))
        if not _satisfies(installed_ver, constraint):
            conflicts.append(
                f"Version conflict: {dep_name} installed {installed_ver} does not satisfy {constraint}"
            )
    if conflicts:
        raise RuntimeError("\n".join(conflicts))


def _satisfies(version, constraint):
    # Supported common constraints:
    # - exact: "==1.2.3" or "1.2.3"
    # - lower bound: ">=1.2.3"
    if not constraint or constraint == "*":
        return True
    c = constraint.strip()
    if c.startswith("=="):
        return version == c[2:]
    if c.startswith(">="):
        return _cmp_semver(version, c[2:]) >= 0
    # Default to exact match
    return version == c


def _cmp_semver(a, b):
    def parse(v):
        return [int(x) for x in str(v).split(".")]
    pa, pb = parse(a), parse(b)
    # Normalize length by padding with zeros
    n = max(len(pa), len(pb))
    pa += [0] * (n - len(pa))
    pb += [0] * (n - len(pb))
    for x, y in zip(pa, pb):
        if x < y:
            return -1
        if x > y:
            return 1
    return 0


def write_lockfile():
    registry = _read_json(REGISTRY_PATH, {})
    lock = {name: {"version": meta.get("version")} for name, meta in registry.items()}
    _write_json(LOCKFILE_PATH, lock)
    console.print(f"🔒 Lockfile updated at {LOCKFILE_PATH}", style="green")


def install_plugin(name, version="0.1"):
    console.print(f"✅ Simulating download of plugin: {name}@{version}", style="green")
    plugin_dir = f"{PLUGIN_DIR}/{name}"
    os.makedirs(plugin_dir, exist_ok=True)
    with open(f"{plugin_dir}/plugin.py", "w", encoding="utf-8") as f:
        f.write("def run(args):\n    print('Hello from', args)\n")
    _ensure_manifest(plugin_dir, name, version)

    os.makedirs(DATA_DIR, exist_ok=True)
    registry = _read_json(REGISTRY_PATH, {})

    # Read manifest and validate dependencies
    manifest = _read_json(f"{plugin_dir}/manifest.json", {})
    _resolve_dependencies(manifest, registry)

    registry[name] = {"version": version}
    _write_json(REGISTRY_PATH, registry)
    write_lockfile()


def uninstall_plugin(name):
    plugin_dir = f"{PLUGIN_DIR}/{name}"
    if os.path.isdir(plugin_dir):
        shutil.rmtree(plugin_dir)
        console.print(f"🗑️ Removed plugin files: {name}", style="green")
    else:
        console.print(f"⚠️ Plugin directory does not exist: {plugin_dir}", style="yellow")

    registry = _read_json(REGISTRY_PATH, {})
    if name in registry:
        del registry[name]
        _write_json(REGISTRY_PATH, registry)
        console.print(f"📝 Removed from registry: {name}", style="green")
    lock = _read_json(LOCKFILE_PATH, {})
    if name in lock:
        del lock[name]
        _write_json(LOCKFILE_PATH, lock)
    console.print("🔒 Lockfile synced", style="green")


def update_plugin(name, target_version=None):
    registry = _read_json(REGISTRY_PATH, {})
    if name not in registry:
        raise RuntimeError(f"Plugin not installed: {name}")
    current = str(registry[name].get("version", "0"))
    version = target_version or current
    if target_version and _cmp_semver(target_version, current) == 0:
        console.print(f"ℹ️ {name} already at {current}", style="yellow")
        return
    # Simulate update: rewrite manifest/version
    plugin_dir = f"{PLUGIN_DIR}/{name}"
    if not os.path.isdir(plugin_dir):
        os.makedirs(plugin_dir, exist_ok=True)
    with open(f"{plugin_dir}/plugin.py", "w", encoding="utf-8") as f:
        f.write("def run(args):\n    print('Hello from', args)\n")
    _ensure_manifest(plugin_dir, name, version)

    # Dependency validation
    manifest = _read_json(f"{plugin_dir}/manifest.json", {})
    _resolve_dependencies(manifest, registry)

    registry[name] = {"version": version}
    _write_json(REGISTRY_PATH, registry)
    write_lockfile()
    console.print(f"⬆️ Updated {name} -> {version}", style="green")

# (Removed deprecated duplicate install_plugin implementation)
