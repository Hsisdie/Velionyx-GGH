"""Pass 2 — Verifier to cross-check extracted patient form against transcript."""

from __future__ import annotations

import json
import os
import re
from difflib import SequenceMatcher
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from core.schema import Item, PatientForm

load_dotenv()

_last_changes: list[str] = []


def get_last_verifier_changes() -> list[str]:
    """Return notes of what the verifier removed or downgraded in last run."""
    return list(_last_changes)


def _normalize(text: Optional[str]) -> str:
    """Strip punctuation and whitespace, lowercase (supports Devanagari)."""
    if not text:
        return ""
    return re.sub(r"[^\w\u0900-\u097F]", "", text.lower())


def _is_evidence_in_transcript(evidence: Optional[str], transcript: str, threshold: float = 0.8) -> bool:
    """Check if evidence appears in transcript with ~80% fuzzy match."""
    if not evidence or not transcript:
        return False
    ev, tr = _normalize(evidence), _normalize(transcript)
    if not ev or not tr:
        return False
    if ev in tr:
        return True
    l_ev = len(ev)
    if len(tr) < l_ev:
        return SequenceMatcher(None, ev, tr).ratio() >= threshold
    best = max(
        SequenceMatcher(None, ev, tr[i : i + l_ev]).ratio()
        for i in range(len(tr) - l_ev + 1)
    )
    return best >= threshold


def _verify_item(name: str, item: Item, transcript: str, missing_info: list[str]) -> Optional[str]:
    """Verify single Item; remove value if evidence is missing from transcript."""
    if item.value is None:
        return None
    if not _is_evidence_in_transcript(item.evidence, transcript):
        item.value = None
        item.confidence = "low"
        if name not in missing_info:
            missing_info.append(name)
        return f"Removed {name} (evidence not in transcript)"
    return None


def _check_gemini_unsupported(form: PatientForm) -> list[str]:
    """Gemini text-only check asking which fields are NOT supported."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return []
    client = genai.Client(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    prompt = (
        "You are a medical record auditor. Compare the transcript with the form data.\n"
        f"Transcript: {form.transcript}\n"
        f"Form: {form.model_dump_json(exclude={'transcript'})}\n\n"
        "Which fields are NOT supported by the transcript? Return ONLY a JSON list of field names."
    )
    response = client.models.generate_content(
        model=model_name,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[str],
            temperature=0.0,
        ),
    )
    return json.loads(response.text)


def verify_form(form: PatientForm, check_llm: bool = True) -> PatientForm:
    """Cross-check extracted form against transcript deterministically and via LLM."""
    global _last_changes
    _last_changes = []

    # 1. Deterministic verification
    single_fields = [
        ("name", form.name), ("age", form.age), ("gender", form.gender),
        ("village", form.village), ("duration", form.duration),
        ("temperature", form.temperature), ("pregnant", form.pregnant),
        ("pregnancy_details", form.pregnancy_details),
    ]
    for fname, item in single_fields:
        note = _verify_item(fname, item, form.transcript, form.missing_info)
        if note:
            _last_changes.append(note)

    for field_name, items in [("symptoms", form.symptoms), ("medicines_taken", form.medicines_taken)]:
        surviving = []
        for it in items:
            if it.value and not _is_evidence_in_transcript(it.evidence, form.transcript):
                it.value = None
                it.confidence = "low"
                _last_changes.append(f"Removed unsupported {field_name} entry")
            else:
                surviving.append(it)
        if not surviving and field_name not in form.missing_info:
            form.missing_info.append(field_name)

    # 2. Gemini text-only check (skip silently on failure or if disabled)
    if check_llm:
        try:
            unsupported = _check_gemini_unsupported(form)
            for fname in unsupported:
                attr = getattr(form, fname, None)
                if isinstance(attr, Item) and attr.confidence != "low":
                    attr.confidence = "low"
                    _last_changes.append(f"Downgraded {fname} to low confidence (Gemini check)")
        except Exception:
            pass

    return form
