"""Pydantic v2 models for the ASHA Scribe patient form."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

# Confidence level assigned to each extracted field.
Confidence = Literal["high", "medium", "low"]


class Item(BaseModel):
    """A single extracted field with evidence and confidence."""

    value: Optional[str]
    # The exact words said in the original language.
    evidence: Optional[str]
    confidence: Confidence


class PatientForm(BaseModel):
    """Structured patient form extracted from an audio conversation."""

    transcript: str

    # Demographics
    name: Item
    age: Item
    gender: Item
    village: Item

    # Clinical
    symptoms: list[Item]
    duration: Item
    temperature: Item
    medicines_taken: list[Item]

    # Pregnancy — value is "yes", "no", or null
    pregnant: Item
    pregnancy_details: Item

    # Safety
    danger_signs_llm: list[Item]

    # Gaps and follow-up
    missing_info: list[str]
    follow_up_questions_hi: list[str]

    # Hindi summary (2 simple sentences)
    summary_hi: str
