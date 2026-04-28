import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000/api/adjudicate_file"

st.set_page_config(
    page_title="AB PM-JAY Auto-Adjudication",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 AB PM-JAY Auto-Adjudication Portal (PS1)")
st.markdown("""
This system implements the **6-Brain Architecture** for deterministic medical claims adjudication. 
It ingests documents, constructs an episode timeline, and evaluates against strict STG JSON rules.
""")

st.sidebar.header("Upload Claim Document")
st.sidebar.info("Upload a PDF or Image. For this demo, uploading a file containing the word 'anemia' or 'ptca' will trigger specific STG evaluation paths.")
uploaded_file = st.sidebar.file_uploader("Upload Medical Record", type=["pdf", "png", "jpg"])

if uploaded_file is not None:
    if st.sidebar.button("Process Claim", type="primary"):
        with st.spinner("Processing through OCR, NLP, Timeline, and Rule Engine Brains..."):
            
            # Send file to FastAPI
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            try:
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    extracted = data["extracted_data"]
                    timeline = data["timeline"]
                    adj = data["adjudication"]
                    
                    st.success(f"✅ Claim {data['claim_id']} Processed Successfully!")
                    
                    col1, col2 = st.columns([1, 1.2])
                    
                    with col1:
                        st.subheader("📄 Extracted Clinical Data (NLP Brain)")
                        st.write(f"**Patient:** {extracted['patient_name']}")
                        st.write(f"**Diagnosis:** {extracted['diagnosis']}")
                        st.write(f"**Package Code:** {extracted['package_code']}")
                        
                        st.write("**Lab Results:**")
                        st.json(extracted.get("lab_results", {}))
                        
                        st.write("**Clinical Findings:**")
                        st.json(extracted.get("clinical_findings", {}))

                        st.subheader("⏱️ Episode Timeline (Timeline Brain)")
                        if timeline["timeline"]:
                            df_timeline = pd.DataFrame(timeline["timeline"])
                            # Reorder columns for display
                            df_timeline = df_timeline[["sequence", "event_type", "date", "source_document", "temporal_validity"]]
                            st.dataframe(df_timeline, hide_index=True)
                            
                            if not timeline["is_plausible"]:
                                st.error("🚨 Timeline Anomalies Detected:")
                                for flag in timeline["flags"]:
                                    st.write(f"- {flag}")
                        else:
                            st.info("No timeline events extracted.")

                    with col2:
                        st.subheader("⚖️ Adjudication Decision (Rule Engine Brain)")
                        
                        decision = adj["overall_decision"].upper()
                        if decision == "PASS":
                            st.success(f"### OVERALL: {decision}")
                        elif decision == "FAIL":
                            st.error(f"### OVERALL: {decision}")
                        else:
                            st.warning(f"### OVERALL: {decision}")
                            
                        st.metric("Rule Adherence Confidence", f"{adj['confidence_score'] * 100:.1f}%")
                        
                        st.markdown("### 📝 STG Rule Evaluation Log")
                        for rule in adj["rule_evaluations"]:
                            status_icon = "✅" if rule["status"] == "PASS" else ("❌" if rule["status"] == "FAIL" else "⚠️")
                            
                            with st.expander(f"{status_icon} Rule: {rule['description']}", expanded=True):
                                st.write(f"**Severity:** {rule['severity']}")
                                st.write(f"**System Message:** {rule['message']}")
                                
                else:
                    st.error(f"Backend Error: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend. Please ensure the FastAPI server is running (`uvicorn app.main:app --reload`).")
else:
    st.info("👈 Please upload a medical claim document in the sidebar to begin.")
