# 🏥 Automated Medical Claims Adjudication & Fraud Detection
**NHA Hackathon Submission | Track: Intelligent Claims Processing & Auto-Adjudication**

## 🎯 Problem Statement Mapping
The National Health Authority (NHA) processes millions of claims under Ayushman Bharat PM-JAY. Manual adjudication is slow, error-prone, and susceptible to sophisticated fraud. 
This project builds an **AI-driven, NHCX-ready Claims Adjudication Engine** that automates clinical validation against Standard Treatment Guidelines (STGs) while maintaining strict human-in-the-loop audibility and fraud detection.

---

## 🚀 MVP Scope.

For the Hackathon MVP, we focused on the core **"Zero-Trust Clinical Validation"** loop, prioritizing Explainability over scale.

### 🏆 Hackathon MVP Scope (Implemented)
- **STG Knowledge Graph (RAG):** Ingestion of 7 specialities of Set-28 STG PDFs into a vector database (ChromaDB).
- **Core Reasoning Engine:** LLM-based evaluation of extracted claim data against the STG knowledge base.
- **Explainability Layer:** Outputting clear Approve/Reject decisions with exact rule-to-evidence mappings.
- **Demo UI:** Streamlit dashboard for end-to-end visualization.

### 🔭 1-Year Target Architecture (Planned)
- **Visual Forensics:** Forgery and deepfake detection on uploaded documents.
- **Temporal Reasoning:** Event-sequence anomaly detection (e.g., procedure before admission).
- **Graph ML Fraud Detection:** Network analysis of hospitals and patients to catch organized fraud rings.
- **Enterprise Scale:** Microservices via Kubernetes & Kafka handling 50K+ claims/day.

---

## 🎬 Demo Narrative
The system follows a strict, transparent pipeline:
1. **Input:** A user (hospital/TPA) uploads a medical claim document (PDF/Image) via the UI.
2. **Extraction:** The system extracts structured data (Patient Demographics, Diagnosis, Procedures, Line Items).
3. **Retrieval:** Based on the Diagnosis, the system queries the local RAG Vector Database for the exact STG rule (e.g., "General Medicine - Rehabilitation").
4. **Adjudication:** The Reasoning Engine evaluates the claim against the STG.
5. **Output (Explainability):** The UI displays a `Decision` (APPROVED, REJECTED, CONDITIONAL) along with a `Confidence Score` and a natural language `Explanation` detailing *why* the decision was made, highlighting the relevant STG clause.

---

## ⚙️ Implementation Details

### Repository Structure
```text
hackathonNHA/
├── Standard_Treatment_Guidelines_Set_28/ # Raw STG PDFs from NHA
├── app/
│   ├── README.md               # You are here
│   ├── main.py                 # FastAPI Application (API Layer)
│   ├── ui.py                   # Streamlit Dashboard (Demo UI)
│   ├── stg_indexer.py          # Script to ingest PDFs into ChromaDB
│   ├── models/                 # Pydantic Schemas
│   └── services/               # Extraction, RAG, and Adjudication logic
├── env/                        # Virtual Environment
└── requirements.txt            # Python Dependencies
```

### Setup & Installation
1. **Clone & Environment Setup:**
   ```bash
   git clone <repo-url>
   cd hackathonNHA
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   pip install -r requirements.txt
   ```
2. **Environment Variables:**
   Create a `.env` file in the `app/` directory:
   ```env
   LLM_API_KEY=your_api_key_here
   ```
3. **Build the STG Database (Run Once):**
   ```bash
   python app/stg_indexer.py
   ```
4. **Run the Backend API:**
   ```bash
   uvicorn app.main:app --reload
   ```
5. **Run the Demo UI:**
   ```bash
   streamlit run app/ui.py
   ```

---

## 📊 Evaluation & Metrics (SLA)
To prove production-readiness, our system is evaluated against the following targets:
- **Precision/Recall on STG Retrieval:** > 92% accuracy in retrieving the correct STG clause for a given diagnosis.
- **Latency SLA:** < 3 seconds for document extraction to decision output.
- **Expected Manual Effort Reduction:** 40% reduction in level-1 manual review for clear-cut cases.
- **Explainability Score:** 100% of auto-rejected claims feature a traceable, human-readable reason code.

---

## 🇮🇳 Compliance & Localization
- **NHCX / ABDM Ready:** Architecture is designed to interface with the National Health Claims Exchange (NHCX) JSON payload standards.
- **Data Privacy:** PII masking at the extraction layer to comply with the Digital Personal Data Protection (DPDP) Act.
- **Auditability:** Every LLM decision logs the exact context chunk and temperature used, fulfilling government audit requirements.

---

### Detailed 14-Layer Architecture Framework (Reference)

1. **Data Ingestion:** Multi-format (PDF/DICOM), ABDM-ready.
2. **Document Understanding:** PaddleOCR + LayoutLMv3.
3. **Visual Forensics:** Implant sticker & signature validation.
4. **Clinical Intelligence:** RAG for STG validation (Implemented).
5. **Rule Engine:** Confidence-aware hierarchical rules.
6. **Temporal Reasoning:** Episode mismatch detection.
7. **Fraud Detection:** Isolation forests and Hospital-Patient Graph ML.
8. **Decision Engine:** Weighted risk scoring.
9. **Explainability Layer:** Rule-evidence mapping (Implemented).
10. **Learning System:** Human-in-the-loop active learning.
11. **Human Review:** Escalation dashboards.
12. **Scalability:** Kafka + Kubernetes.
13. **Security:** Data encryption at rest.
14. **Evaluation:** Model drift detection.
