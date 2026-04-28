import json
from typing import Dict, List, Any

# Simulated JSON Knowledge Base (STG encoded rules)
STG_KNOWLEDGE_BASE = {
    "MG064A": { # Severe Anemia
        "package_name": "Severe Anemia",
        "rules": [
            {
                "id": "R1",
                "description": "Eligibility Check: Hemoglobin level must be < 7 g/dl",
                "check_fn": "check_hb_level",
                "severity": "CRITICAL"
            },
            {
                "id": "R2",
                "description": "Mandatory Document: CBC Report must be present",
                "check_fn": "check_mandatory_docs",
                "args": ["CBC Report"],
                "severity": "MAJOR"
            }
        ]
    },
    "S300031": { # PTCA (Angioplasty)
        "package_name": "PTCA",
        "rules": [
            {
                "id": "R1",
                "description": "Eligibility Check: Stenosis >= 70% in main coronary artery",
                "check_fn": "check_stenosis",
                "severity": "CRITICAL"
            },
            {
                "id": "R2",
                "description": "Mandatory Document: Angiogram Report",
                "check_fn": "check_mandatory_docs",
                "args": ["Angiogram Report"],
                "severity": "CRITICAL"
            }
        ]
    }
}

class RuleEngine:
    def __init__(self):
        self.kb = STG_KNOWLEDGE_BASE

    def evaluate(self, package_code: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates extracted clinical data against the deterministic STG JSON rules.
        """
        if package_code not in self.kb:
            return {
                "overall_decision": "FAIL",
                "confidence_score": 0.0,
                "rule_evaluations": [{
                    "rule_id": "PKG_UNKNOWN",
                    "description": "Package Code Validation",
                    "status": "FAIL",
                    "severity": "CRITICAL",
                    "message": f"Package '{package_code}' not found in Knowledge Base."
                }]
            }

        package_rules = self.kb[package_code]["rules"]
        results = []
        overall_status = "PASS"
        confidence_sum = 0

        for rule in package_rules:
            # Dynamically call the check function
            func = getattr(self, rule["check_fn"], self.default_check)
            args = rule.get("args", [])
            
            rule_result = func(extracted_data, *args)
            
            res = {
                "rule_id": rule["id"],
                "description": rule["description"],
                "status": rule_result["status"],
                "severity": rule["severity"],
                "message": rule_result["message"]
            }
            results.append(res)

            # Aggregate status
            if rule_result["status"] == "FAIL":
                if rule["severity"] == "CRITICAL":
                    overall_status = "FAIL"
                elif overall_status != "FAIL":
                    overall_status = "CONDITIONAL"

        # Calculate a mock confidence score based on pass rate
        pass_count = sum(1 for r in results if r["status"] == "PASS")
        confidence = (pass_count / len(package_rules)) if package_rules else 1.0

        return {
            "overall_decision": overall_status,
            "confidence_score": round(confidence, 2),
            "rule_evaluations": results
        }

    # --- Rule Check Functions ---

    def check_hb_level(self, data: Dict[str, Any]) -> Dict[str, str]:
        hb_level = data.get("lab_results", {}).get("hemoglobin")
        if hb_level is None:
            return {"status": "FAIL", "message": "Hemoglobin level not found in documents."}
        try:
            if float(hb_level) < 7.0:
                return {"status": "PASS", "message": f"Hb level {hb_level} g/dl is eligible (< 7)."}
            else:
                return {"status": "FAIL", "message": f"Hb level {hb_level} g/dl is not eligible (>= 7)."}
        except ValueError:
            return {"status": "CONDITIONAL", "message": "Could not parse Hemoglobin value."}

    def check_stenosis(self, data: Dict[str, Any]) -> Dict[str, str]:
        stenosis = data.get("clinical_findings", {}).get("stenosis_percentage")
        if stenosis is None:
            return {"status": "FAIL", "message": "Stenosis percentage not found."}
        try:
            if float(stenosis) >= 70.0:
                return {"status": "PASS", "message": f"Stenosis {stenosis}% is eligible (>= 70%)."}
            else:
                return {"status": "FAIL", "message": f"Stenosis {stenosis}% is not eligible (< 70%)."}
        except ValueError:
            return {"status": "CONDITIONAL", "message": "Could not parse Stenosis value."}

    def check_mandatory_docs(self, data: Dict[str, Any], doc_type: str) -> Dict[str, str]:
        docs = data.get("documents_provided", [])
        if doc_type in docs:
            return {"status": "PASS", "message": f"{doc_type} is present."}
        return {"status": "FAIL", "message": f"Missing mandatory document: {doc_type}."}

    def default_check(self, data: Dict[str, Any], *args) -> Dict[str, str]:
        return {"status": "CONDITIONAL", "message": "Rule check function not implemented."}
