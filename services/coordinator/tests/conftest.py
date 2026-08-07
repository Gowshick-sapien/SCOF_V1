"""Pytest configuration and path injection for SCOF Coordinator tests."""

from pathlib import Path
import sys

# Inject shared and coordinator src onto sys.path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
shared_path = str(root_dir / "shared")
coordinator_path = str(root_dir / "services" / "coordinator")

if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

if coordinator_path not in sys.path:
    sys.path.insert(0, coordinator_path)
