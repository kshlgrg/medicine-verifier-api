from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class CounterfeitRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class MedicineInfo(BaseModel):
    name: str
    confidence: float = Field(ge=0, le=1)
    method: str

class OCRResult(BaseModel):
    text: str
    confidence: float = Field(ge=0, le=1)
    method: str
    engines_used: Optional[int] = None

class ExtractedInfo(BaseModel):
    medicine_names: List[MedicineInfo]
    company: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[str] = None
    strength: Optional[str] = None
    country_detected: Optional[str] = None
    language_detected: Optional[str] = None
    raw_text: str

class DatabaseMatch(BaseModel):
    source: str
    medicine_id: Optional[str] = None
    brand_name: str
    generic_name: Optional[str] = None
    manufacturer: Optional[str] = None
    country: Optional[str] = None
    similarity_score: float = Field(ge=0, le=1)
    verified: bool = False

class VerificationResult(BaseModel):
    is_authentic: bool
    confidence_score: float = Field(ge=0, le=1)
    risk_level: CounterfeitRisk
    matches_found: int
    verification_details: Dict[str, Any]
    warning_flags: List[str] = []

class APIResponse(BaseModel):
    status: str = "success"
    processing_time: float
    ocr_result: OCRResult
    extracted_info: ExtractedInfo
    database_matches: List[DatabaseMatch]
    verification_result: VerificationResult
    recommendations: List[str] = []

class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
