import cv2
import numpy as np
from PIL import Image
import pytesseract
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from typing import Dict, Any

class OCRService:
    def __init__(self):
        # Tesseract setup
        self.tesseract_configs = ['--oem 3 --psm 6', '--oem 3 --psm 8']
        
        # TrOCR setup
        try:
            self.trocr_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
            self.trocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
            self.trocr_available = True
        except:
            self.trocr_available = False

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim==3 else image
        denoised = cv2.fastNlMeansDenoising(gray)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        return clahe.apply(denoised)

    def tesseract_ocr(self, image: np.ndarray) -> Dict[str, Any]:
        img = self._preprocess(image)
        pil = Image.fromarray(img)
        best = {'text':'','confidence':0}
        for cfg in self.tesseract_configs:
            text = pytesseract.image_to_string(pil, config=cfg).strip()
            conf = min(len(text)/10,1.0)
            if conf>best['confidence']:
                best={'text':text,'confidence':conf,'method':'tesseract'}
        return best

    def trocr_ocr(self, image: np.ndarray) -> Dict[str, Any]:
        if not self.trocr_available:
            return {'text':'','confidence':0,'method':'trocr_unavailable'}
        pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        inputs = self.trocr_processor(pil, return_tensors='pt').pixel_values
        ids = self.trocr_model.generate(inputs, max_length=256)
        text = self.trocr_processor.batch_decode(ids, skip_special_tokens=True)[0].strip()
        conf = min(len(text)/10,1.0)
        return {'text':text,'confidence':conf,'method':'trocr'}

    async def extract_text(self, image: np.ndarray) -> Dict[str, Any]:
        # Run Tesseract
        t_res = self.tesseract_ocr(image)
        # Run TrOCR
        results = [t_res]
        if self.trocr_available:
            results.append(self.trocr_ocr(image))
        # Choose best
        valid = [r for r in results if r['confidence']>0]
        if not valid:
            return {'text':'','confidence':0,'method':'none'}
        best = max(valid, key=lambda x: (x['confidence'], len(x['text'])))
        best['all_results']=results
        return best
