from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.extraction import extract_text_from_file, nlp_extract_entities
from rules_engine import RuleEngine
from timeline_service import TimelineService
import uuid

app = FastAPI(
    title="NHA Auto-Adjudication Engine (Fullstack)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rule_engine = RuleEngine()
timeline_service = TimelineService()

@app.get("/")
def health_check():
    return {"status": "healthy"}

@app.post("/api/adjudicate_file")
async def adjudicate_file_endpoint(file: UploadFile = File(...)):
    try:
        # 1. Ingestion (Read File)
        file_bytes = await file.read()
        claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"

        # 2. OCR Brain (PyMuPDF / simulated OCR)
        raw_text = extract_text_from_file(file_bytes)
        
        # 3. NLP Brain (Entity Extraction)
        extracted_data = nlp_extract_entities(raw_text)
        package_code = extracted_data["package_code"]

        # 4. Timeline Brain
        timeline_result = timeline_service.construct_timeline(extracted_data.get("timeline_events", []))

        # 5. Deterministic Rule Engine Brain (40% Weight)
        rule_evaluation = rule_engine.evaluate(package_code, extracted_data)

        # Merge timeline flags into the decision if timeline is invalid
        if not timeline_result["is_plausible"]:
            rule_evaluation["overall_decision"] = "CONDITIONAL"
            rule_evaluation["rule_evaluations"].append({
                "rule_id": "TIMELINE_CHK",
                "description": "Episode timeline plausibility",
                "status": "FAIL",
                "severity": "MAJOR",
                "message": " | ".join(timeline_result["flags"])
            })

        return {
            "status": "success",
            "claim_id": claim_id,
            "filename": file.filename,
            "extracted_data": extracted_data,
            "timeline": timeline_result,
            "adjudication": rule_evaluation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
