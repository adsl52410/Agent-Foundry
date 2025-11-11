import os, shutil, json
from afm.config.settings import (
    REGISTRY_PATH, LOCKFILE_PATH, PLUGIN_DIR, DATA_DIR,
    REMOTE_REGISTRY_DIR, REMOTE_PLUGINS_DIR, REMOTE_INDEX_PATH
)
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


def _download_from_remote(name, version):
    """從遠端 registry 下載插件到本地"""
    remote_plugin_dir = os.path.join(REMOTE_PLUGINS_DIR, name, version)
    if not os.path.exists(remote_plugin_dir):
        return False
    
    # 檢查遠端是否有必要的檔案
    remote_plugin_file = os.path.join(remote_plugin_dir, "plugin.py")
    remote_manifest_file = os.path.join(remote_plugin_dir, "manifest.json")
    
    if not os.path.exists(remote_plugin_file):
        return False
    
    # 複製到本地
    local_plugin_dir = f"{PLUGIN_DIR}/{name}"
    os.makedirs(local_plugin_dir, exist_ok=True)
    
    # 複製 plugin.py
    shutil.copy2(remote_plugin_file, os.path.join(local_plugin_dir, "plugin.py"))
    
    # 複製 manifest.json（如果存在）
    if os.path.exists(remote_manifest_file):
        shutil.copy2(remote_manifest_file, os.path.join(local_plugin_dir, "manifest.json"))
    else:
        # 如果遠端沒有 manifest，從遠端目錄名稱推斷版本
        _ensure_manifest(local_plugin_dir, name, version)
    
    # 複製其他檔案（如果有的話）
    for item in os.listdir(remote_plugin_dir):
        remote_item_path = os.path.join(remote_plugin_dir, item)
        if os.path.isfile(remote_item_path) and item not in ["plugin.py", "manifest.json"]:
            shutil.copy2(remote_item_path, os.path.join(local_plugin_dir, item))
    
    return True


def install_plugin(name, version=None):
    """安裝插件：優先從遠端 registry 下載，否則使用本地模擬"""
    # 如果沒有指定版本，嘗試從遠端 index 查找最新版本
    if version is None:
        remote_index = _read_json(REMOTE_INDEX_PATH, {})
        if name in remote_index:
            # 取得最新版本
            versions = remote_index[name].get("versions", [])
            if versions:
                version = max(versions, key=lambda v: _parse_version_for_sort(v))
            else:
                version = "0.1"
        else:
            version = "0.1"
    
    # 嘗試從遠端下載
    downloaded = _download_from_remote(name, version)
    
    if downloaded:
        console.print(f"📥 Downloaded plugin from remote: {name}@{version}", style="green")
    else:
        # 如果遠端沒有，使用本地模擬（向後兼容）
        console.print(f"⚠️ Plugin not found in remote registry, using local simulation: {name}@{version}", style="yellow")
        plugin_dir = f"{PLUGIN_DIR}/{name}"
        os.makedirs(plugin_dir, exist_ok=True)
        with open(f"{plugin_dir}/plugin.py", "w", encoding="utf-8") as f:
            f.write("def run(args):\n    print('Hello from', args)\n")
        _ensure_manifest(plugin_dir, name, version)

    os.makedirs(DATA_DIR, exist_ok=True)
    registry = _read_json(REGISTRY_PATH, {})

    # Read manifest and validate dependencies
    plugin_dir = f"{PLUGIN_DIR}/{name}"
    manifest = _read_json(f"{plugin_dir}/manifest.json", {})
    _resolve_dependencies(manifest, registry)

    registry[name] = {"version": version}
    _write_json(REGISTRY_PATH, registry)
    write_lockfile()


def _parse_version_for_sort(version_str):
    """將版本字串轉換為可排序的元組"""
    try:
        parts = version_str.split(".")
        return tuple(int(p) for p in parts)
    except:
        return (0,)


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
    
    # 如果沒有指定版本，嘗試從遠端取得最新版本
    if target_version is None:
        remote_index = _read_json(REMOTE_INDEX_PATH, {})
        if name in remote_index:
            versions = remote_index[name].get("versions", [])
            if versions:
                latest = max(versions, key=lambda v: _parse_version_for_sort(v))
                if _cmp_semver(latest, current) > 0:
                    version = latest
                    console.print(f"📥 Found newer version in remote: {latest}", style="cyan")
                else:
                    console.print(f"ℹ️ {name} already at latest version {current}", style="yellow")
                    return
            else:
                console.print(f"ℹ️ {name} already at {current}, no newer version found", style="yellow")
                return
        else:
            console.print(f"ℹ️ {name} already at {current}, not found in remote registry", style="yellow")
            return
    else:
        version = target_version
    
    if version == current:
        console.print(f"ℹ️ {name} already at {current}", style="yellow")
        return
    
    # 嘗試從遠端下載新版本
    downloaded = _download_from_remote(name, version)
    
    if downloaded:
        console.print(f"📥 Downloaded updated version from remote: {name}@{version}", style="green")
    else:
        # 如果遠端沒有，使用本地模擬（向後兼容）
        console.print(f"⚠️ Updated version not found in remote, using local simulation: {name}@{version}", style="yellow")
        plugin_dir = f"{PLUGIN_DIR}/{name}"
        if not os.path.isdir(plugin_dir):
            os.makedirs(plugin_dir, exist_ok=True)
        with open(f"{plugin_dir}/plugin.py", "w", encoding="utf-8") as f:
            f.write("def run(args):\n    print('Hello from', args)\n")
        _ensure_manifest(plugin_dir, name, version)

    # Dependency validation
    plugin_dir = f"{PLUGIN_DIR}/{name}"
    manifest = _read_json(f"{plugin_dir}/manifest.json", {})
    _resolve_dependencies(manifest, registry)

    registry[name] = {"version": version}
    _write_json(REGISTRY_PATH, registry)
    write_lockfile()
    console.print(f"⬆️ Updated {name} -> {version}", style="green")


def publish_plugin(name, version=None):
    """上傳本地插件到遠端 registry"""
    local_plugin_dir = f"{PLUGIN_DIR}/{name}"
    if not os.path.isdir(local_plugin_dir):
        raise RuntimeError(f"Plugin not found locally: {name}")
    
    # 讀取 manifest 取得版本
    manifest = _read_json(f"{local_plugin_dir}/manifest.json", {})
    if version is None:
        version = manifest.get("version", "0.1")
    
    # 建立遠端目錄
    remote_plugin_dir = os.path.join(REMOTE_PLUGINS_DIR, name, version)
    os.makedirs(remote_plugin_dir, exist_ok=True)
    
    # 複製檔案到遠端
    plugin_file = os.path.join(local_plugin_dir, "plugin.py")
    if not os.path.exists(plugin_file):
        raise RuntimeError(f"Plugin file not found: {plugin_file}")
    
    shutil.copy2(plugin_file, os.path.join(remote_plugin_dir, "plugin.py"))
    
    manifest_file = os.path.join(local_plugin_dir, "manifest.json")
    if os.path.exists(manifest_file):
        shutil.copy2(manifest_file, os.path.join(remote_plugin_dir, "manifest.json"))
    
    # 複製其他檔案
    for item in os.listdir(local_plugin_dir):
        local_item_path = os.path.join(local_plugin_dir, item)
        if os.path.isfile(local_item_path) and item not in ["plugin.py", "manifest.json"]:
            shutil.copy2(local_item_path, os.path.join(remote_plugin_dir, item))
    
    # 更新遠端 index
    remote_index = _read_json(REMOTE_INDEX_PATH, {})
    if name not in remote_index:
        remote_index[name] = {"versions": [], "latest": version}
    
    if version not in remote_index[name]["versions"]:
        remote_index[name]["versions"].append(version)
        remote_index[name]["versions"].sort(key=lambda v: _parse_version_for_sort(v), reverse=True)
    
    remote_index[name]["latest"] = remote_index[name]["versions"][0]
    _write_json(REMOTE_INDEX_PATH, remote_index)
    
    console.print(f"📤 Published plugin to remote: {name}@{version}", style="green")
    console.print(f"   Location: {remote_plugin_dir}", style="dim")


def list_remote_plugins():
    """列出遠端 registry 中可用的插件"""
    remote_index = _read_json(REMOTE_INDEX_PATH, {})
    if not remote_index:
        console.print("🚫 No plugins in remote registry", style="yellow")
        return
    
    from rich.table import Table
    table = Table(title="Remote Registry Plugins")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Latest Version", style="green")
    table.add_column("All Versions", style="magenta")
    
    for name, info in remote_index.items():
        latest = info.get("latest", "N/A")
        versions = ", ".join(info.get("versions", []))
        table.add_row(name, latest, versions)
    
    console.print(table)
