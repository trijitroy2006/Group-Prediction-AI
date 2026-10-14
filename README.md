# Prediction AI

---

## 🚀 Live Application
Test and explore the live cloud version here:  
👉 **[prediction-ai-app.streamlit.app](https://prediction-ai-app.streamlit.app/)**

---

## 📌 Executive Summary
**Prediction AI** is a collaborative decision-support system engineered to evaluate business ventures, forecast startup failure likelihoods, and deliver strategic remedies. Developed as a multi-stage team initiative, the platform merges quantitative market evaluation with generative artificial intelligence to deliver transparent, data-driven venture viability scores.

---

## 🎯 Core Capabilities
* **Interactive Venture Submission:** Intake interface capturing business model, industry sector, target audience, capital allocation, and team composition.
* **Deterministic Risk Scoring:** Weighted mathematical formulas assessing team capacity, financial runway, competitive pressure, and execution feasibility.
* **Autonomous SWOT Formulation:** Dynamically synthesizes internal strengths/weaknesses and external opportunities/threats.
* **Cognitive Strategic Advisory:** Connects with Google Gemini LLMs to formulate actionable pivot pathways and operational improvements.
* **Dynamic Risk Dashboarding:** Visual representations of feasibility breakdowns, market sizing (TAM/SAM/SOM), and categorized mitigation playbooks.

---

## 👥 Collaborative Engineering Milestones

```
[Milestone 1: Foundations & Market Sizing]
       │
       ▼
[Milestone 2: Risk Scoring & SWOT Matrix]
       │
       ▼
[Milestone 3: Gemini LLM & Mitigation Engine]
       │
       ▼
[Milestone 4: Orchestration & Streamlit Deployment]
```

### 🔹 Milestone 1 — Data Architecture & Market Modeling
* Built initial database schema and project submission pipelines.
* Modeled market sizing estimations (TAM, SAM, SOM) and annual growth projections.
* Established competitor discovery and market share distribution graphs.

### 🔹 Milestone 2 — Risk Matrix & Feasibility Logic
* Implemented multi-dimensional risk scoring algorithms across four critical pillars:
  * Financial Solvency & Runway
  * Team Capability & Domain Experience
  * Market Saturation & Competitive Moat
  * Technical & Regulatory Complexity
* Developed an algorithmic SWOT matrix evaluating qualitative and quantitative variables.

### 🔹 Milestone 3 — AI Recommendations & Strategy Synthesis
* Integrated the **Google Gemini API** (`google-genai`) for real-time strategic reasoning.
* Engineered the dynamic mitigation engine categorizing risks into High, Medium, and Low priorities with tailored countermeasures.
* Transitioned storage to an embedded, zero-configuration SQLite architecture (`ml_project.db`).

### 🔹 Milestone 4 — Full Pipeline Integration & Cloud Deployment
* Synchronized the end-to-end multi-agent orchestration workflow across project intake, scoring, advisory, and reporting.
* Designed the unified four-tab analytical interface (*Project Setup, Risk Assessment, Strategy & Mitigations, Dashboard & Reports*).
* Deployed the full production build to Streamlit Community Cloud with encrypted secrets management.

---

## 🏗️ Technical Architecture & Stack

| Layer | Technologies | Purpose |
| :--- | :--- | :--- |
| **User Interface** | Streamlit, Custom HTML/CSS | Responsive, single-page analytical dashboard |
| **Intelligence Engine** | Google Gemini 2.5 Flash / Pro | Generative reasoning, advisory synthesis, SWOT analysis |
| **Analytics Core** | Python, NumPy, Pandas | Algorithmic risk index calculation, market sizing calculations |
| **Data Layer** | SQLite3 | Embedded persistence for project profiles and analytical history |
| **Deployment** | Streamlit Community Cloud, Git | Automated CI/CD and globally available hosting |

---

## 📂 Repository Structure

```
Group-Prediction-AI/
├── app_streamlit.py           # Unified Streamlit application entry point
├── llm_service.py             # Google Gemini API connector & prompt workflows
├── recommendation_engine.py   # Strategic recommendation logic
├── mitigation_engine.py       # Risk categorization & mitigation mapping
├── market_analysis.py         # TAM/SAM/SOM and market estimation functions
├── database.py                # SQLite database management routines
├── requirements.txt           # Project environment dependencies
├── .env.example               # Template for required environment variables
└── README.md                  # Team project documentation
```

---

## 💻 Local Setup & Installation

### Prerequisites
* Python 3.10 or higher installed on your system
* A valid Google Gemini API key ([Get an API key here](https://aistudio.google.com/))

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/trijitroy2006/Group-Prediction-AI.git
   cd Group-Prediction-AI
   ```

2. **Create and activate a virtual environment:**
   * **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your environment:**
   Copy `.env.example` to `.env` and insert your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Launch the application:**
   ```bash
   python -m streamlit run app_streamlit.py
   ```

---

## 👩‍🏫 Mentorship & Guidance
We extend our deepest gratitude to our mentor, **Mrs. Sophia**, under whose guidance, leadership, and continuous support we successfully developed and completed this entire project.

---

## 👥 Project Contributors
This project was collaboratively engineered by:
* **Rabjyotsingh Majethiya**
* **Ruchita Jagdish Chaudhari**
* **S.A.R.V. Likhith**
* **Sachin Chaubey**
* **Shravani Gajanan Hiwase**
* **Trijit Roy**
* **Vegi Sangeetha**

---

## 🛡️ License & Academic Disclosure
This project was developed collaboratively for academic and research purposes to demonstrate the convergence of Machine Learning, Generative AI, and software engineering in business analytics.
