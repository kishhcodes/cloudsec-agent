from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

def build_vectorstore(chunks, persist_path="data/embeddings"):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(persist_path, allow_dangerous_deserialization=True)
    return vectorstore
