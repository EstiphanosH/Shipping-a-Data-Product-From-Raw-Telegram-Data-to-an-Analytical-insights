import pytest
from src.scraper.yolo.process_images import detect_objects

def test_object_detection():
    # Create a test image
    from PIL import Image
    import numpy as np
    
    # Create a simple red image
    img = Image.new('RGB', (100, 100), color='red')
    img_path = "test_image.jpg"
    img.save(img_path)
    
    # Test detection
    detections = detect_objects(img_path)
    assert isinstance(detections, list)
    
    # Cleanup
    import os
    os.remove(img_path)