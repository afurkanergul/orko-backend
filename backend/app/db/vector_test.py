# app/db/vector_test.py
import os
import random
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv(".env.local")

# --- If your environment loader doesn't read .env.local automatically, uncomment these two lines:
# from dotenv import load_dotenv
# load_dotenv(".env.local")

def make_fake_embedding(dim: int = 1536) -> list[float]:
    """Create a fake embedding vector with 1536 numbers."""
    random.seed(42)
    return [random.random() for _ in range(dim)]

def main():
    print("🔗 Connecting to Pinecone index 'orko-embeddings'...")

    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("❌ PINECONE_API_KEY not found in environment.")

    pc = Pinecone(api_key=api_key)
    index = pc.Index("orko-embeddings")

    # Create a fake embedding (vector)
    vector = make_fake_embedding(1536)

    # Insert (upsert) the vector
    print("📥 Upserting test vector...")
    upsert_response = index.upsert(
        vectors=[
            {
                "id": "test-1",
                "values": vector,
                "metadata": {"source": "unit-test", "doc_id": "demo-1"}
            }
        ]
    )
    print("✅ Upsert result:", upsert_response)

    # Query the same vector
    print("🔍 Querying nearest neighbors...")
    query_response = index.query(
        vector=vector,
        top_k=1,
        include_values=False,
        include_metadata=True,
    )
    print("✅ Query result:", query_response)

    # Validation
    top_match_id = query_response.matches[0].id if query_response.matches else None
    if top_match_id == "test-1":
        print("🎯 Validation OK: Retrieved top-1 == inserted sample (test-1)")
    else:
        print("⚠️ Validation FAILED: top-1 did not match 'test-1'")

if __name__ == "__main__":
    main()
