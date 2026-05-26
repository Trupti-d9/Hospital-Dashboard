import chromadb

def get_chroma_client():
    """
    Initializes a local ChromaDB client for document embeddings.
    """
    client = chromadb.PersistentClient(path="./chroma_store")
    return client

def build_vector_store():
    """
    Creates or retrieves the vector store collection for hospital data.
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="hospital_knowledge_base")
    return collection
