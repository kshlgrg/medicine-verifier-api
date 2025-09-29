from fastapi.testclient import TestClient
from app.main import app
import io
from PIL import Image
import numpy as np

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Universal Medicine Verifier API"

def test_verify_endpoint():
    """Test medicine verification endpoint"""
    # Create a test image
    img = Image.new('RGB', (400, 200), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    response = client.post(
        "/api/v1/verify",
        files={"image": ("test.png", img_byte_arr, "image/png")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "processing_time" in data
    assert "ocr_result" in data
    assert "verification_result" in data

def test_invalid_image():
    """Test with invalid image"""
    response = client.post(
        "/api/v1/verify",
        files={"image": ("test.txt", b"not an image", "text/plain")}
    )
    
    assert response.status_code == 400
