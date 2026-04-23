import os
from pathlib import Path

from django.core.asgi import get_asgi_application

ultralytics_dir = Path(__file__).resolve().parent.parent / ".ultralytics"
ultralytics_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("ULTRALYTICS_CONFIG_DIR", str(ultralytics_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spacestation_safety.settings")

application = get_asgi_application()
