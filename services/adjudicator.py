import os
import json
from dotenv import load_dotenv
from models.schemas import ExtractedData, STGContext, AdjudicationResult

# Support multiple LLMs via Langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

def get_llm():
    if os.getenv("GOOGLE_API_KEY"):
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)
    elif os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
    else:
        raise ValueError("No LLM API Key found. Please set GOOGLE_API_KEY or OPENAI_API_KEY in .env")

def adjudicate_claim(claim_data: ExtractedData, stg_contexts: list[STGContext]) -> AdjudicationResult:
    """
    Uses an LLM to evaluate the claim against the retrieved Standard Treatment Guidelines.
    """
    llm = get_llm()
    
    # Format the STG contexts into a single string
    stg_text = ""
    for idx, ctx in enumerate(stg_contexts):
        stg_text += f"\n[Document: {ctx.source_document}]\n{ctx.relevant_text}\n"
    
    if not stg_text:
        stg_text = "No Standard Treatment Guidelines found for this diagnosis."

    # Construct the Prompt
    prompt_template = PromptTemplate(
        input_variables=["claim", "stg_text"],
        template="""
You are an expert Medical Claims Adjudicator for the National Health Authority (NHA).
Your job is to review the following Medical Claim Data and determine if it should be APPROVED, REJECTED, or INVESTIGATED, strictly based on the provided Standard Treatment Guidelines (STG).

--- MEDICAL CLAIM DATA ---
{claim}

--- STANDARD TREATMENT GUIDELINES (STG) CONTEXT ---
{stg_text}

--- INSTRUCTIONS ---
1. Compare the Diagnosis and Procedures in the claim against the STG Context.
2. Ensure all required procedures/items according to the STG are present.
3. Check for any anomalies or potential fraud (e.g., claiming a procedure that doesn't match the diagnosis).
4. Provide a structured JSON output exactly matching the following schema. Do NOT wrap it in markdown block quotes.

JSON SCHEMA:
{{
  "decision": "APPROVED" | "REJECTED" | "INVESTIGATE",
  "confidence_score": 0.95,
  "explanation": "Provide a clear, natural language explanation citing the specific STG rule that led to this decision.",
  "fraud_flags": ["List any anomalies, or leave empty if none"]
}}
"""
    )

    prompt = prompt_template.format(
        claim=claim_data.model_dump_json(indent=2),
        stg_text=stg_text
    )
    
    try:
        response = llm.invoke(prompt)
        content = response.content
        
        # Clean markdown code block formatting if LLM includes it
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        parsed_json = json.loads(content.strip())
        
        return AdjudicationResult(**parsed_json)
        
    except Exception as e:
        print(f"Error during adjudication: {e}")
        return AdjudicationResult(
            decision="INVESTIGATE",
            confidence_score=0.0,
            explanation=f"System failed to process the adjudication due to an internal error: {str(e)}",
            fraud_flags=["System Error"]
        )
