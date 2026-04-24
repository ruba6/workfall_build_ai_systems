from fastapi import FastAPI
import chromadb
import logging
import os
from dotenv import load_dotenv
from chromadb.utils import embedding_functions
from crewai import LLM

app = FastAPI()

client = chromadb.Client()
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    "insights",
    embedding_function=ef
)

load_dotenv("keys.env")
key = os.environ["GROQ_API_KEY"]
if not key:
    raise ValueError("GROQ_API_KEY not set")

print("Groq API key loaded ✅")

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_insight(data):
    prompt = f"""
    Analyze this property:

    Location: {data.get('location')}
    Budget: {data.get('budget')}

    Provide:
    - Market trend
    - Risk
    - Opportunity
    """

    res = llm.call(prompt)
    return res   

@app.get("/agent-card")
def agent_card():
    return {
        "agent_name": "marketing_agent",
        "capabilities": ["analyze_property"],
        "endpoint": "http://localhost:8003"
    }

@app.post("/analyze")
def analyze(req: dict):
    data = req.get("payload", {})
    property_id = data.get("property_id")

    if not property_id:
        return {"status": "error", "error": "Missing property_id"}

    # Placeholder LLM-style insight
    insight = generate_insight(data)

    collection.add(
        documents=[insight],
        metadatas=[{"property_id": property_id}],
        ids=[property_id]
    )

    logging.info(f"Insight stored for {property_id}")

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
