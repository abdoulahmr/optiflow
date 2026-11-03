# config.py
import os
import sys

def get_data_dir():
    """Returns the writable AppData directory for the database."""
    if sys.platform == "win32":
        data_dir = os.path.join(os.getenv('APPDATA'), 'Optiflow')
    else:
        data_dir = os.path.expanduser('~/.optiflow')
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

# Determine if running as a PyInstaller bundle
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BASE_DIR

DATA_DIR = get_data_dir()

DB_NAME = "optiflow.db"
DB_PATH = os.path.join(DATA_DIR, DB_NAME)

# License Server Configuration
LICENSE_SERVER_URL = "https://abdoulahmr.pythonanywhere.com/"
LICENSE_API_TOKEN = "cbfb5ba44ecd30a6d53dff24c53ce91fb3968713beca0a184720c88d4bec4788"