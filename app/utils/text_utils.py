import re
import string
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz
from langdetect import detect, LangDetectError
import country_converter as coco

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep medical ones
    text = re.sub(r'[^\w\s\.\-\/\%\+\(\)]', ' ', text)
    return text.strip()

def detect_language(text: str) -> Optional[str]:
    """Detect text language"""
    try:
        if len(text.strip()) < 10:
            return None
        lang = detect(text)
        return lang
    except LangDetectError:
        return None

def extract_medicine_names(text: str) -> List[Dict[str, any]]:
    """Extract potential medicine names using patterns"""
    text_upper = text.upper()
    medicine_names = []
    
    # Common medicine name patterns
    patterns = [
        # Brand names (all caps words)
        r'\b([A-Z]{4,})\b',
        # Generic names with common endings
        r'\b([A-Z][a-z]+(?:mycin|cillin|prazole|statin|olol|sartan|pril|dipine|azole|tropin))\b',
        # Common Indian medicines
        r'\b(PARACETAMOL|ACETAMINOPHEN|ASPIRIN|IBUPROFEN|CROCIN|DOLO|COMBIFLAM|VICKS|SINAREST)\b',
        # Common antibiotics
        r'\b(AMOXICILLIN|AZITHROMYCIN|CIPROFLOXACIN|DOXYCYCLINE|ERYTHROMYCIN)\b'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text_upper)
        for match in matches:
            name = match.group(1)
            if len(name) >= 3 and not _is_common_word(name):
                medicine_names.append({
                    'name': name.title(),
                    'confidence': 0.8,
                    'method': 'regex_pattern',
                    'position': match.span()
                })
    
    # Remove duplicates
    seen = set()
    unique_names = []
    for med in medicine_names:
        if med['name'].lower() not in seen:
            unique_names.append(med)
            seen.add(med['name'].lower())
    
    return unique_names[:5]  # Top 5 candidates

def extract_company_info(text: str) -> Optional[Dict[str, str]]:
    """Extract pharmaceutical company information"""
    text_upper = text.upper()
    
    # Global pharmaceutical companies
    company_patterns = [
        # Indian companies
        r'\b(CIPLA|SUN\s+PHARMA|DR\.?\s*REDDY|RANBAXY|LUPIN|AUROBINDO|ZYDUS|TORRENT)\b',
        # International companies
        r'\b(GSK|GLAXO|SMITHKLINE|PFIZER|NOVARTIS|MERCK|ABBOTT|SANOFI|BAYER)\b',
        r'\b(JOHNSON|J&J|BRISTOL|MYERS|SQUIBB|ROCHE|ASTRAZENECA)\b',
        # Generic patterns
        r'\b([A-Z]+\s+(?:PHARMA|PHARMACEUTICALS?|LABORATORIES?|LABS?))\b'
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text_upper)
        if match:
            company_name = match.group().strip()
            country = _detect_company_country(company_name)
            return {
                'name': company_name,
                'country': country,
                'confidence': 0.9
            }
    
    return None

def extract_batch_info(text: str) -> Optional[str]:
    """Extract batch/lot number"""
    patterns = [
        r'\b(?:BATCH|LOT|B\.?NO\.?)[\s:]*([A-Z0-9]{3,})\b',
        r'\b(B[A-Z0-9]{3,})\b',
        r'\b([A-Z]{2,3}\d{3,})\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.upper())
        if match:
            return match.group(1)
    
    return None

def extract_expiry_date(text: str) -> Optional[str]:
    """Extract expiry date"""
    patterns = [
        r'\b(?:EXP|EXPIRY|EXPIRES?)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b',
        r'\b(\d{1,2}[\/\-]\d{4})\b',
        r'\b([A-Z]{3}\s*\d{4})\b',
        r'\b(\d{1,2}\.\d{1,2}\.\d{2,4})\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.upper())
        if match:
            return match.group(1)
    
    return None

def extract_strength_dosage(text: str) -> Optional[str]:
    """Extract medicine strength/dosage"""
    patterns = [
        r'\b(\d+(?:\.\d+)?\s*(?:mg|gm|g|mcg|µg|ml|%|units?|iu))\b',
        r'\b(\d+(?:\.\d+)?\/\d+(?:\.\d+)?\s*(?:mg|ml))\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def fuzzy_match_medicines(query: str, medicine_list: List[str], threshold: int = 70) -> List[Tuple[str, int]]:
    """Find fuzzy matches for medicine names"""
    matches = []
    
    for medicine in medicine_list:
        # Try different matching strategies
        ratio = fuzz.ratio(query.lower(), medicine.lower())
        partial_ratio = fuzz.partial_ratio(query.lower(), medicine.lower())
        token_sort_ratio = fuzz.token_sort_ratio(query.lower(), medicine.lower())
        
        # Take the best score
        best_score = max(ratio, partial_ratio, token_sort_ratio)
        
        if best_score >= threshold:
            matches.append((medicine, best_score))
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:10]  # Top 10 matches

def _is_common_word(word: str) -> bool:
    """Check if word is a common non-medicine word"""
    common_words = {
        'TABLETS', 'CAPSULES', 'SYRUP', 'CREAM', 'OINTMENT', 'DROPS',
        'COMPANY', 'PHARMA', 'PHARMACEUTICALS', 'LABORATORIES', 'LABS',
        'BATCH', 'EXPIRY', 'CONTENT', 'STORE', 'KEEP', 'AWAY', 'CHILDREN',
        'MADE', 'INDIA', 'PACK', 'SIZE', 'PLEASE', 'READ', 'LABEL'
    }
    return word.upper() in common_words

def _detect_company_country(company_name: str) -> str:
    """Detect country based on company name"""
    indian_companies = [
        'CIPLA', 'SUN PHARMA', 'DR REDDY', 'RANBAXY', 'LUPIN', 
        'AUROBINDO', 'ZYDUS', 'TORRENT', 'MANKIND', 'HIMALAYA'
    ]
    
    us_companies = [
        'PFIZER', 'MERCK', 'JOHNSON', 'BRISTOL', 'ABBOTT'
    ]
    
    uk_companies = [
        'GSK', 'GLAXO', 'SMITHKLINE', 'ASTRAZENECA'
    ]
    
    company_upper = company_name.upper()
    
    if any(comp in company_upper for comp in indian_companies):
        return 'India'
    elif any(comp in company_upper for comp in us_companies):
        return 'USA'
    elif any(comp in company_upper for comp in uk_companies):
        return 'UK'
    else:
        return 'Unknown'
