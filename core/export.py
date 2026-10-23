"""Export referral messages and summaries for ASHA workers."""

from __future__ import annotations

import urllib.parse

from core.safety import SafetyResult
from core.schema import PatientForm


def referral_message_hi(form: PatientForm, safety: SafetyResult) -> str:
    """Generate a short Hindi referral note for doctors or hospital referral.

    Includes name, age, village, symptoms, duration, risk level, and a see-a-doctor
    instruction ONLY if risk is medium or high.
    Never includes disease diagnoses or medicine suggestions.
    """
    name = form.name.value or "अज्ञात"
    age = f"{form.age.value} वर्ष" if form.age.value else "अज्ञात"
    village = form.village.value or "अज्ञात"

    sym_list = [s.value for s in form.symptoms if s.value]
    symptoms = ", ".join(sym_list) if sym_list else "कोई विशेष लक्षण नहीं"
    duration = form.duration.value or "अज्ञात"

    risk_map = {
        "high": "उच्च जोखिम (High Risk)",
        "medium": "मध्यम जोखिम (Medium Risk)",
        "low": "कम जोखिम (Low Risk)",
    }
    risk_label = risk_map.get(safety.risk, "अज्ञात")

    lines = [
        "आशा मरीज रेफरल विवरण:",
        f"• नाम: {name}",
        f"• उम्र: {age}",
        f"• गाँव: {village}",
        f"• लक्षण: {symptoms}",
        f"• अवधि: {duration}",
        f"• जोखिम स्तर: {risk_label}",
    ]

    # Sentence meaning "Please show a doctor" ONLY if risk is medium or high
    if safety.risk in ("medium", "high"):
        lines.append("कृपया मरीज को तुरंत डॉक्टर को दिखाएं।")

    return "\n".join(lines)


def get_whatsapp_url(message: str) -> str:
    """Generate a WhatsApp click-to-chat URL with the message URL-encoded."""
    return f"https://wa.me/?text={urllib.parse.quote(message)}"
