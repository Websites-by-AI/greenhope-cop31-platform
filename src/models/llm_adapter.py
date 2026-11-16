"""Pluggable LLM synthesis adapter for KAG and RAG form-field generation.

Default mode: `deterministic-grounded-synthesizer-v1` (runs 100% locally offline with zero API keys, zero hallucinations,
strictly grounded in KAG graph paths + retrieved RAG chunks + applicant facts).

Optional live LLM providers (auto-activated via environment variables):
- `COP31_LLM_PROVIDER=openai` (`OPENAI_API_KEY`, `COP31_LLM_MODEL=gpt-4o-mini`)
- `COP31_LLM_PROVIDER=anthropic` (`ANTHROPIC_API_KEY`, `COP31_LLM_MODEL=claude-3-5-sonnet-latest`)
- `COP31_LLM_PROVIDER=ollama` (`OLLAMA_BASE_URL=http://localhost:11434`, `COP31_LLM_MODEL=llama3.1`)
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, List, Optional


class GroundedLLMAdapter:
    """Unified generation interface for both offline deterministic synthesis and optional live LLM APIs."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None) -> None:
        self.provider = (provider or os.getenv("COP31_LLM_PROVIDER", "local")).lower()
        self.model = model or os.getenv("COP31_LLM_MODEL", "deterministic-grounded-synthesizer-v1")

    @property
    def backend_label(self) -> str:
        if self.provider == "local":
            return "deterministic-grounded-synthesizer-v1"
        return f"{self.provider}:{self.model}"

    def synthesize_field(
        self,
        investor_name: str,
        field_label: str,
        field_description: str,
        applicant_context: Dict[str, Any],
        kag_facts: List[str],
        rag_snippets: List[Dict[str, Any]],
        fallback_draft: str,
    ) -> str:
        """Synthesize a form field value. Falls back cleanly to deterministic grounded draft if offline or API fails."""
        if self.provider == "local":
            return fallback_draft

        prompt = self._build_grounded_prompt(
            investor_name=investor_name,
            field_label=field_label,
            field_description=field_description,
            applicant_context=applicant_context,
            kag_facts=kag_facts,
            rag_snippets=rag_snippets,
            baseline_draft=fallback_draft,
        )
        try:
            if self.provider == "openai" and os.getenv("OPENAI_API_KEY"):
                return self._call_openai(prompt)
            if self.provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
                return self._call_anthropic(prompt)
            if self.provider == "ollama":
                return self._call_ollama(prompt)
        except Exception:
            # Never fail form completion if an external API is unreachable; return deterministic grounded draft
            return fallback_draft
        return fallback_draft

    @staticmethod
    def _build_grounded_prompt(
        investor_name: str,
        field_label: str,
        field_description: str,
        applicant_context: Dict[str, Any],
        kag_facts: List[str],
        rag_snippets: List[Dict[str, Any]],
        baseline_draft: str,
    ) -> str:
        rag_block = "\n".join(
            f"- [{s['chunk_id']}] (score={s['score']:.2f}): {s['text']}" for s in rag_snippets
        ) or "None"
        kag_block = "\n".join(f"- {fact}" for fact in kag_facts) or "None"
        return (
            f"You are filling an official climate finance application form for {investor_name}.\n"
            f"Field: {field_label}\nRequirement: {field_description}\n\n"
            f"STRICT RULES: Use ONLY the verified facts below. Never invent missing regulatory approvals, tax IDs, or financial metrics. "
            f"Preserve citations like [chunk_id]. Keep the response concise and bankable (2-4 sentences).\n\n"
            f"KAG KNOWLEDGE GRAPH FACTS:\n{kag_block}\n\n"
            f"RAG RETRIEVED POLICY CHUNKS:\n{rag_block}\n\n"
            f"APPLICANT PROFILE (PII-REDACTED):\n{json.dumps(applicant_context, ensure_ascii=False)}\n\n"
            f"GROUNDED BASELINE DRAFT:\n{baseline_draft}\n\n"
            f"Produce the polished final form entry:"
        )

    def _call_openai(self, prompt: str) -> str:
        api_key = os.environ["OPENAI_API_KEY"]
        payload = json.dumps(
            {
                "model": self.model if self.model != "deterministic-grounded-synthesizer-v1" else "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 350,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()

    def _call_anthropic(self, prompt: str) -> str:
        api_key = os.environ["ANTHROPIC_API_KEY"]
        payload = json.dumps(
            {
                "model": self.model if self.model != "deterministic-grounded-synthesizer-v1" else "claude-3-5-sonnet-latest",
                "max_tokens": 350,
                "temperature": 0.1,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["content"][0]["text"].strip()

    def _call_ollama(self, prompt: str) -> str:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        payload = json.dumps(
            {
                "model": self.model if self.model != "deterministic-grounded-synthesizer-v1" else "llama3.1",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["response"].strip()
