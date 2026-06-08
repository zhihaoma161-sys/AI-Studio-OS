"""CLI wrapper for the stable project Codex builder."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from Skills.codex_builder import build_codex


if __name__ == "__main__":
    data_dir = os.environ.get("AI_STUDIO_DATA_DIR", str(ROOT_DIR))
    print(json.dumps(build_codex(data_dir), ensure_ascii=False, indent=2))
