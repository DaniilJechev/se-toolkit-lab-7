"""LLM client service for intent routing."""
import httpx
from typing import Optional, Dict, Any


class LLMClient:
    """Client for interacting with the LLM API."""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat(self, message: str) -> Optional[str]:
        """
        Send a message to the LLM and get a response.
        
        Args:
            message: User message to process.
        
        Returns:
            LLM response text or None if error.
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful LMS assistant."},
                            {"role": "user", "content": message}
                        ]
                    },
                    timeout=30.0
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content")
        except Exception:
            return None
    
    async def classify_intent(self, message: str) -> str:
        """
        Classify user intent from natural language.
        
        Args:
            message: User message to classify.
        
        Returns:
            Intent name (e.g., 'scores', 'labs', 'help', 'unknown').
        """
        prompt = (
            f"Classify this message into one of: scores, labs, submissions, help, health, unknown.\n"
            f"Message: {message}\n"
            f"Intent:"
        )
        response = await self.chat(prompt)
        if response:
            intent = response.strip().lower()
            if intent in ["scores", "labs", "submissions", "help", "health"]:
                return intent
        return "unknown"
