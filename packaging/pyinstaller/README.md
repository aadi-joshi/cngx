# Standalone CLI binaries

cngx release binaries are built with **PyInstaller** (one-file executables per platform).

## Why PyInstaller

- cngx is a Python CLI with native dependencies (`duckdb`, `scipy`, `frouros`) that are awkward to ship any other way without rewriting the tool.
- PyInstaller is the most practical way to bundle those libraries into a single downloadable executable for macOS, Linux, and Windows.
- Alternatives considered: Nuitka (longer builds, more brittle with scientific stacks), shiv/pex (still require a Python runtime on the host).

## Build locally

```bash
python -m build
pip install dist/*.whl
pip install "pyinstaller>=6.0.0"
pyinstaller packaging/pyinstaller/cngx.spec --noconfirm
```

Output: `dist/cngx` (or `dist/cngx.exe` on Windows).

Smoke test:

```bash
./dist/cngx --help
./dist/cngx quickstart
```

CI runs the same build on `release: published` and attaches assets to the GitHub Release.
