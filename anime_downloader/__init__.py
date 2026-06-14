"""
AnimePahe Downloader

A Python application for downloading anime episodes from AnimePahe.
"""

__version__ = "5.10.1"

# Main entry points
#
# The CLI / interactive (terminal) interfaces are always available. The GUI is
# imported lazily so the package can be installed and used on minimal,
# terminal-only environments (e.g. Termux on Android) where PyQt6 is not
# available. Importing ``run_gui`` eagerly here would pull in PyQt6 and break
# every terminal-only invocation.
from .main import main
from .cli import cli_main, run_interactive_mode

__all__ = ['main', 'cli_main', 'run_interactive_mode', 'run_gui']


def __getattr__(name):
    """Lazily expose optional GUI entry points without importing PyQt6 eagerly."""
    if name == "run_gui":
        from .gui import run_gui

        return run_gui
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
