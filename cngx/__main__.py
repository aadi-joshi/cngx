"""Allow ``python -m cngx`` and PyInstaller entry."""

from cngx.cli.main import app

if __name__ == "__main__":
    app()
