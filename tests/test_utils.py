import numpy as np
from app.utils.image_utils import preprocess_image, analyze_image_quality
from app.utils.text_utils import (
    clean_text, extract_medicine_names, 
    extract_company_info, fuzzy_match_medicines
)

class TestImageUtils:
    def test_preprocess_image(self):
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        result = preprocess_image(img)
        assert isinstance(result, dict)
        assert "original" in result
        assert "grayscale" in result
        assert "enhanced" in result
    
    def test_analyze_quality(self):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = analyze_image_quality(img)
        assert "sharpness" in result
        assert "brightness" in result
        assert "overall_quality" in result
        assert 0 <= result["overall_quality"] <= 1

class TestTextUtils:
    def test_clean_text(self):
        dirty = "  PARACETAMOL   500mg  \n  "
        clean = clean_text(dirty)
        assert clean == "PARACETAMOL 500mg"
    
    def test_extract_medicine_names(self):
        text = "PARACETAMOL 500mg TABLETS ASPIRIN 100mg"
        names = extract_medicine_names(text)
        assert len(names) >= 1
        assert any("PARACETAMOL" in n["name"] for n in names)
    
    def test_extract_company_info(self):
        text = "CIPLA PHARMACEUTICALS LTD"
        company = extract_company_info(text)
        assert company is not None
        assert "CIPLA" in company["name"]
        assert company["country"] == "India"
    
    def test_fuzzy_matching(self):
        query = "PARACETAMOL"
        candidates = ["PARACETAMOL", "ACETAMINOPHEN", "ASPIRIN"]
        matches = fuzzy_match_medicines(query, candidates, threshold=50)
        assert len(matches) > 0
        assert matches[0][0] == "PARACETAMOL"
        assert matches[0][1] == 100
