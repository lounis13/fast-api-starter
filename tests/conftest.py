# Ensure project root is on sys.path for imports like `import app`
from __future__ import annotations

import os
import sys
import asyncio
import inspect

# Add the project root (one level up from the tests directory) to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Minimal async test support without external plugins (runs async tests via asyncio)

def pytest_pyfunc_call(pyfuncitem):  # type: ignore[override]
    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(testfunction(**pyfuncitem.funcargs))
        finally:
            loop.close()
        return True
    # Let pytest handle non-async tests normally
    return None
