"""LLM-based intent router with tool calling."""
import json
import sys
from typing import Any, Optional
from dataclasses import dataclass

from services.llm_client import LLMResponse
from services.simple_router import simple_route


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    name: str
    arguments: dict[str, Any]


class IntentRouter:
    """Routes user intents to backend tools using LLM."""
    
    def __init__(self, llm_client, lms_client):
        self.llm = llm_client
        self.lms = lms_client
        
        # Define 9 backend tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get list of all labs and tasks. Use this first to understand available labs.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get list of enrolled students and their groups.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get score distribution (4 buckets) for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task average scores and attempt counts for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submissions per day timeline for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group scores and student counts for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by average score for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                            "limit": {"type": "integer", "description": "Number of top learners to return, default 5"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate percentage for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Trigger ETL pipeline sync to refresh data from autochecker.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]
        
        # Tool name to method mapping
        self.tool_handlers = {
            "get_items": self._call_get_items,
            "get_learners": self._call_get_learners,
            "get_scores": self._call_get_scores,
            "get_pass_rates": self._call_get_pass_rates,
            "get_timeline": self._call_get_timeline,
            "get_groups": self._call_get_groups,
            "get_top_learners": self._call_get_top_learners,
            "get_completion_rate": self._call_get_completion_rate,
            "trigger_sync": self._call_trigger_sync,
        }
    
    async def _call_get_items(self, **kwargs) -> Any:
        return await self.lms.get_items()
    
    async def _call_get_learners(self, **kwargs) -> Any:
        return await self.lms.get_learners()
    
    async def _call_get_scores(self, lab: str) -> Any:
        return await self.lms.get_scores(lab)
    
    async def _call_get_pass_rates(self, lab: str) -> Any:
        return await self.lms.get_pass_rates(lab)
    
    async def _call_get_timeline(self, lab: str) -> Any:
        return await self.lms.get_timeline(lab)
    
    async def _call_get_groups(self, lab: str) -> Any:
        return await self.lms.get_groups(lab)
    
    async def _call_get_top_learners(self, lab: str, limit: int = 5) -> Any:
        return await self.lms.get_top_learners(lab, limit)
    
    async def _call_get_completion_rate(self, lab: str) -> Any:
        return await self.lms.get_completion_rate(lab)
    
    async def _call_trigger_sync(self, **kwargs) -> Any:
        return await self.lms.trigger_sync()
    
    async def execute_tool(self, tool_call: ToolCall) -> Any:
        """Execute a tool call and return result."""
        handler = self.tool_handlers.get(tool_call.name)
        if not handler:
            return f"Error: Unknown tool '{tool_call.name}'"
        
        try:
            result = await handler(**tool_call.arguments)
            print(f"[tool] Result: {len(result) if isinstance(result, (list, dict)) else 'data'} items", file=sys.stderr)
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def route(self, user_message: str) -> str:
        """
        Route user message through LLM with tool calling.
        
        Args:
            user_message: User's natural language message.
        
        Returns:
            Formatted response string.
        """
        system_prompt = """You are an LMS analytics assistant. You have access to backend tools to fetch real data.

AVAILABLE TOOLS:
- get_items(): List all labs and tasks
- get_learners(): List enrolled students
- get_scores(lab): Score distribution for a lab
- get_pass_rates(lab): Per-task pass rates for a lab  
- get_timeline(lab): Submission timeline for a lab
- get_groups(lab): Per-group performance for a lab
- get_top_learners(lab, limit=5): Top N learners
- get_completion_rate(lab): Completion percentage
- trigger_sync(): Refresh data from autochecker

INSTRUCTIONS:
1. For greetings (hello, hi) - respond friendly without tools
2. For lab queries - use tools to get REAL data
3. Always mention specific lab numbers and percentages
4. After receiving tool results, summarize them clearly

To call a tool, respond with:
TOOL: tool_name({"arg": "value"})

Examples:
- "what labs are available?" → TOOL: get_items({})
- "scores for lab 4" → TOOL: get_pass_rates({"lab": "lab-04"})
- "hello" → Hello! I can help you with LMS data...
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM
            response = await self.llm.chat_with_tools(messages, self.tools)
            
            print(f"[LLM] content={response.content[:50] if response.content else 'None'} tool_calls={response.tool_calls}", file=sys.stderr)
            
            # Check if LLM returned tool calls
            if response.tool_calls:
                # Execute tool calls
                tool_results = []
                for tc in response.tool_calls:
                    print(f"[tool] LLM called: {tc.name}({tc.arguments})", file=sys.stderr)
                    result = await self.execute_tool(tc)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, default=str)
                    })
                
                print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)
                
                # Add tool results to messages
                messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments)
                            }
                        }
                        for tc in response.tool_calls
                    ]
                })
                messages.extend(tool_results)
                continue
            
            # LLM returned final answer or error
            if response.content:
                # Check if it's an error - use fallback
                if "error" in response.content.lower() or "401" in response.content:
                    print(f"[fallback] LLM error, using simple routing", file=sys.stderr)
                    return await simple_route(user_message, self.lms)
                return response.content

            # Fallback: try simple routing without LLM
            print(f"[fallback] No tool calls, using simple routing", file=sys.stderr)
            return await simple_route(user_message, self.lms)
        
        return "I need more iterations to answer this. Please try rephrasing."
