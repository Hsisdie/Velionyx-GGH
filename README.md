# ASHA Scribe
### Voice-Powered Health Documentation for Community Health Workers

*Team Velionyx · Google Gemini Hackathon · 23 October 2026*

ASHA Scribe is an AI-assisted documentation tool designed to help community health workers convert spoken patient information into structured, reviewable health records. It aims to reduce repetitive paperwork while keeping the health worker in control of every record.

> *Safety first:* ASHA Scribe is a documentation assistant, not a diagnostic system. All extracted information must be reviewed and confirmed by the health worker.

---

## The Problem

Accredited Social Health Activists (ASHAs) play an important role in connecting communities with healthcare services. Recording patient information accurately can require significant time and repetitive paperwork.

When documentation is delayed or difficult, important details may be omitted, recorded incorrectly, or require additional follow-up.

## Our Solution

ASHA Scribe explores a voice-first workflow that turns a patient conversation into a structured health record for human review.

### How It Works

1. *Capture:* The health worker provides a patient conversation recording or supported audio input.
2. *Extract:* Gemini processes the supported input to identify relevant information, such as name, age, symptoms and medicines.
3. *Review:* The application presents extracted information in a structured, editable form.
4. *Identify gaps:* Missing or uncertain fields are highlighted when supported by the implemented workflow.
5. *Confirm:* The health worker reviews and confirms the information before using the record.

The goal is to make documentation easier without replacing professional judgement or clinical care.

## Key Features

Features should be considered available only when they are implemented and verified in the current build.

- *Voice-first documentation:* Convert supported audio input into structured patient information.
- *Structured extraction:* Organize relevant details into identifiable fields.
- *Editable records:* Allow human review and correction of extracted information.
- *Missing-field awareness:* Identify information that needs further confirmation, if supported by the current build.
- *Safety-oriented workflow:* Keep human review central and avoid presenting AI output as a diagnosis.
- *Evaluation suite:* Assess extraction quality and safety-related behaviour using scripted test cases.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web application interface |
| Google Gemini API | AI-assisted information extraction |
| Pydantic | Structured data validation |
| python-dotenv | Local environment configuration |

The technologies listed above reflect the project's documented dependencies. Exact model names and implemented capabilities should be verified against the current source code.

## Getting Started

### Prerequisites

- Python installed on your system
- Git
- A Google Gemini API key
- Internet access for API-based functionality

### 1. Clone the Repository

bash
git clone https://github.com/Hsisidie/Velionyx-GGH.git
cd Velionyx-GGH


### 2. Create a Virtual Environment

*Windows:*

bash
python -m venv .venv
.venv\Scripts\activate


*Linux / macOS:*

bash
python3 -m venv .venv
source .venv/bin/activate


### 3. Install Dependencies

bash
pip install -r requirements.txt


Ensure requirements.txt exists in the repository before running this command.

### 4. Configure the API Key

Create a .env file in the project root:

env
GEMINI_API_KEY=your_gemini_api_key_here


Replace the placeholder with your own API key. Never commit .env or expose API keys in source code, screenshots, logs or public repositories.

### 5. Run the Application

bash
streamlit run app.py


Open the local URL displayed in the terminal. This command assumes app.py is the application's entry point.

## Evaluation

The repository's reported eval/results.json values indicate that the current evaluation is *not yet passing*.

| Metric | Reported result |
|---|---:|
| Field Accuracy | 0.0% |
| Hallucination Count | 1 |
| Danger Recall | 0.0% |
| False Alarms | 0 |

### Test Case Status

- t1_fever: *FAIL* — reported risk: low.
- t2_pregnant_danger through t7_hinglish: *MISSING* — the corresponding audio files were not found in the test environment.

These results should not be interpreted as evidence of clinical safety or readiness. In particular, a danger recall of 0.0% means the current evaluation has not demonstrated successful detection of the evaluated danger cases.

*Next steps:* Restore or generate the missing scripted test assets, rerun the evaluation, inspect extraction errors and false negatives, and report the updated results with the test-set size and evaluation method.

## Privacy and Safety

- *No diagnosis:* The system is intended to support documentation, not diagnose conditions, prescribe medicines or replace a healthcare professional.
- *Human verification:* Extracted information must be checked and corrected by the health worker.
- *Uncertainty matters:* Missing, ambiguous or unverified information must not be presented as confirmed fact.
- *Responsible testing:* Use fictional, scripted test data for development and evaluation unless appropriate authorization and safeguards are in place.
- *Secure configuration:* Keep credentials outside source control and follow applicable privacy requirements before handling real patient information.

Any danger-sign or referral alert must be clinically reviewed and validated before real-world use. An alert must not be treated as a definitive clinical decision.

## Development During the Hackathon

*Hackathon date:* 23 October 2026

ASHA Scribe was developed for the Google Gemini Hackathon. The team should document its actual development timeline and distinguish pre-existing work from features created during the event.

The repository's commit history provides a record of changes. The statements in this section should be updated to match the actual code, assets and commits.

## Team Velionyx

- *Harish Choudhary* — Team Lead and Application Development
- *Vikash Kaushal* — Research and Presentation
- *Akshay Singh* — Testing and Demo

## Acknowledgements

- Google Gemini API
- Google Antigravity
- Streamlit
- Pydantic
- python-dotenv

We acknowledge the tools and libraries used in the project. Third-party assets, datasets and additional dependencies should be credited where applicable.

## Project Status

*Hackathon prototype — evaluation issues remain open.*

The current results do not establish production readiness. Further testing, validation, privacy safeguards and review by qualified healthcare stakeholders are necessary before real-world deployment.

---

Built by Team Velionyx for the Google Gemini Hackathon, RUVERSE Techfest 2026
