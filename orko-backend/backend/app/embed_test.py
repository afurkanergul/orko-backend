# app/embed_test.py
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# 1️⃣ Load your secret keys from .env.local (go up one folder)
load_dotenv("C:/Users/AhmetErgul/Downloads/ORKO_Step1-1_starter/orko-backend/backend/.env.local")

print("🔑 Loaded key prefix:", os.getenv("OPENAI_API_KEY"))

# 2️⃣ Connect to OpenAI using the loaded key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3️⃣ Function to turn text into embeddings
def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# 4️⃣ Sample texts to test
texts = [
    "Grain prices are rising in Kazakhstan.",
    "Corn exports are increasing.",
    "Weather is affecting wheat harvests."
]

# 5️⃣ Create a DataFrame (table)
df = pd.DataFrame({
    "doc_id": [1, 2, 3],
    "source": ["news", "report", "update"],
    "text": texts
})

# 6️⃣ Create embeddings for each text
df["embedding"] = df["text"].apply(get_embedding)

# 7️⃣ Save them to a CSV file for reference
df.to_csv("embeddings_sample.csv", index=False)
print("✅ Embeddings created and saved to embeddings_sample.csv")
