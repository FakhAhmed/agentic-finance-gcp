import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import Chroma

def setup_rag_retriever():
    """Charge un PDF et le vectorise par lots (Batching) sans persistance."""
    
    pdf_path = "data/rapport_financier.pdf"
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"🚨 Fichier introuvable : {pdf_path}. Mets un PDF dans le dossier data !")

    # 1. Lecture du PDF
    print(f"📖 Lecture et découpage du PDF massif : {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # 2. Découpage
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    print(f"📊 Le PDF a été découpé en {len(splits)} morceaux.")
    print("⏳ Vectorisation par lots en cours (pour respecter les quotas Vertex AI)...")

    # 3. Initialisation du modèle et d'une base ChromaDB "volatile" (en mémoire vive)
    embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
    vectorstore = Chroma(embedding_function=embeddings) # Remarque : pas de persist_directory !

    # 4. LE BATCHING : On insère par paquets de 100 pour contourner la limite de 250
    batch_size = 100
    for i in range(0, len(splits), batch_size):
        batch = splits[i : i + batch_size]
        vectorstore.add_documents(batch)
        print(f"  -> 🔄 Lot inséré : {min(i + batch_size, len(splits))} / {len(splits)} morceaux envoyés à GCP...")

    print("✅ Base vectorielle temporaire terminée !")
    
    return vectorstore.as_retriever(search_kwargs={"k": 3})