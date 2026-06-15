from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

SCHEMA_VERSION_KEY = "schema_version"
