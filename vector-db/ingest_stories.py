import os
import sys
import json
import chromadb

# Fix Windows console UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

STORAGE_PATH = os.path.join(os.path.dirname(__file__), "chroma_storage")
STORIES_JSON = os.path.join(os.path.dirname(__file__), "..", "tests", "data", "jira_stories.json")

def ingest_user_stories():
    """Initializes local persistent ChromaDB and ingests insurance user stories."""
    os.makedirs(STORAGE_PATH, exist_ok=True)
    
    # Persistent Chroma Client
    client = chromadb.PersistentClient(path=STORAGE_PATH)
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name="ins_user_stories",
        metadata={"hnsw:space": "cosine", "description": "Enterprise Insurance Requirements Vector Store"}
    )
    
    # Load JSON mock stories
    with open(STORIES_JSON, "r", encoding="utf-8") as f:
        stories = json.load(f)
        
    documents = []
    metadatas = []
    ids = []
    
    for story in stories:
        content = f"Story ID: {story['id']}\nTitle: {story['title']}\nFeature: {story['feature']}\nDescription: {story['description']}\nAcceptance Criteria:\n" + "\n".join(story["acceptance_criteria"])
        documents.append(content)
        metadatas.append({
            "id": story["id"],
            "title": story["title"],
            "feature": story["feature"],
            "tags": ",".join(story.get("tags", []))
        })
        ids.append(story["id"])
        
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"[SUCCESS] Ingested {len(ids)} User Stories into local ChromaDB store at {STORAGE_PATH}")
    return collection

if __name__ == "__main__":
    ingest_user_stories()
