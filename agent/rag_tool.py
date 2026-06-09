from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS

def setup_rag_retriever():
    """Charge ton rapport TechCorp, le découpe et crée la base vectorielle."""
    # 1. Charger TON texte existant
    loader = TextLoader("data/rapport_techcorp_2023.txt", encoding="utf-8")
    docs = loader.load()

    # 2. Découper en petits morceaux (Chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    splits = text_splitter.split_documents(docs)

    # 3. Utiliser le modèle d'Embedding de Vertex AI
    embeddings = VertexAIEmbeddings(model_name="text-embedding-004")

    # 4. Créer la base de données vectorielle locale (FAISS)
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    # On retourne le Retriever
    return vectorstore.as_retriever(search_kwargs={"k": 2})