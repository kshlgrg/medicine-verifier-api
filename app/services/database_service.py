import aiohttp
import os
from typing import List, Dict, Any

class DatabaseService:
    async def search_openfda(self, name: str) -> List[Dict[str,Any]]:
        url = f"https://api.fda.gov/drug/label.json"
        params={'search':f'openfda.brand_name:"{name}"','limit':5}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params) as r:
                data=await r.json()
                return data.get('results',[])

    async def search_rxnorm(self, name: str) -> List[Dict[str,Any]]:
        url=f"https://rxnav.nlm.nih.gov/REST/drugs.json"
        params={'name':name}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params) as r:
                data=await r.json()
                return data.get('drugGroup',{}).get('conceptGroup',[])

    async def search_drugbank(self, name: str) -> List[Dict[str,Any]]:
        key=os.getenv('DRUGBANK_API_KEY','')
        url="https://api.drugbank.com/v1/us/drugs"
        headers={'Authorization':f'Token {key}'}
        params={'q':name,'limit':5}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, params=params) as r:
                data=await r.json()
                return data.get('drugs',[])

    async def universal_search(self, name: str) -> List[Dict[str,Any]]:
        results=[]
        for fn in (self.search_openfda, self.search_rxnorm, self.search_drugbank):
            try:
                res=await fn(name)
                results.extend(res)
            except: pass
        return results
