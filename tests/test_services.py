import pytest
import numpy as np
from app.services.ocr_service import OCRService
from app.services.pharma_service import PharmaService
from app.services.verification_service import VerificationService

@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    return np.ones((100, 200, 3), dtype=np.uint8) * 255

@pytest.fixture
def sample_text():
    """Sample OCR text for testing"""
    return "PARACETAMOL 500mg CIPLA PHARMACEUTICALS BATCH: ABC123 EXP: 12/2026"

class TestOCRService:
    def test_tesseract_ocr(self, sample_image):
        ocr = OCRService()
        result = ocr.tesseract_ocr(sample_image)
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert "method" in result

class TestPharmaService:
    def test_extract_info(self, sample_text):
        pharma = PharmaService()
        result = pharma.extract_info(sample_text)
        assert isinstance(result, dict)
        assert "medicine_names" in result
        assert "company" in result
        assert "batch_number" in result
        assert len(result["medicine_names"]) > 0

@pytest.mark.asyncio
class TestVerificationService:
    async def test_verify(self, sample_text):
        pharma = PharmaService()
        verifier = VerificationService()
        
        extracted = pharma.extract_info(sample_text)
        result = await verifier.verify(extracted)
        
        assert hasattr(result, 'is_authentic')
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'risk_level')
