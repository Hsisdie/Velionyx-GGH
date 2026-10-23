"""ASHA Scribe — Streamlit UI for clinical audio note-taking."""

import json, os, time, streamlit as st
from dotenv import load_dotenv

from core.export import get_whatsapp_url, referral_message_hi
from core.extractor import extract_form
from core.safety import check_danger
from core.schema import Item, PatientForm
from core.store import delete_all, load_all, save_confirmed
from core.verifier import get_last_verifier_changes, verify_form

load_dotenv()
st.set_page_config(page_title="ASHA Scribe", layout="wide")
st.title("ASHA Scribe")
st.caption("Notes only. No diagnosis. Worker confirms every entry.")

worker_name = st.sidebar.text_input("Worker name", value="ASHA Worker")
lang = st.sidebar.radio("Label language / भाषा", ["Hindi", "English"], horizontal=True)


def _get_mime(f) -> str:
    m = getattr(f, "type", None) or ""
    if m == "audio/mpeg": return "audio/mp3"
    ext = os.path.splitext(getattr(f, "name", f) if isinstance(f, str) else getattr(f, "name", ""))[1].lower()
    return {".mp3": "audio/mp3", ".wav": "audio/wav", ".m4a": "audio/mp4", ".ogg": "audio/ogg"}.get(ext, "audio/wav")


def _process_audio(data: bytes, mime: str, filename: str):
    c_dir, t0 = os.path.join("data", "cache"), time.time()
    os.makedirs(c_dir, exist_ok=True)
    c_path = os.path.join(c_dir, f"{filename}.json")
    try:
        form = verify_form(extract_form(data, mime))
        with open(c_path, "w", encoding="utf-8") as f: f.write(form.model_dump_json())
        st.session_state["is_cached"] = False
    except Exception as e:
        if os.path.exists(c_path):
            with open(c_path, "r", encoding="utf-8") as f: form = PatientForm.model_validate_json(f.read())
            st.session_state["is_cached"] = True
        else: raise e
    st.session_state["verifier_notes"] = get_last_verifier_changes()
    for k in [k for k in st.session_state.keys() if k.startswith("f_")]: del st.session_state[k]
    st.session_state["form"], st.session_state["elapsed"] = form, time.time() - t0


st.sidebar.subheader("Demo mode / डेमो मोड")
s_files = [f for f in os.listdir("samples") if f.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".mp4"))] if os.path.exists("samples") else []
for s in s_files:
    if st.sidebar.button(f"Load sample: {s}", use_container_width=True):
        with open(os.path.join("samples", s), "rb") as af: _process_audio(af.read(), _get_mime(s), s)

tab_rec, tab_hist, tab_eval = st.tabs(["Record", "History", "Evaluation"])

with tab_rec:
    consent = st.checkbox("Patient has agreed to this record")
    c1, c2 = st.columns(2)
    with c1: rec = st.audio_input("Record audio", disabled=not consent)
    with c2: up = st.file_uploader("Upload audio", type=["mp3", "wav", "m4a", "ogg"], disabled=not consent)
    audio_file = rec or up

    if st.button("Fill the form", disabled=not consent, use_container_width=True):
        if not audio_file: st.warning("Please record or upload an audio file first.")
        else:
            try:
                with st.spinner("Processing audio..."):
                    audio_file.seek(0)
                    _process_audio(audio_file.read(), _get_mime(audio_file), getattr(audio_file, "name", "uploaded_audio"))
            except Exception as e: st.error(f"Error during extraction: {e}")

    if "form" in st.session_state:
        form: PatientForm = st.session_state["form"]
        if st.session_state.get("is_cached"): st.warning("Offline demo (cached)")
        st.info(f"Processing time: {st.session_state.get('elapsed', 0.0):.2f} seconds")
        if st.session_state.get("verifier_notes"): st.info("🔍 " + "; ".join(st.session_state["verifier_notes"]))

        safety = check_danger(form)
        reasons = "\n".join(f"• {f.reason_hi} ({f.reason_en})" for f in safety.flags)
        if safety.risk == "high":
            st.badge("उच्च जोखिम (High Risk)", color="red", icon="🚨"); st.error(f"### 🚨 डॉक्टर को दिखाओ\n\n{reasons}")
        elif safety.risk == "medium":
            st.badge("मध्यम जोखिम (Medium Risk)", color="orange", icon="⚠️"); st.warning(f"### ⚠️ डॉक्टर को दिखाओ\n\n{reasons}")
        else: st.badge("कम जोखिम (Low Risk)", color="green", icon="✅")

        with st.expander("Transcript", expanded=False): st.write(form.transcript)

        dots = {"high": "🟢", "medium": "🟡", "low": "🔴"}
        def render_f(lbl: str, item: Item, key: str):
            st.text_input(f"{dots.get(item.confidence, '🔴')} {lbl}", value=item.value or "", key=key)
            with st.expander("What was heard"): st.write(item.evidence or "None")

        lbls = {
            "name": "नाम" if lang == "Hindi" else "Name", "age": "उम्र" if lang == "Hindi" else "Age",
            "gender": "लिंग" if lang == "Hindi" else "Gender", "village": "गाँव" if lang == "Hindi" else "Village",
            "dur": "अवधि" if lang == "Hindi" else "Duration", "temp": "तापमान" if lang == "Hindi" else "Temperature",
            "preg": "गर्भवती" if lang == "Hindi" else "Pregnant", "preg_d": "गर्भावस्था विवरण" if lang == "Hindi" else "Pregnancy Details",
            "sym": "लक्षण" if lang == "Hindi" else "Symptoms", "med": "दवाइयाँ" if lang == "Hindi" else "Medicines",
        }
        for k_id, it, f_id in [("name", form.name, "f_name"), ("age", form.age, "f_age"), ("gender", form.gender, "f_gender"), ("village", form.village, "f_village"), ("dur", form.duration, "f_dur"), ("temp", form.temperature, "f_temp"), ("preg", form.pregnant, "f_preg"), ("preg_d", form.pregnancy_details, "f_preg_d")]:
            render_f(lbls[k_id], it, f_id)

        s_val = ", ".join(i.value for i in form.symptoms if i.value)
        s_conf = "high" if any(i.confidence == "high" for i in form.symptoms) else ("medium" if any(i.confidence == "medium" for i in form.symptoms) else "low")
        render_f(lbls["sym"], Item(value=s_val or None, evidence=", ".join(i.evidence for i in form.symptoms if i.evidence) or None, confidence=s_conf), "f_sym")

        m_val = ", ".join(i.value for i in form.medicines_taken if i.value)
        m_conf = "high" if any(i.confidence == "high" for i in form.medicines_taken) else ("medium" if any(i.confidence == "medium" for i in form.medicines_taken) else "low")
        render_f(lbls["med"], Item(value=m_val or None, evidence=", ".join(i.evidence for i in form.medicines_taken if i.evidence) or None, confidence=m_conf), "f_med")

        if form.summary_hi: st.markdown("### 📝 संक्षिप्त विवरण (Summary)"); st.info(form.summary_hi)
        if form.follow_up_questions_hi:
            with st.container(border=True):
                st.markdown("### ❓ आगे क्या पूछें (Ask next)")
                for q in form.follow_up_questions_hi: st.markdown(f"- {q}")

        ref_msg = referral_message_hi(form, safety)
        st.markdown("### 📋 रेफरल संदेश (Referral Note)")
        st.text_area("रेफरल संदेश", value=ref_msg, height=180, key="ta_referral")
        st.link_button("📲 WhatsApp पर भेजें (Share on WhatsApp)", url=get_whatsapp_url(ref_msg), use_container_width=True)

        if st.button("Confirm and save / पुष्टि करें और सुरक्षित करें", use_container_width=True):
            save_confirmed(form.model_dump(), worker_name); st.success("Record saved successfully! / रिकॉर्ड सुरक्षित कर दिया गया!")

with tab_hist:
    st.subheader("📜 Saved Patient Records")
    records = load_all()
    if not records: st.info("No records saved yet.")
    else:
        st.dataframe([{"Time (UTC)": r.get("timestamp_utc", "")[:19], "Worker": r.get("worker_name", ""), "Name": r.get("name", {}).get("value") if isinstance(r.get("name"), dict) else r.get("name") or "-", "Age": r.get("age", {}).get("value") if isinstance(r.get("age"), dict) else r.get("age") or "-", "Village": r.get("village", {}).get("value") if isinstance(r.get("village"), dict) else r.get("village") or "-", "Symptoms": ", ".join(s.get("value", "") for s in r.get("symptoms", []) if isinstance(s, dict) and s.get("value")) or "-"} for r in records], use_container_width=True)
    st.divider()
    confirm_del = st.checkbox("I confirm I want to delete all saved data")
    if st.button("Delete all data", disabled=not confirm_del, use_container_width=True):
        delete_all(); st.success("All data deleted."); st.rerun()

with tab_eval:
    st.subheader("📊 System Evaluation")
    res_path = os.path.join("eval", "results.json")
    if not os.path.exists(res_path): st.warning("Run eval first")
    else:
        with open(res_path, "r", encoding="utf-8") as f: res_data = json.load(f)
        m = res_data.get("metrics", {})
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Field Accuracy", f"{m.get('field_accuracy', 0):.1%}")
        mc2.metric("Hallucinations", m.get("hallucination_count", 0))
        mc3.metric("Danger Recall", f"{m.get('danger_recall', 0):.1%}")
        mc4.metric("False Alarms", m.get("false_alarms", 0))
        st.dataframe(res_data.get("cases_table", []), use_container_width=True)

st.divider()
st.caption("Notes only. No diagnosis. Worker confirms every entry.")
