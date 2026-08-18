"""Pytest bootstrap.

The app runs as `demo.main` / `demo.cache`, and `demo/main.py` inserts its own
directory onto `sys.path` so it can `from cache import ...`. We replicate that
here so the test suite can `import main` and `import cache` as top-level
modules (matching how the server launches). `pythonpath = ["demo"]` in
pyproject.toml does the same for bare pytest; this guard covers direct runs.
"""
import sys
from pathlib import Path

_DEMO = Path(__file__).resolve().parent / "demo"
if str(_DEMO) not in sys.path:
    sys.path.insert(0, str(_DEMO))
