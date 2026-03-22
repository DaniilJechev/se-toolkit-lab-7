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
                headers=self._headers
            )
            resp.raise_for_status()
            return resp.json()
    
    async def get_logs(self) -> List[Dict[str, Any]]:
        """Fetch all logs from the LMS."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/logs/",
                headers=self._headers
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
