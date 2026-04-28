from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from models.schemas import STGContext

CHROMA_DB_DIR = Path("c:/Users/JAINAB/Downloads/NewPyFolder/hackathonNHA/chroma_db")

# Initialize embeddings (must match what was used in indexer)
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Global reference to DB so it's loaded once
try:
    vector_store = Chroma(
        persist_directory=str(CHROMA_DB_DIR), 
        embedding_function=embedding_function
    )
except Exception as e:
    print(f"Warning: Could not load Chroma DB: {e}")
    vector_store = None

def get_stg_context(diagnosis: str, procedures: list[str]) -> list[STGContext]:
    """
    Query the local ChromaDB to find relevant STG documentation for the given diagnosis/procedures.
    """
    if not vector_store:
        return []

    query = f"Diagnosis: {diagnosis}. Procedures: {', '.join(procedures)}"
    
    # Retrieve top 3 most relevant chunks
    docs = vector_store.similarity_search(query, k=3)
    
    contexts = []
    for doc in docs:
        contexts.append(
            STGContext(
                speciality=doc.metadata.get("speciality", "Unknown"),
                relevant_text=doc.page_content,
                source_document=doc.metadata.get("filename", "Unknown")
            )
        )
        
    return contexts
