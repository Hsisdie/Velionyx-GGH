"""Rule-based clinical danger signs evaluation.

DEMO RULES ONLY — based on commonly taught community health danger signs.
Must be reviewed by a qualified doctor or mentor before any real clinical use.
"""

from __future__ import annotations

import re
from typing import Literal, Optional
from pydantic import BaseModel
from core.schema import Item, PatientForm


class SafetyFlag(BaseModel):
    """A flagged danger sign with bilingual reasons and evidence."""
    rule_id: str
    reason_en: str
    reason_hi: str
    evidence: Optional[str] = None


class SafetyResult(BaseModel):
    """Aggregated safety evaluation result."""
    risk: Literal["low", "medium", "high"]
    flags: list[SafetyFlag]


# Rules defined as DATA (a list of dicts, not scattered if statements)
RULES = [
    {
        "rule_id": "R1", "level": "high", "condition_type": "pregnant",
        "keywords": [
            "severe headache", "तेज़ सिरदर्द", "tez sirdard", "sir dard", "sar dard",
            "blurred vision", "धुंधला", "dhundhla", "swelling", "सूजन", "sujan",
            "bleeding", "खून", "khoon", "raktsrav", "fits", "convulsions", "दौरा", "daura",
            "jhatke", "झटके", "baby moving less", "हलचल कम", "halchal kam", "high fever", "तेज़ बुखार",
        ],
        "reason_en": "Pregnancy danger sign detected. See a doctor immediately.",
        "reason_hi": "गर्भावस्था में खतरे का संकेत। तुरंत डॉक्टर को दिखाएं।",
    },
    {
        "rule_id": "R2", "level": "high", "condition_type": "under_5",
        "keywords": [
            "fast breathing", "difficult breathing", "difficulty breathing", "तेज़ सांस", "साँस लेने में",
            "not feeding", "not drinking", "दूध नहीं", "khana nahi", "pani nahi", "fits", "convulsions",
            "दौरा", "daura", "jhatke", "झटके", "sleepy", "unresponsive", "सुस्त", "behosh", "sust",
            "बेहोश", "repeated vomiting", "बार-बार उल्टी", "vomiting", "उल्टी",
        ],
        "reason_en": "Child danger sign detected. See a doctor immediately.",
        "reason_hi": "बच्चे में खतरे का संकेत। तुरंत डॉक्टर को दिखाएं।",
    },
    {
        "rule_id": "R3", "level": "high", "condition_type": "anyone",
        "keywords": [
            "unconscious", "बेहोश", "behosh", "murchhit", "fits", "convulsions", "दौरा", "daura",
            "chest pain", "सीने में दर्द", "seene mein dard", "heavy bleeding", "bleeding", "ज़्यादा खून",
            "difficulty breathing", "shortness of breath", "साँस लेने में", "saans lene", "dum ghutna",
        ],
        "reason_en": "Emergency danger sign detected. See a doctor immediately.",
        "reason_hi": "गंभीर खतरे का संकेत। तुरंत डॉक्टर को दिखाएं।",
    },
    {
        "rule_id": "R4", "level": "medium", "condition_type": "fever_3days",
        "keywords": [],
        "reason_en": "Fever for 3 or more days. See a doctor.",
        "reason_hi": "3 या अधिक दिनों से बुखार। डॉक्टर को दिखाएं।",
    },
]


def _is_pregnant(item: Optional[Item]) -> bool:
    return bool(item and item.value and item.value.strip().lower() in {"yes", "ha", "haan", "हाँ", "हा", "true", "pregnant"})


def _is_under_5(age_str: Optional[str]) -> bool:
    if not age_str:
        return False
    t = age_str.lower()
    m_mo = re.search(r"(\d+)\s*(?:month|mo|mahine|mahina|महीने|महीना)", t)
    if m_mo:
        return (int(m_mo.group(1)) / 12.0) < 5.0
    m_yr = re.search(r"\b(\d+)\b", t)
    return int(m_yr.group(1)) < 5 if m_yr else False


def _check_fever_3_days(form: PatientForm, search_text: str) -> Optional[str]:
    if not any(w in search_text for w in ["fever", "बुखार", "bukhar", "तापमान", "temperature"]):
        return None
    dur_text = f"{form.duration.value or ''} {form.duration.evidence or ''} {search_text}".lower()
    for pat in [r"\b([3-9]|\d{2,})\s*(?:day|days|din|दिन)", r"\b(?:week|weeks|हफ्ता|hafta)\b"]:
        m = re.search(pat, dur_text)
        if m:
            return m.group(0)
    return None


def _find_keyword(text: str, keywords: list[str]) -> Optional[str]:
    return next((kw for kw in keywords if kw.lower() in text), None)


def check_danger(form: PatientForm) -> SafetyResult:
    """Evaluate rule-based danger signs on a patient form."""
    parts = [
        form.transcript or "", *(s.value or "" for s in form.symptoms),
        *(s.evidence or "" for s in form.symptoms), form.duration.value or "",
        form.duration.evidence or "", form.pregnancy_details.value or "",
        form.pregnancy_details.evidence or "",
    ]
    search_text = " ".join(parts).lower()
    flags: list[SafetyFlag] = []

    for rule in RULES:
        cond, m_kw = rule["condition_type"], None
        if cond == "pregnant" and _is_pregnant(form.pregnant):
            m_kw = _find_keyword(search_text, rule["keywords"])
        elif cond == "under_5" and _is_under_5(form.age.value):
            m_kw = _find_keyword(search_text, rule["keywords"])
        elif cond == "anyone":
            m_kw = _find_keyword(search_text, rule["keywords"])
        elif cond == "fever_3days":
            m_kw = _check_fever_3_days(form, search_text)

        if m_kw:
            flags.append(SafetyFlag(
                rule_id=rule["rule_id"], reason_en=rule["reason_en"],
                reason_hi=rule["reason_hi"], evidence=m_kw,
            ))

    for item in form.danger_signs_llm:
        if item.value:
            flags.append(SafetyFlag(
                rule_id="LLM", reason_en=f"AI noted danger sign: {item.value}. See a doctor.",
                reason_hi=f"खतरे का संकेत: {item.evidence or item.value}। डॉक्टर को दिखाएं।",
                evidence=item.evidence or item.value,
            ))

    rule_levels = {r["rule_id"]: r["level"] for r in RULES}
    risk: Literal["low", "medium", "high"] = "low"
    for f in flags:
        lvl = rule_levels.get(f.rule_id, "medium")
        if lvl == "high":
            risk = "high"
            break
        if lvl == "medium" and risk != "high":
            risk = "medium"

    return SafetyResult(risk=risk, flags=flags)
