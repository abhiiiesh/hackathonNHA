import fitz  # PyMuPDF
import re
from typing import Dict, Any

def extract_text_from_file(file_bytes: bytes) -> str:
    """
    Uses PyMuPDF to extract text from a PDF file.
    For images, a real system would use PaddleOCR here. 
    We simulate OCR by just reading text if it's a PDF.
    """
    try:
        # Open PDF from bytes
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading file (maybe it's an image?): {e}")
        return "Simulated OCR Text: Patient Name: Rajesh Kumar. Diagnosis: Severe Anemia. Hb Level: 6.5. Admission Date: 02-Feb-26."

def nlp_extract_entities(text: str) -> Dict[str, Any]:
    """
    Simulates the 'NLP Brain' (BioBERT/spaCy).
    In reality, this extracts structured data from the raw OCR text.
    """
    data = {
        "patient_name": "Unknown",
        "diagnosis": "Unknown",
        "package_code": "Unknown",
        "lab_results": {},
        "clinical_findings": {},
        "documents_provided": [],
        "timeline_events": []
    }

    # Simulate Extraction Logic based on keywords
    text_lower = text.lower()
    
    if "anemia" in text_lower:
        data["patient_name"] = "Rajesh Kumar"
        data["diagnosis"] = "Severe Anemia"
        data["package_code"] = "MG064A"
        
        # Simulate regex extraction for Hb level
        hb_match = re.search(r"hb.*?(\d+\.?\d*)", text_lower)
        if hb_match:
            data["lab_results"]["hemoglobin"] = hb_match.group(1)
        else:
            # default mock if missing
            data["lab_results"]["hemoglobin"] = "6.5"
            
        data["documents_provided"] = ["Discharge Summary", "CBC Report"]
        data["timeline_events"] = [
            {"event_type": "Admission", "date_str": "02-Feb-2026", "source": "Discharge Summary"},
            {"event_type": "Diagnostic Investigation", "date_str": "02-Feb-2026", "source": "CBC Report"},
            {"event_type": "Discharge", "date_str": "06-Feb-2026", "source": "Discharge Summary"}
        ]

    elif "ptca" in text_lower or "angioplasty" in text_lower:
        data["patient_name"] = "Aarti Sharma"
        data["diagnosis"] = "Coronary Artery Disease"
        data["package_code"] = "S300031"
        data["clinical_findings"]["stenosis_percentage"] = "85.0"
        data["documents_provided"] = ["Discharge Summary", "Angiogram Report"]
        data["timeline_events"] = [
            {"event_type": "Admission", "date_str": "10-Mar-2026", "source": "Discharge Summary"},
            {"event_type": "Diagnostic Investigation", "date_str": "10-Mar-2026", "source": "Angiogram Report"},
            {"event_type": "Procedure", "date_str": "11-Mar-2026", "source": "Angiogram Report"},
            {"event_type": "Discharge", "date_str": "14-Mar-2026", "source": "Discharge Summary"}
        ]

    return data
