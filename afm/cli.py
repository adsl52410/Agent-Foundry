import click
from afm.core.installer import install_plugin, uninstall_plugin, update_plugin, write_lockfile
from afm.core.registry import list_plugins
from afm.core.loader import run_plugin
from rich.console import Console

console = Console()

@click.group()
def main():
    pass

@main.command()
@click.argument('name')
def install(name):
    try:
        install_plugin(name)
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

if __name__ == "__main__":
    main()
