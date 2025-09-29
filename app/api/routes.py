from fastapi import APIRouter, UploadFile, File, HTTPException
import time
import cv2
import numpy as np

from app.services.ocr_service import OCRService
from app.services.pharma_service import PharmaService
from app.services.verification_service import VerificationService
from app.models.schemas import APIResponse, ErrorResponse

router = APIRouter()

ocr = OCRService()
pharma = PharmaService()
verifier = VerificationService()

@router.post("/verify", response_model=APIResponse, responses={400:{'model':ErrorResponse}})
async def verify_medicine(image: UploadFile=File(...)):
    start=time.time()
    img_bytes=await image.read()
    nparr=np.frombuffer(img_bytes,np.uint8)
    img=cv2.imdecode(nparr,cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400,"Invalid image")
    ocr_res=await ocr.extract_text(img)
    extracted=pharma.extract_info(ocr_res['text'])
    ver_res=await verifier.verify(extracted)
    duration=time.time()-start
    return APIResponse(
        processing_time=duration,
        ocr_result=ocr_res,
        extracted_info=extracted,
        database_matches=[],
        verification_result=ver_res,
        recommendations=[]
    )
