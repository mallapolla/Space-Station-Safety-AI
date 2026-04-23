#!/usr/bin/env python
import os
import sys
from pathlib import Path


def main() -> None:
    ultralytics_dir = Path(__file__).resolve().parent / ".ultralytics"
    ultralytics_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("ULTRALYTICS_CONFIG_DIR", str(ultralytics_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spacestation_safety.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is not installed. Activate your virtual environment and install requirements."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
