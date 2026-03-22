"""LLM-based intent router with tool calling."""
import json
import sys
from typing import Any, Optional
from dataclasses import dataclass

from services.llm_client import LLMResponse


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
                    return await self._simple_route(user_message)
                return response.content

            # Fallback: try simple chat without tools
            print(f"[fallback] No tool calls, using simple routing", file=sys.stderr)
            return await self._simple_route(user_message)
        
        return "I need more iterations to answer this. Please try rephrasing."
    
    async def _simple_route(self, user_message: str) -> str:
        """Simple keyword-based routing as fallback."""
        msg = user_message.lower()
        
        # Greeting
        if any(g in msg for g in ["hello", "hi", "hey"]):
            return "Hello! I can help you with LMS data. Try asking about labs, scores, or students."
        
        # Lowest/worst pass rate comparison
        if "lowest" in msg or "worst" in msg or "best" in msg or "highest" in msg:
            if "lab" in msg and ("pass" in msg or "rate" in msg or "score" in msg):
                print(f"[debug] Checking lowest/highest query", file=sys.stderr)
                # Get all labs and compare
                items = await self.lms.get_items()
                print(f"[debug] Got {len(items)} items", file=sys.stderr)
                labs = [item for item in items if item.get("type") == "lab"]
                print(f"[debug] Found {len(labs)} labs", file=sys.stderr)
                
                if not labs:
                    return "No labs found."
                
                # Get pass rates for each lab
                lab_rates = []
                for lab in labs[:7]:  # Limit to first 7 labs
                    lab_id = f"lab-{str(lab.get('id', '')).zfill(2)}"
                    print(f"[debug] Fetching pass rates for {lab_id}", file=sys.stderr)
                    rates = await self.lms.get_pass_rates(lab_id)
                    print(f"[debug] Got {len(rates) if rates else 0} rates", file=sys.stderr)
                    if rates:
                        avg = sum(t.get('avg_score', 0) for t in rates) / len(rates) if rates else 0
                        lab_rates.append((lab.get('title', lab_id), avg, lab_id))
                
                print(f"[debug] Collected {len(lab_rates)} lab rates", file=sys.stderr)
                
                if not lab_rates:
                    return "No pass rate data available."
                
                # Sort by average
                lab_rates.sort(key=lambda x: x[1], reverse=("best" in msg or "highest" in msg))
                
                if "lowest" in msg or "worst" in msg:
                    result = lab_rates[0]  # Lowest
                    return f"Based on the data, {result[0]} has the lowest average pass rate at {result[1]:.1f}%."
                else:
                    result = lab_rates[0]  # Highest (after reverse sort)
                    return f"Based on the data, {result[0]} has the highest average pass rate at {result[1]:.1f}%."
        
        # Labs
        if "lab" in msg and ("available" in msg or "list" in msg or "what" in msg):
            items = await self.lms.get_items()
            labs = [item for item in items if item.get("type") == "lab"]
            if labs:
                lab_list = "\n".join([f"• {lab.get('title', 'Unknown')}" for lab in labs[:10]])
                return f"📚 Available Labs:\n\n{lab_list}"
            return "No labs found."
        
        # Scores
        if "score" in msg or "pass rate" in msg:
            import re
            match = re.search(r'lab[- ]?(\d+)', msg)
            if match:
                lab_num = match.group(1).zfill(2)
                lab = f"lab-{lab_num}"
                rates = await self.lms.get_pass_rates(lab)
                if rates:
                    lines = [f"📊 Pass rates for {lab}:"]
                    for t in rates:
                        lines.append(f"• {t.get('task', 'Unknown')}: {t.get('avg_score', 0):.1f}% ({t.get('attempts', 0)} attempts)")
                    return "\n".join(lines)
            return "Specify a lab, e.g., 'scores for lab 04'"
        
        # Students/learners
        if "student" in msg or "learner" in msg or "enrolled" in msg:
            learners = await self.lms.get_learners()
            return f"📚 {len(learners)} students enrolled."
        
        # Top learners
        if "top" in msg and ("student" in msg or "learner" in msg):
            import re
            match = re.search(r'lab[- ]?(\d+)', msg)
            if match:
                lab_num = match.group(1).zfill(2)
                lab = f"lab-{lab_num}"
                limit_match = re.search(r'(\d+)', msg)
                limit = int(limit_match.group(1)) if limit_match else 5
                top = await self.lms.get_top_learners(lab, limit)
                if top:
                    lines = [f"🏆 Top {len(top)} learners for {lab}:"]
                    for i, t in enumerate(top, 1):
                        lines.append(f"{i}. Learner #{t.get('learner_id', '?')}: {t.get('avg_score', 0):.1f}% avg")
                    return "\n".join(lines)
            return "Specify a lab, e.g., 'top 5 students in lab 04'"
        
        # Default
        return "I can help with: labs list, scores for a lab, student count. Try 'what labs are available?' or 'scores for lab 04'."
