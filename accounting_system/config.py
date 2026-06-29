import os

# Paths (resolved relative to this file's location)
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "data")
DB_PATH     = os.path.join(DATA_DIR, "store.db")
BACKUPS_DIR = os.path.join(DATA_DIR, "backups")

# Window sizes
LOGIN_WINDOW_WIDTH  = 900
LOGIN_WINDOW_HEIGHT = 600
MAIN_WINDOW_MIN_WIDTH  = 900
MAIN_WINDOW_MIN_HEIGHT = 600

# App info
APP_NAME = "Store Accounting System"

# Default admin credentials (user should change on first run)
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# Password policy
MIN_PASSWORD_LENGTH = 4
