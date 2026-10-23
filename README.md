# ASHA Scribe — Team Velionyx
### Gemini-Powered Voice Documentation Assistant for Community Healthcare

**Project Track:** AI for Society & Well-being — Healthcare  
**Event:** Google Gemini Hackathon, RUVERSE Techfest 2026  
**Institution:** Rungta International Skills University, Bhilai  
**Team:** Velionyx

---

## 1. Project Overview

ASHA Scribe is an AI-powered voice documentation assistant designed to help Accredited Social Health Activists (ASHA workers) document patient conversations more efficiently. The project explores how Google Gemini's audio-understanding and structured-output capabilities can convert spoken patient information into organized, editable healthcare form fields.

The proposed application allows a health worker to record or upload a patient conversation in Hindi or a supported local dialect. The AI then extracts relevant information, such as the patient's name, age, symptoms, medicines, and pregnancy-related details when applicable.

By reducing repetitive manual documentation, ASHA Scribe aims to help community health workers spend more time interacting with patients while maintaining a human-reviewed documentation process.

**Our vision:** Make community healthcare documentation simpler, more accessible, and more efficient through responsible AI assistance.

## 2. Problem Statement

ASHA workers play an important role in connecting communities with essential healthcare services across India. During household visits, they collect health-related information and maintain records that support follow-ups, reporting, and community health activities.

Manual documentation can be time-consuming, particularly when workers need to record multiple details after conversations with patients. Important information may be overlooked, entered incorrectly, or left incomplete. Repeated paperwork can also reduce the time available for direct interaction with patients.

There is an opportunity to use voice-based technology and AI-assisted information extraction to simplify this process while keeping healthcare workers responsible for reviewing and confirming the information.

ASHA Scribe addresses this challenge by exploring a voice-first approach to structured healthcare documentation.

## 3. Our Solution

ASHA Scribe proposes a simple workflow that transforms a patient conversation into an editable documentation form.

### How It Works

1. **Record or Upload Audio:** The health worker records or uploads a patient conversation in Hindi or a supported language.
2. **AI Audio Understanding:** Google Gemini processes the audio and identifies relevant information stated during the conversation.
3. **Structured Information Extraction:** The extracted details are organized into structured fields, including patient name, age, symptoms, medicines, and relevant pregnancy-related information.
4. **Missing Information Detection:** Missing or unclear fields are highlighted so the health worker knows which details require verification.
5. **Potential Danger-Sign Review:** Potential warning signs mentioned in the conversation can be flagged for human review. These flags are not medical diagnoses.
6. **Human Review and Confirmation:** The health worker checks the extracted information, corrects errors, completes missing details where possible, and confirms the final entries.

The objective is to support documentation rather than replace professional medical judgment. The application must not independently diagnose conditions or prescribe treatment.

## 4. Google Gemini Usage

Google Gemini is the core AI component planned for ASHA Scribe. Its audio-understanding and structured-output capabilities are intended to support the conversion of spoken information into organized documentation.

### Planned AI Capabilities

- **Audio Understanding:** Process supported audio recordings containing Hindi or other supported speech.
- **Contextual Extraction:** Identify relevant patient details from the conversation without intentionally filling gaps through unsupported assumptions.
- **Structured JSON Output:** Return extracted information in a consistent format that the application can map to patient form fields.
- **Missing and Unclear Field Identification:** Help identify information that is absent, incomplete, or uncertain.
- **Potential Danger-Sign Flagging:** Identify selected warning signs for review by the health worker, without generating an independent diagnosis.

The Gemini integration must be tested with representative synthetic audio before these capabilities are described as operational. Structured output improves consistency of formatting but does not guarantee that extracted information is medically or factually correct.

## 5. Technology Stack

ASHA Scribe is designed around a lightweight web architecture that can be developed and tested within a short hackathon.

| Technology | Purpose |
|---|---|
| HTML5 | Structure the application interface and patient form |
| CSS3 | Create a responsive, accessible, mobile-friendly design |
| JavaScript | Handle audio interactions, form updates, and frontend API requests |
| Node.js | Run the backend JavaScript environment |
| Express.js | Provide backend routes and connect the frontend to the AI service |
| Google Gemini API | Process supported audio and extract structured information |
| Git and GitHub | Track genuine code changes and collaborate across the team |
| Google Antigravity | Assist the team with development and code iteration |

The final technology list and model details should reflect the components actually used in the implemented application.

## 6. Key Features

The following features define the intended minimum viable product (MVP). Each feature should be marked as implemented only after it has been built and tested.

- **Audio Recording and Upload:** Provide a way to supply a patient conversation to the application.
- **AI-Assisted Information Extraction:** Extract relevant details from supported audio using Gemini.
- **Structured Patient Form:** Display extracted information in clearly labeled, editable fields.
- **Missing-Field Highlighting:** Identify information that has not been provided or could not be extracted reliably.
- **Unclear-Information Review:** Highlight uncertain details for manual verification.
- **Potential Danger-Sign Alerts:** Present selected warning signs for review without making a diagnosis.
- **Human Confirmation:** Allow the health worker to review and correct the extracted information before confirming entries.
- **Error Handling:** Communicate upload, API, and processing failures clearly instead of silently displaying invented results.

## 7. Setup and Installation

These instructions describe the intended local development setup. Verify them against the final repository before publishing.

### Prerequisites

- Node.js and npm installed
- Git installed
- Access to the project repository
- A valid Gemini API key from Google AI Studio
- Internet connectivity for Gemini API requests

### Clone the Repository

```bash
git clone https://github.com/Hsisidie/Velionyx-GGH.git
cd Velionyx-GGH
```

### Install Dependencies

Run the following command if the project uses the planned Node.js and Express stack:

```bash
npm install
```

If dependencies have not yet been added to `package.json`, install the packages specified by the final implementation before running the application.

### Configure Environment Variables

Create a `.env` file in the project root and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your own valid key. Never publish the real key in source code, screenshots, commits, or the README.

Ensure `.env` is listed in `.gitignore`. The backend should read the key from the server environment, not from frontend JavaScript.

### Run the Application

Use the actual start script configured in `package.json`. For example, if the project defines a start script:

```bash
npm start
```

Open the local URL printed by the application in your browser.

**Note:** The exact setup commands, start script, and local URL must be confirmed against the final implementation.

## 8. Team Members and Responsibilities

### Harish Choudhary — Team Lead and Full-Stack Development
Coordinates the overall application architecture, core workflow, frontend-backend integration, repository management, and final technical integration. Ensures that the application is tested as a complete workflow.

### Vikash Kaushal — Backend and Gemini API Integration
Works on Gemini API configuration, audio processing, structured data extraction, backend validation, error handling, and testing the AI responses.

### Akshay Singh — Documentation, Demo, and Presentation
Prepares the project documentation, organizes application screenshots, creates the demonstration sequence, records testing observations, and prepares explanations and answers for judging.

All team members contribute to implementation, testing, integration, and the final presentation according to their actual work.

## 9. Testing and Limitations

Testing is essential because errors in healthcare-related information can have serious consequences. The team should evaluate the application using synthetic patient conversations rather than identifiable real patient data.

### Testing Priorities

- Verify whether the extracted name and age match the conversation.
- Check whether symptoms and explicitly mentioned medicines are captured correctly.
- Test conversations with missing or unclear information.
- Verify that the application highlights missing fields instead of inventing values.
- Test potential danger-sign alerts with carefully selected synthetic examples.
- Confirm that form fields can be reviewed and edited.
- Test invalid audio files, unsupported formats, oversized uploads, missing API keys, and API failures.
- Verify that secrets and patient audio are not inadvertently exposed or permanently stored.

### Current Limitations

As a hackathon MVP, ASHA Scribe may have limitations in speech recognition, regional dialect support, noisy audio, medical terminology, and the accuracy of extracted information. Model output can be incomplete or incorrect and therefore requires human verification.

The project should not be described as clinically validated unless an appropriate validation process has actually been completed. Real-world deployment would require additional privacy and security safeguards, clinical review, usability testing with intended users, and evaluation under realistic field conditions.

## 10. Future Scope

ASHA Scribe could be extended beyond the initial hackathon prototype through carefully evaluated improvements.

- **Expanded Language Support:** Improve support for additional Indian languages and regional dialects, including Chhattisgarhi, subject to model capability and testing.
- **Offline-First Operation:** Explore secure temporary local storage and synchronization when connectivity becomes available, with appropriate access controls and conflict handling.
- **Authorized Healthcare-System Integration:** Investigate integration with relevant public-health reporting systems through authorized APIs and required approvals.
- **Improved Safety Review:** Evaluate warning-sign identification against approved clinical guidance and qualified healthcare professional oversight.
- **Supervisor Review:** Explore privacy-conscious tools for authorized supervisors to assess documentation completeness and correction patterns.
- **Broader Community Healthcare Use:** Evaluate whether the workflow can be adapted for additional community healthcare programs following pilot testing.

These are potential future enhancements, not claims about existing capabilities. Each would require technical evaluation, appropriate safeguards, and testing before deployment.

## 11. Privacy, Safety, and Responsible AI

ASHA Scribe is intended to assist documentation, not make independent clinical decisions.

The project follows these design principles:

- Use synthetic patient data for development and demonstrations.
- Keep API keys and other secrets on the backend.
- Avoid unnecessary collection, logging, or retention of sensitive patient information.
- Require human review and confirmation of extracted information.
- Present potential danger signs as review alerts, not definitive diagnoses.
- Avoid claiming that the absence of an alert means a patient is safe.
- Evaluate accuracy, privacy, and usability before any real-world deployment.

Any future handling of real patient data must use appropriate consent, access controls, security measures, and applicable privacy and healthcare requirements.

## 12. Credits and Acknowledgements

We acknowledge the Google Gemini API and its official documentation as resources for exploring audio understanding and structured information extraction.

We also acknowledge the tools and development resources actually used by Team Velionyx during the hackathon.

This project is being developed for the Google Gemini Hackathon at RUVERSE Techfest 2026, with the aim of exploring how responsible AI can support community healthcare documentation.

---

**Team Velionyx | ASHA Scribe**  
*Supporting community healthcare workers through AI-assisted documentation.*
