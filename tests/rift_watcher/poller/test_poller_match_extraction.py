import json
import sys
import types
from datetime import datetime, timezone

# Provide a dummy dotenv module for tests to avoid external dependency
sys.modules.setdefault("dotenv", types.ModuleType("dotenv"))
setattr(sys.modules["dotenv"], "load_dotenv", lambda: None)

from rift_watcher.poller.poller import Poller



