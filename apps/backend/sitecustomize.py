from __future__ import annotations

import sys
from pathlib import Path


backend_workspace_root = Path(__file__).resolve().parent

backend_workspace_root_str = str(backend_workspace_root)
if backend_workspace_root_str not in sys.path:
    sys.path.insert(0, backend_workspace_root_str)
