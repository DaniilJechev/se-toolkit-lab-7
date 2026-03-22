"""LLM client service for intent routing."""
import httpx
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    """Response from LLM with potential tool calls."""
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]]


class LLMClient:
    """Client for interacting with the LLM API with tool calling support."""
    
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
        except Exception as e:
            print(f"LLM error: {e}", file=__import__('sys').stderr)
            return None
    
    async def chat_with_tools(
        self, 
        messages: list[dict], 
        tools: list[dict]
    ) -> LLMResponse:
        """
        Send messages to LLM with tool definitions.
        
        Args:
            messages: Conversation history with role/content dicts.
            tools: List of tool definitions in OpenAI format.
        
        Returns:
            LLMResponse with content and/or tool_calls.
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto"
                }
                
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers,
                    json=payload,
                    timeout=60.0
                )
                resp.raise_for_status()
                data = resp.json()
                
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                content = message.get("content")
                
                tool_calls = []
                if "tool_calls" in message:
                    for tc in message["tool_calls"]:
                        func = tc.get("function", {})
                        try:
                            args = json.loads(func.get("arguments", "{}"))
                        except:
                            args = {}
                        tool_calls.append(ToolCall(
                            id=tc.get("id", "1"),
                            name=func.get("name", ""),
                            arguments=args
                        ))
                
                return LLMResponse(content=content, tool_calls=tool_calls)
                
        except Exception as e:
            print(f"LLM tool error: {e}", file=__import__('sys').stderr)
            return LLMResponse(content=f"LLM error: {str(e)}", tool_calls=None)
    
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
