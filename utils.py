import sys
import os

def resource_path(relative_path):
    """
    Get absolute path to resource, works for both development and PyInstaller builds.
    """
    try:
        # PyInstaller creates a temporary folder and stores path in `_MEIPASS`.
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
