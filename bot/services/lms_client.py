"""LMS API client service."""
import httpx
from typing import Optional, List, Dict, Any


class LMSClient:
    """Client for interacting with the LMS backend API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {api_key}"}
    
    async def get_items(self) -> List[Dict[str, Any]]:
        """Fetch all items from the LMS."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/items/",
                headers=self._headers,
                timeout=10.0
            )
            resp.raise_for_status()
            return resp.json()
    
    async def get_logs(self) -> List[Dict[str, Any]]:
        """Fetch all logs from the LMS."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/logs/",
                headers=self._headers,
                timeout=10.0
            )
            resp.raise_for_status()
            return resp.json()
    
    async def get_pass_rates(self, lab: str) -> List[Dict[str, Any]]:
        """
        Fetch pass rates for a specific lab.
        
        Args:
            lab: Lab identifier (e.g., 'lab-04').
        
        Returns:
            List of task pass rates with task, avg_score, attempts.
        """
        async with httpx.AsyncClient() as client:
            # Note: endpoint expects query param without trailing slash
            resp = await client.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab},
                headers=self._headers,
                timeout=10.0
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Handle different response formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get("pass_rates", data.get("data", data.get("results", [])))
            return []
    
    async def get_scores(self, lab: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch score distribution."""
        async with httpx.AsyncClient() as client:
            params = {"lab": lab} if lab else {}
            resp = await client.get(
                f"{self.base_url}/analytics/scores",
                params=params,
                headers=self._headers,
                timeout=10.0
            )
            resp.raise_for_status()
            return resp.json()
    
    async def health_check(self) -> bool:
        """Check if the backend is healthy."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/",
                    headers=self._headers,
                    timeout=5.0
                )
                return resp.status_code == 200
        except Exception:
            return False
