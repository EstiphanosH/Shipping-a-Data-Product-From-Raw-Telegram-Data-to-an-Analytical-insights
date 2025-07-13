import os
import logging

def ensure_directory_exists(path):
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {path}: {str(e)}")
        return False