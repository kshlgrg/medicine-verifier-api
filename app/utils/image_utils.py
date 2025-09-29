import cv2
import numpy as np
from PIL import Image
import os
from typing import Tuple, Dict
import base64
import io

def setup_directories():
    """Create necessary directories"""
    dirs = ["./data", "./data/temp", "./data/cache", "./data/models"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def validate_image(image_bytes: bytes, max_size: int = 10 * 1024 * 1024) -> bool:
    """Validate image size and format"""
    if len(image_bytes) > max_size:
        return False
    
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img is not None
    except:
        return False

def preprocess_image(image: np.ndarray) -> Dict[str, np.ndarray]:
    """Preprocess image for better OCR results"""
    results = {}
    
    # Original
    results['original'] = image
    
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    results['grayscale'] = gray
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray)
    results['denoised'] = denoised
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    results['enhanced'] = enhanced
    
    # Edge enhancement
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    results['sharpened'] = sharpened
    
    # Threshold for binary image
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results['binary'] = binary
    
    return results

def analyze_image_quality(image: np.ndarray) -> Dict[str, float]:
    """Analyze image quality metrics"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Sharpness (Laplacian variance)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = laplacian.var()
    
    # Brightness
    brightness = np.mean(gray)
    
    # Contrast (standard deviation)
    contrast = np.std(gray)
    
    # Resolution
    height, width = gray.shape
    resolution_score = min(height * width / 100000, 1.0)  # Normalize to 0-1
    
    # Overall quality score
    quality_score = 0
    if sharpness > 100: quality_score += 0.25
    if 50 <= brightness <= 200: quality_score += 0.25
    if contrast > 30: quality_score += 0.25
    if resolution_score > 0.5: quality_score += 0.25
    
    return {
        'sharpness': float(sharpness),
        'brightness': float(brightness),
        'contrast': float(contrast),
        'resolution_score': float(resolution_score),
        'overall_quality': float(quality_score)
    }

def image_to_base64(image: np.ndarray) -> str:
    """Convert image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return image_base64

def base64_to_image(base64_string: str) -> np.ndarray:
    """Convert base64 string to image"""
    image_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image
