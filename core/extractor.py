"""Pass 1 — Send audio to Gemini and get a structured PatientForm back."""

from __future__ import annotations

import json
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from core.schema import PatientForm

load_dotenv()

# System prompt instructs Gemini to act as a medical scribe — never diagnose.
_SYSTEM_PROMPT = """\
You are a scribe for an Indian village health worker (ASHA).
The audio is a conversation in Hindi, Hinglish or a local dialect.

Step 1 — Write a faithful transcript in the original language.
Step 2 — Fill every field of the JSON schema using ONLY facts actually said.
         Unknown = null. Write field values in English (transliterate names),
         but copy the evidence as the exact original words.
         For each field set:
           • value  — the extracted answer (in English)
           • evidence — the EXACT words from the transcript (original language)
           • confidence — "high" if clearly stated, "medium" if implied,
             "low" if uncertain. Set confidence honestly.
         If a field was NOT mentioned at all, leave value and evidence as null.
Step 3 — List important missing fields in missing_info \
(e.g. "age", "temperature").
Step 4 — Write 2-3 simple Hindi follow-up questions the worker can ask \
to fill the gaps, in follow_up_questions_hi.
Step 5 — Write a 2-sentence Hindi summary in summary_hi.

RULES:
• NEVER diagnose or suggest medicines. You are only a scribe.
• NEVER guess — only record what was actually said.
• For the pregnant field, value must be "yes", "no", or null.
• Keep evidence in the original language (Hindi / dialect).
"""

# Map file extensions to MIME types for the CLI.
_EXT_TO_MIME: dict[str, str] = {
    ".wav": "audio/wav",
    ".mp3": "audio/mp3",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
}

_MAX_RETRIES = 1  # Retry once on failure.


def extract_form(audio_bytes: bytes, mime_type: str) -> PatientForm:
    """Send audio to Gemini and return a structured PatientForm.

    Retries once on failure, then raises a clear error.

    Args:
        audio_bytes: Raw audio file bytes.
        mime_type: MIME type of the audio (e.g. "audio/wav").

    Returns:
        A validated PatientForm parsed from the model's JSON response.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")

    model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    client = genai.Client(api_key=api_key)

    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
    config = types.GenerateContentConfig(
        system_instruction=_SYSTEM_PROMPT,
        response_mime_type="application/json",
        response_schema=PatientForm,
        temperature=0.1,
    )

    last_error: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[audio_part, "Extract the patient form from this audio."],
                config=config,
            )
            return PatientForm.model_validate_json(response.text)
        except Exception as exc:
            last_error = exc
            if attempt < _MAX_RETRIES:
                continue  # retry once

    raise RuntimeError(
        f"Gemini extraction failed after {_MAX_RETRIES + 1} attempts: {last_error}"
    ) from last_error


def _guess_mime(path: str) -> str:
    """Guess MIME type from file extension."""
    ext = os.path.splitext(path)[1].lower()
    mime = _EXT_TO_MIME.get(ext)
    if not mime:
        raise ValueError(
            f"Unknown audio extension '{ext}'. "
            f"Supported: {', '.join(_EXT_TO_MIME)}"
        )
    return mime


# --- CLI entry-point: python -m core.extractor path/to/audio ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m core.extractor <path/to/audio>")
        sys.exit(1)

    audio_path = sys.argv[1]
    try:
        mime = _guess_mime(audio_path)
        with open(audio_path, "rb") as f:
            data = f.read()
        form = extract_form(data, mime)
        # Pretty-print the JSON output.
        print(json.dumps(form.model_dump(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
