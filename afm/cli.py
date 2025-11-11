import click
from afm.core.installer import (
    install_plugin, uninstall_plugin, update_plugin, write_lockfile,
    publish_plugin, list_remote_plugins
)
from afm.core.registry import list_plugins
from afm.core.loader import run_plugin
from rich.console import Console

console = Console()

@click.group()
def main():
    pass

@main.command()
@click.argument('name')
@click.option('--version', default=None, help='Plugin version to install (e.g. 0.2.0). If not specified, uses latest from remote or default.')
def install(name, version):
    """Install a plugin from remote registry or use local simulation."""
    try:
        install_plugin(name, version)
    except Exception as e:
        raise click.ClickException(str(e))

@main.command()
def list():
    try:
        list_plugins()
    except Exception as e:
        raise click.ClickException(str(e))

@main.command()
@click.argument('name')
@click.option('--args', default='', help='Plugin args')
def run(name, args):
    try:
        run_plugin(name, args)
    except Exception as e:
        raise click.ClickException(str(e))

@main.command()
@click.argument('name')
def uninstall(name):
    """Uninstall a plugin and remove it from registry and lockfile."""
    try:
        uninstall_plugin(name)
    except Exception as e:
        raise click.ClickException(str(e))

@main.command()
@click.argument('name')
@click.option('--version', default=None, help='Target version, e.g. 0.2.0')
def update(name, version):
    """Update a plugin to the latest or specified version."""
    try:
        update_plugin(name, version)
    except Exception as e:
        raise click.ClickException(str(e))

@main.command(name="lock")
def lock_cmd():
    """Regenerate lockfile from current registry (pins exact versions)."""
    try:
        write_lockfile()
    except Exception as e:
        raise click.ClickException(str(e))


@main.command()
@click.argument('name')
@click.option('--version', default=None, help='Plugin version to publish. If not specified, uses version from manifest.')
def publish(name, version):
    """Publish a local plugin to remote registry (Desktop/af-registry)."""
    try:
        publish_plugin(name, version)
    except Exception as e:
        raise click.ClickException(str(e))


@main.command(name="remote-list")
def remote_list():
    """List all plugins available in remote registry."""
    try:
        list_remote_plugins()
    except Exception as e:
        raise click.ClickException(str(e))

if __name__ == "__main__":
    main()
