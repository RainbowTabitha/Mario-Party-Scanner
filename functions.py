import sys
import os

def resource_path(relative_path):
    """Get the absolute path to a resource, works for both development and bundled executable."""
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
