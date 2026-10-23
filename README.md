# ASHA Scribe

> Voice-first AI documentation and clinical danger sign assistant for Accredited Social Health Activists (ASHA workers).

---

## The Problem and Who It Affects

Accredited Social Health Activists (ASHA workers) serve as the frontline of rural and community healthcare in India, conducting home visits, maternal care tracking, and child health monitoring. 

ASHA workers face significant operational burdens:
- **Paperwork Overload:** Workers spend hours manually filling registers and reporting forms after home visits.
- **Documentation Errors:** Vital patient details, symptom durations, and warning signs can be missed or recorded inconsistently.
- **Time Away from Patients:** Extensive manual paperwork reduces the time community health workers can spend counseling and caring for patients.

---

## Our Solution and How Gemini Is Used

ASHA Scribe provides an AI-powered voice assistant that turns spoken patient conversations in Hindi and regional dialects into structured, verified digital records.

### How Google Gemini Is Used
- **Multimodal Audio Understanding:** Directly processes voice recordings via the Gemini API using Pydantic structured schemas to extract key fields (patient name, age, village, symptoms, duration, medicines, and pregnancy status).
- **Two-Stage Hallucination Verifier:** Extracted data undergoes a deterministic fuzzy-matching check against the audio transcript, followed by a Gemini text-verification call to confirm evidence grounding and downgrade unsupported fields.
- **Rule-Based Danger Sign Detection:** Cross-checks extracted symptoms against clinical danger sign rules to trigger instant high/medium risk alerts.
- **Bilingual Actionable Summaries:** Generates Devanagari Hindi patient summaries and pre-formatted WhatsApp referral messages for urgent medical attention.

---

## Tech Stack

- **Python** — Core language
- **Streamlit** — Web application interface
- **Google Gemini API** (`google-genai` SDK) — Multimodal audio understanding and structured extraction
- **Pydantic** — Schema definition and data validation
- **python-dotenv** — Environment configuration management
- **pytest** — Unit and regression test suite

---

## Setup and Run Steps

Clone the repository:
```bash
git clone https://github.com/Hsisidie/Velionyx-GGH.git
cd Velionyx-GGH
```

Create and activate a virtual environment:
```bash
python -m venv .venv
```
- Windows: `.venv\Scripts\activate`
- Linux/macOS: `source .venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

Set up your Gemini API key in `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Run the application:
```bash
streamlit run app.py
```

---

## Team Members and Roles

- **Harish Choudhary**: Lead Developer
- **Vikash Kaushal**: Research and Presentation
- **Akshay Singh**: Testing and Demo

---

## Before vs Built on the Day

Before vs built on the day: nothing existed before 23 Oct 2026.

All application code, Pydantic schemas, danger sign safety logic, deterministic verifier, evaluation suite, offline demo caching, and Streamlit interface were designed and developed from scratch on 23 Oct 2026 for the Google Gemini Hackathon.

---

## Credits

- **Google Gemini API**
- **Google Antigravity**
- **Streamlit**
- **Pydantic**
- **python-dotenv**

---

## Limits and Safety

- **No diagnosis:** ASHA Scribe is strictly a documentation aid and referral alert assistant. It does not provide medical diagnoses, clinical determinations, or prescriptions.
- **Worker confirms:** Every extracted field must be reviewed, verified, and confirmed by the human health worker before any record is saved.
- **Scripted test data only:** All evaluation cases, audio files, and test scenarios use scripted team test data. No real patient data or patient audio is collected, processed, or stored.

---

## Evaluation Results

Real evaluation numbers copied directly from `eval/results.json`:

| Metric | Value |
|---|---|
| Field Accuracy | 0.0% |
| Hallucination Count | 1 |
| Danger Recall | 0.0% |
| False Alarms | 0 |

### Case Breakdown (eval/results.json)
- `t1_fever`: Status FAIL, Risk low (Tested against scripted audio)
- `t2_pregnant_danger` to `t7_hinglish`: Status MISSING (Audio file not found in test environment)
