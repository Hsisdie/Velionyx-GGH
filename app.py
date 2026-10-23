"""ASHA Scribe — Streamlit UI for clinical audio note-taking."""

import os
import time
import streamlit as st
from dotenv import load_dotenv

from core.extractor import extract_form
from core.schema import Item, PatientForm

load_dotenv()

# 1. Header
st.title("ASHA Scribe")
st.caption("Notes only. No diagnosis. Worker confirms every entry.")

# 2. Consent checkbox (gates recording and processing)
consent = st.checkbox("Patient has agreed to this record")

# 3. Audio input & uploader (disabled until consent is given)
col1, col2 = st.columns(2)
with col1:
    recorded_audio = st.audio_input("Record audio", disabled=not consent)
with col2:
    uploaded_audio = st.file_uploader(
        "Upload audio",
        type=["mp3", "wav", "m4a", "ogg"],
        disabled=not consent,
    )

audio_file = recorded_audio or uploaded_audio


def _get_mime_type(file) -> str:
    """Detect MIME type from file or fallback by extension."""
    mime = getattr(file, "type", None) or ""
    if mime == "audio/mpeg":
        return "audio/mp3"
    if not mime or mime == "application/octet-stream":
        name = getattr(file, "name", "").lower()
        ext_map = {
            ".mp3": "audio/mp3",
            ".wav": "audio/wav",
            ".m4a": "audio/mp4",
            ".ogg": "audio/ogg",
        }
        for ext, mapped in ext_map.items():
            if name.endswith(ext):
                return mapped
        return "audio/wav"
    return mime


# Extraction trigger button
if st.button("Fill the form", disabled=not consent):
    if not audio_file:
        st.warning("Please record or upload an audio file first.")
    else:
        start_time = time.time()
        try:
            with st.spinner("Extracting patient details..."):
                audio_file.seek(0)
                data = audio_file.read()
                mime = _get_mime_type(audio_file)
                form = extract_form(data, mime)

                # Reset widget keys so new values show up
                widget_keys = [
                    "f_name", "f_age", "f_gender", "f_village",
                    "f_symptoms", "f_duration", "f_temp", "f_meds",
                    "f_pregnant", "f_preg_details",
                ]
                for k in widget_keys:
                    st.session_state.pop(k, None)

                st.session_state["form"] = form
                st.session_state["elapsed"] = time.time() - start_time
        except Exception as e:
            st.error(f"Error during extraction: {e}")

# 4 & 5. Display extracted form and processing time
if "form" in st.session_state:
    form: PatientForm = st.session_state["form"]
    elapsed = st.session_state.get("elapsed", 0.0)

    # 5. Show processing time
    st.info(f"Processing time: {elapsed:.2f} seconds")

    # Transcript expander
    with st.expander("Transcript", expanded=False):
        st.write(form.transcript)

    # Confidence dots
    dots = {"high": "🟢", "medium": "🟡", "low": "🔴"}

    def render_field(label_hi: str, label_en: str, item: Item, key: str):
        dot = dots.get(item.confidence, "🔴")
        val = item.value or ""
        st.text_input(f"{dot} {label_hi} ({label_en})", value=val, key=key)
        with st.expander("What was heard"):
            st.write(item.evidence or "None")

    # Editable inputs for all 10 fields with Hindi (English) labels & confidence dots
    render_field("नाम", "Name", form.name, "f_name")
    render_field("उम्र", "Age", form.age, "f_age")
    render_field("लिंग", "Gender", form.gender, "f_gender")
    render_field("गाँव", "Village", form.village, "f_village")

    # Symptoms list
    sym_val = ", ".join(i.value for i in form.symptoms if i.value)
    sym_ev = ", ".join(i.evidence for i in form.symptoms if i.evidence)
    sym_conf = (
        "high" if any(i.confidence == "high" for i in form.symptoms)
        else ("medium" if any(i.confidence == "medium" for i in form.symptoms) else "low")
    )
    render_field("लक्षण", "Symptoms", Item(value=sym_val or None, evidence=sym_ev or None, confidence=sym_conf), "f_symptoms")

    render_field("अवधि", "Duration", form.duration, "f_duration")
    render_field("तापमान", "Temperature", form.temperature, "f_temp")

    # Medicines list
    med_val = ", ".join(i.value for i in form.medicines_taken if i.value)
    med_ev = ", ".join(i.evidence for i in form.medicines_taken if i.evidence)
    med_conf = (
        "high" if any(i.confidence == "high" for i in form.medicines_taken)
        else ("medium" if any(i.confidence == "medium" for i in form.medicines_taken) else "low")
    )
    render_field("दवाइयाँ", "Medicines", Item(value=med_val or None, evidence=med_ev or None, confidence=med_conf), "f_meds")

    render_field("गर्भवती", "Pregnant", form.pregnant, "f_pregnant")
    render_field("गर्भावस्था विवरण", "Pregnancy Details", form.pregnancy_details, "f_preg_details")
