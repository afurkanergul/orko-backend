# backend/app/db/vector_client.py
import os
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(".env.local")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not PINECONE_API_KEY or not OPENAI_API_KEY:
    raise ValueError("Missing keys in .env.local")

pc = Pinecone(api_key=PINECONE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

INDEX_NAME = "orko-embeddings-v2"

# Create index if missing (serverless mode)
if INDEX_NAME not in [idx["name"] for idx in pc.list_indexes()]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(INDEX_NAME)

def get_embedding(text: str, model="text-embedding-3-small"):
    resp = openai_client.embeddings.create(model=model, input=text)
    return resp.data[0].embedding

def upsert_vector(vector_id: str, embedding: list, metadata: dict):
    index.upsert(vectors=[{"id": vector_id, "values": embedding, "metadata": metadata}])
    print(f"🧩 Upserted vector {vector_id}")

def query_vector(query_text: str, top_k=3):
    emb = get_embedding(query_text)
    res = index.query(vector=emb, top_k=top_k, include_metadata=True)
    return res

if __name__ == "__main__":
    print("Indexes:", [i["name"] for i in pc.list_indexes()])
    print(query_vector("test document"))
