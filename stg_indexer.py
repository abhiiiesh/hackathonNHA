import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

STG_ROOT = Path("c:/Users/JAINAB/Downloads/NewPyFolder/hackathonNHA/Standard_Treatment_Guidelines_Set_28/STG Set 28")
CHROMA_DB_DIR = Path("c:/Users/JAINAB/Downloads/NewPyFolder/hackathonNHA/chroma_db")

def build_index():
    print("Initializing embedding model...")
    # Using local embeddings so we don't need API keys for the indexing phase
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    documents = []
    
    print(f"Scanning directory: {STG_ROOT}")
    if not STG_ROOT.exists():
        print("ERROR: STG root directory not found!")
        return

    for root, _, files in os.walk(STG_ROOT):
        for file in files:
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(root, file)
                speciality = os.path.basename(os.path.dirname(root)) # e.g., "General Medicine"
                print(f"Loading PDF: {file}")
                
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                
                for doc in docs:
                    doc.metadata["speciality"] = speciality
                    doc.metadata["filename"] = file
                documents.extend(docs)

    print(f"Loaded {len(documents)} pages. Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    
    print(f"Creating Chroma DB with {len(split_docs)} chunks...")
    db = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding_function,
        persist_directory=str(CHROMA_DB_DIR)
    )
    
    print(f"Index built successfully at {CHROMA_DB_DIR}")

if __name__ == "__main__":
    build_index()
