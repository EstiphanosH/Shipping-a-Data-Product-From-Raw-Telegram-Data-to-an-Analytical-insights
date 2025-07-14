import os
import re
import logging

def ensure_directory_exists(path):
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Directory creation failed: {path} - {str(e)}")
        return False

def sanitize_channel_name(channel):
    """Sanitize channel names for filesystem safety"""
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', channel)