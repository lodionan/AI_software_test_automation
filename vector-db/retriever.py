import os
import sys
import chromadb

# Fix Windows console UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

STORAGE_PATH = os.path.join(os.path.dirname(__file__), "chroma_storage")

def get_relevant_stories(query: str, n_results: int = 2) -> list[dict]:
    """Retrieves semantically relevant User Stories from local ChromaDB."""
    if not os.path.exists(STORAGE_PATH):
        raise FileNotFoundError("ChromaDB storage not found. Please run vector-db/ingest_stories.py first.")
        
    client = chromadb.PersistentClient(path=STORAGE_PATH)
    collection = client.get_collection("ins_user_stories")
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    retrieved = []
    if results and "documents" in results and results["documents"]:
        for doc, meta, doc_id in zip(results["documents"][0], results["metadatas"][0], results["ids"][0]):
            retrieved.append({
                "id": doc_id,
                "metadata": meta,
                "document": doc
            })
            
    return retrieved

if __name__ == "__main__":
    query = "annuity premium rider calculation and interest bonus"
    res = get_relevant_stories(query)
    print(f"[SEARCH] Results for '{query}':")
    for r in res:
        print(f" - [{r['id']}] {r['metadata']['title']}")
