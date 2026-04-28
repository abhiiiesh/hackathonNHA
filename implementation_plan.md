# Automated Medical Claims Adjudication MVP

Building the full 14-layer architecture outlined in the `README.md` is a massive multi-month project. For a hackathon-winning "production-grade MVP", we need to focus on the core value proposition: **Intelligent Adjudication based on Standard Treatment Guidelines (STGs) with Explainability.**

## Goal Description

Build a functional MVP that ingests a medical claim, extracts necessary clinical information, retrieves the relevant STG from the provided dataset using RAG (Retrieval-Augmented Generation), and uses an LLM to evaluate the claim against the guidelines, providing an explainable Approve/Reject decision.

## User Review Required

> [!IMPORTANT]
> **LLM / API Keys:** To parse complex medical documents and perform the final adjudication reasoning against the STGs, we will need access to an LLM API (e.g., OpenAI, Google Gemini, or Anthropic Claude). Do you have an API key we can use for the backend?

> [!IMPORTANT]
> **OCR Strategy:** Building a custom TrOCR/PaddleOCR model from scratch takes time. For the MVP, I recommend either using a mock OCR response (assuming the document text is perfectly extracted) OR using a basic text extraction library (like `pytesseract` or cloud OCR) if you have sample bills. Should we implement basic OCR or mock the extraction phase to focus entirely on the RAG/Reasoning engine?

## Proposed Architecture for MVP

We will use a modern Python stack:
- **Backend:** `FastAPI` (for high-performance, async API endpoints)
- **RAG / Vector DB:** `LangChain` + `ChromaDB` (or `FAISS`) to index the STG PDFs.
- **Frontend (Demo):** `Streamlit` (fastest way to build a beautiful, interactive data app for the judges).

---

### Phase 1: STG Knowledge Base (RAG) Setup

We have hundreds of PDFs inside `Standard_Treatment_Guidelines_Set_28`. We need to convert these into a searchable knowledge graph.

#### [NEW] `app/stg_indexer.py`
A script that traverses the STG folders, reads the PDFs using `pdfplumber` or `PyPDFLoader`, chunks the text, and generates embeddings to store in a local ChromaDB instance. 
*This only needs to be run once to build the database.*

### Phase 2: Core Processing Engine

#### [NEW] `app/models/schemas.py`
Pydantic models for the system: `ClaimRequest`, `ExtractedData`, `STGContext`, `AdjudicationResult`.

#### [NEW] `app/services/extraction.py`
Service to handle incoming claims (images/PDFs) and extract Patient Info, Diagnosis, Procedure, and Line Items. (We will use an LLM for structured extraction from raw text).

#### [NEW] `app/services/rag_service.py`
Service that takes the extracted Diagnosis/Procedure and queries the ChromaDB to fetch the relevant STG rules.

#### [NEW] `app/services/adjudicator.py`
The "Clinical Reasoning Engine". It constructs a prompt combining the `Extracted Claim Data` + `Retrieved STG Rules` and asks the LLM to output a structured JSON:
```json
{
  "decision": "APPROVED | REJECTED | INVESTIGATE",
  "confidence_score": 0.95,
  "explanation": "The STG for this procedure requires an MRI, which is missing from the claim.",
  "fraud_flags": []
}
```

### Phase 3: API & Frontend

#### [NEW] `app/main.py`
FastAPI application exposing the `/adjudicate` endpoint which orchestrates the services above.

#### [NEW] `app/ui.py`
A Streamlit dashboard where users can:
1. Upload a sample claim document.
2. View the Extracted Data (simulating Layer 2).
3. View the retrieved STG context (simulating Layer 4).
4. See the final Decision and Explainability report (simulating Layers 8 & 9).

## Verification Plan

### Automated Tests
- Unit tests for the RAG retrieval function to ensure it fetches the correct STG PDF segment when given a specific diagnosis (e.g., "General Medicine - Rehabilitation").
- Unit tests for the Pydantic schema validation.

### Manual Verification
1. Run the `stg_indexer.py` to ensure the vector database is populated without errors.
2. Run the FastAPI server and Streamlit app locally.
3. Upload a sample (or mock) claim and verify the entire pipeline flow from ingestion to explanation.
