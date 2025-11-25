from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

# Your existing imports (kept!)
from .intent_schema import Intent
from backend.app.services.parser.intent_mapper import IntentMapper


# =====================================================
# Base ParsedCommand + Abstract Base Parser (NEW — REQUIRED BY STEP 6)
# =====================================================

class ParsedCommand:
    """
    Normalized representation of a user command
    matching intent.schema.json.
    """
    def __init__(
        self,
        command: str,
        intent: Optional[str] = None,
        action: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.command = command
        self.intent = intent
        self.action = action
        self.parameters = parameters or {}
        self.context = context or {}

    def to_dict(self):
        return {
            "command": self.command,
            "intent": self.intent,
            "action": self.action,
            "parameters": self.parameters,
            "context": self.context,
        }


class BaseCommandParser(ABC):
    """
    Step 6 Day 2 requirement:
    All parsers must expose parse(), extract(), validate().
    """

    @abstractmethod
    def parse(self, text: str, context: Optional[Dict[str, Any]] = None) -> ParsedCommand:
        raise NotImplementedError

    @abstractmethod
    def extract(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def validate(self, payload: Dict[str, Any]) -> None:
        raise NotImplementedError


# =====================================================
# Regex Baseline Parser (NEW — Non-breaking fallback)
# =====================================================

class RegexCommandParser(BaseCommandParser):
    """
    Simple fallback parser for testing / early integration.
    """

    ACTION_PATTERN = re.compile(r"^\s*(?P<action>\w+)\b(?P<rest>.*)$", re.IGNORECASE)

    def parse(self, text: str, context: Optional[Dict[str, Any]] = None) -> ParsedCommand:
        context = context or {}
        payload = self.extract(text, context=context)
        self.validate(payload)
        return ParsedCommand(
            command=text,
            intent=payload.get("intent"),
            action=payload.get("action"),
            parameters=payload.get("parameters", {}),
            context=payload.get("context", {}),
        )

    def extract(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        m = self.ACTION_PATTERN.match(text)
        if not m:
            return {
                "command": text,
                "intent": None,
                "action": None,
                "parameters": {},
                "context": context,
            }

        action = m.group("action").lower()
        rest = m.group("rest").strip()

        return {
            "command": text,
            "intent": None,
            "action": action,
            "parameters": {"raw_text": rest},
            "context": context,
        }

    def validate(self, payload: Dict[str, Any]) -> None:
        if not payload.get("command"):
            raise ValueError("Command text is required.")


# =====================================================
# LLM Client Wrapper (PRESERVED)
# =====================================================

@dataclass
class LLMClient:
    name: str
    call: Callable[..., Dict[str, Any]]

    def __call__(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return self.call(prompt=prompt, **kwargs)


# =====================================================
# Constants (PRESERVED)
# =====================================================

SUPPORTED_DOMAINS = {"trading", "logistics", "docs"}
DEFAULT_PROMPT_VERSION = "v1"

ALLOWED_ACTIONS = {
    "db_update",
    "sheets_update",
    "email_send",
    "chat_post",
    "doc_generate",
}

DESTRUCTIVE_ACTIONS = {
    "db_update",
    "sheets_update",
}


@dataclass
class PromptMetadata:
    domain: str
    version: str
    template_name: str


# =====================================================
# FULL LLM-BASED COMMAND PARSER (YOUR ORIGINAL ONE — INTACT)
# =====================================================

class CommandParser:
    """
    Full LLM-backed Command Parser for ORKO.
    """

    def __init__(self, llm_client: LLMClient = None, default_domain: str = "trading"):
        self.llm_client = llm_client
        self.default_domain = default_domain
        self.mapper = IntentMapper()

    # ------------------------
    # Parse
    # ------------------------
    async def parse(
        self,
        raw_command: str,
        *,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Intent:

        if not raw_command or not raw_command.strip():
            raise ValueError("raw_command must be a non-empty string")

        prompt_payload = self._build_prompt(
            raw_command=raw_command,
            domain=domain,
            context=context,
        )

        raw_response = await self._call_llm(prompt_payload)
        intent = self.extract(raw_response)
        intent = self.validate(intent)
        return intent

    # ------------------------
    # Parse + Map
    # ------------------------
    async def parse_and_map(
        self,
        raw_command: str,
        *,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        intent = await self.parse(raw_command, domain=domain, context=context)
        mapped = self.mapper.map(intent, context or {})
        return intent, mapped

    # ------------------------
    # Prompt builder
    # ------------------------
    def _build_prompt(self, raw_command: str, domain: Optional[str], context: Optional[Dict[str, Any]]):
        selected_domain = (domain or self.default_domain or "trading").lower()
        if selected_domain not in SUPPORTED_DOMAINS:
            selected_domain = self.default_domain

        system = (
            "You are ORKO's command parser. "
            "You MUST respond with valid JSON matching the intent schema: "
            "{command, action, parameters, context, risk_level, requires_confirmation}."
        )

        user_lines = [
            f"Domain: {selected_domain}",
            f"Prompt version: {DEFAULT_PROMPT_VERSION}",
            "",
            "User command:",
            raw_command.strip(),
        ]

        if context:
            user_lines.append("\nContext:")
            for key, value in context.items():
                user_lines.append(f"- {key}: {value}")

        user = "\n".join(user_lines)

        prompt_meta = PromptMetadata(
            domain=selected_domain,
            version=DEFAULT_PROMPT_VERSION,
            template_name=f"{selected_domain}_base",
        )

        return {
            "system": system,
            "user": user,
            "metadata": {
                "domain": selected_domain,
                "prompt_version": DEFAULT_PROMPT_VERSION,
                "template_name": prompt_meta.template_name,
            },
        }

    # ------------------------
    # LLM call
    # ------------------------
    async def _call_llm(self, prompt_payload: Dict[str, Any]):
        return self.llm_client(prompt=prompt_payload)

    # ------------------------
    # Extract
    # ------------------------
    def extract(self, raw_response: Dict[str, Any]) -> Intent:
        if not isinstance(raw_response, dict):
            raise ValueError("raw_response must be a dict")

        content = raw_response.get("content")
        if not isinstance(content, dict):
            raise ValueError("raw_response['content'] must be a dict")

        raw_text = raw_response.get("raw_text")
        if raw_text and "raw_text" not in content:
            content.setdefault("raw_text", raw_text)

        return Intent(**content)

    # ------------------------
    # Validate
    # ------------------------
    def validate(self, intent: Intent) -> Intent:
        action = intent.action

        if action not in ALLOWED_ACTIONS:
            raise ValueError(f"Unsupported or unsafe action: {action}")

        if action in DESTRUCTIVE_ACTIONS:
            if intent.requires_confirmation is False:
                intent.requires_confirmation = True

        params = intent.parameters or {}
        if action == "email_send" and not params.get("recipient"):
            raise ValueError("email_send requires recipient")

        if action == "db_update":
            if not params.get("table") or not params.get("where"):
                raise ValueError("db_update requires table + where")

        if not intent.risk_level:
            intent.risk_level = "medium"

        return intent

    # ------------------------
    # Debug
    # ------------------------
    def parse_sync_for_debug(self, raw_command: str, *, domain: str = None, context: dict = None) -> Intent:
        payload = self._build_prompt(raw_command, domain, context)
        raw = self.llm_client(prompt=payload)
        intent = self.extract(raw)
        return self.validate(intent)
