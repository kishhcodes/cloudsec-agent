from langchain_community.document_loaders import PyPDFLoader
import os

def load_pdfs(pdf_dir: str):
    documents = []
    for file in os.listdir(pdf_dir):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_dir, file))
            docs = loader.load()
            documents.extend(docs)
    return documents
