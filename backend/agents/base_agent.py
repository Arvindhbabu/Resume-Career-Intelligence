"""
ResumeIQ v2 — Base Agent
Abstract base class for all AI agents in the multi-agent system.
Supports OpenAI, Gemini, and rule-based fallback.
"""

import os
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from backend.config import get_settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for ResumeIQ AI agents.

    Each agent has:
    - A name and description
    - An execute() method that processes input and returns structured output
    - LLM integration with rule-based fallback
    - Execution timing and logging
    """

    name: str = "base_agent"
    description: str = "Base AI Agent"

    def __init__(self):
        self.settings = get_settings()
        self._execution_log: list[dict] = []

    async def run(self, input_data: dict) -> dict:
        """
        Execute the agent with timing, logging, and error handling.

        Args:
            input_data: Agent-specific input

        Returns:
            {"status": "completed", "output": {...}, "duration_ms": int}
        """
        start = time.time()
        logger.info(f"🤖 Agent [{self.name}] starting...")

        try:
            result = await self.execute(input_data)
            duration_ms = int((time.time() - start) * 1000)

            log_entry = {
                "agent": self.name,
                "status": "completed",
                "output": result,
                "duration_ms": duration_ms,
            }
            self._execution_log.append(log_entry)
            logger.info(f"✅ Agent [{self.name}] completed in {duration_ms}ms")

            return log_entry

        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            logger.error(f"❌ Agent [{self.name}] failed: {e}")

            log_entry = {
                "agent": self.name,
                "status": "failed",
                "error": str(e),
                "duration_ms": duration_ms,
            }
            self._execution_log.append(log_entry)

            # Return fallback result
            fallback = await self.fallback(input_data)
            log_entry["output"] = fallback
            log_entry["status"] = "fallback"
            return log_entry

    @abstractmethod
    async def execute(self, input_data: dict) -> dict:
        """Core agent logic. Override in subclasses."""
        pass

    @abstractmethod
    async def fallback(self, input_data: dict) -> dict:
        """Rule-based fallback when LLM is unavailable. Override in subclasses."""
        pass

    def call_llm(self, prompt: str, system_prompt: str = "",
                 response_format: str = "json") -> Optional[str]:
        """
        Call the configured LLM (OpenAI or Gemini).
        Returns raw text response or None on failure.
        """
        if self.settings.OPENAI_API_KEY:
            return self._call_openai(prompt, system_prompt, response_format)
        elif self.settings.GEMINI_API_KEY:
            return self._call_gemini(prompt, system_prompt)
        return None

    def _call_openai(self, prompt: str, system_prompt: str,
                     response_format: str) -> Optional[str]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.settings.OPENAI_API_KEY)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            kwargs = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "max_tokens": self.settings.LLM_MAX_TOKENS,
                "temperature": self.settings.LLM_TEMPERATURE,
            }
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            resp = client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return None

    def _call_gemini(self, prompt: str, system_prompt: str) -> Optional[str]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            resp = model.generate_content(full_prompt)
            return resp.text

        except Exception as e:
            logger.error(f"Gemini call failed: {e}")
            return None

    def parse_llm_json(self, text: Optional[str]) -> dict:
        """Safely parse JSON from LLM response."""
        if not text:
            return {}
        try:
            clean = text.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean
                clean = clean.rsplit("```", 1)[0]
            return json.loads(clean)
        except Exception:
            return {}
