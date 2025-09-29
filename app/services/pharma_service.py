from typing import Dict, Any
from app.utils.text_utils import (
    clean_text, detect_language, extract_medicine_names,
    extract_company_info, extract_batch_info,
    extract_expiry_date, extract_strength_dosage
)

class PharmaService:
    def extract_info(self, ocr_text: str) -> Dict[str, Any]:
        text = clean_text(ocr_text)
        return {
            'raw_text': ocr_text,
            'cleaned_text': text,
            'language': detect_language(text),
            'medicine_names': extract_medicine_names(text),
            'company': extract_company_info(text),
            'batch_number': extract_batch_info(text),
            'expiry_date': extract_expiry_date(text),
            'strength': extract_strength_dosage(text)
        }
