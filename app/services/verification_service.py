from typing import Dict, Any, List
from .database_service import DatabaseService
from app.models.schemas import DatabaseMatch, VerificationResult, CounterfeitRisk
from app.utils.text_utils import fuzzy_match_medicines

class VerificationService:
    def __init__(self):
        self.db = DatabaseService()

    async def verify(self, extracted: Dict[str,Any]) -> Dict[str,Any]:
        names=[m['name'] for m in extracted['medicine_names']]
        all_matches=[]
        for name in names:
            data=await self.db.universal_search(name)
            for item in data:
                # Simplified mapping
                bn=item.get('openfda',{}).get('brand_name',[name])[0]
                gn=item.get('openfda',{}).get('generic_name',[None])[0]
                m=DatabaseMatch(
                    source=item.get('source','db'),
                    medicine_id=item.get('id',None),
                    brand_name=bn,
                    generic_name=gn,
                    manufacturer=item.get('openfda',{}).get('manufacturer_name',[None])[0],
                    country=None,
                    similarity_score=0.0,
                    verified=False
                )
                score=fuzzy_match_medicines(name, [bn], threshold=50)
                if score: m.similarity_score=score[0][1]/100
                m.verified=m.similarity_score>0.7
                all_matches.append(m)
        
        if not all_matches:
            risk=CounterfeitRisk.UNKNOWN
            is_auth=False
            score=0
        else:
            best=max(all_matches,key=lambda x:x.similarity_score)
            score=best.similarity_score
            is_auth=best.verified
            if score>=0.8: risk=CounterfeitRisk.LOW
            elif score>=0.5: risk=CounterfeitRisk.MEDIUM
            else: risk=CounterfeitRisk.HIGH
        
        return VerificationResult(
            is_authentic=is_auth,
            confidence_score=score,
            risk_level=risk,
            matches_found=len(all_matches),
            verification_details={'best_match':best.dict() if all_matches else {}},
            warning_flags=[]
        )
