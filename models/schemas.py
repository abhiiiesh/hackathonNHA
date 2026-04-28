from pydantic import BaseModel, Field
from typing import List, Optional

class PatientInfo(BaseModel):
    name: str
    age: int
    gender: str
    patient_id: str

class LineItem(BaseModel):
    description: str
    quantity: int
    amount: float

class ExtractedData(BaseModel):
    """Data extracted from the raw claim document (Mocked for MVP)"""
    patient_info: PatientInfo
    hospital_name: str
    diagnosis: str
    procedures: List[str]
    line_items: List[LineItem]
    total_amount: float

class ClaimRequest(BaseModel):
    """Incoming request to adjudicate a claim."""
    claim_id: str
    document_text: str # In MVP, we might pass the raw text or rely on Mock extraction

class STGContext(BaseModel):
    """Context retrieved from the ChromaDB vector store."""
    speciality: str
    relevant_text: str
    source_document: str

class AdjudicationResult(BaseModel):
    """Final output from the Reasoning Engine."""
    decision: str = Field(..., description="APPROVED, REJECTED, or INVESTIGATE")
    confidence_score: float = Field(..., description="Score from 0.0 to 1.0")
    explanation: str = Field(..., description="Natural language reasoning citing the STG")
    fraud_flags: List[str] = Field(default=[], description="List of detected anomalies or flags")
