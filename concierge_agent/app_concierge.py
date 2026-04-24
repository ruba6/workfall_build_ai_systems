from fastapi import FastAPI
import requests, logging
from typing import TypedDict
from langgraph.graph import StateGraph
import chromadb
import json
from dotenv import load_dotenv
from crewai import LLM
from chromadb.utils import embedding_functions
import os
import re

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

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        return json.loads(match.group())
    return {"intent": "unknown"}

def parse_intent(user_query: str):
    prompt = f"""
    You are a strict JSON generator.
    Extract data from this query:
    "{user_query}"
    Return ONLY valid JSON:
    {{
        "intent": "buy|rent",
        "location": "string",
        "budget": number,
        "property_type": "string"
    }}
    No explanation. No text. Only JSON.
    """

    response = llm.call(prompt)
    try:
        # return json.loads(response.content)
        return extract_json(response)
    except:
        return {"intent": "unknown"}

# ---------- STATE ----------
class State(TypedDict):
    user_query: str
    parsed_data: dict
    customer_id: str
    property_id: str
    insights: str
# ---------- NODES ----------

def parse_node(state: State):
    parsed = parse_intent(state["user_query"])
    state["parsed_data"] = parsed
    return state

def customer_node(state: State):
    try:
        res = requests.post("http://localhost:8001/onboard", json={
            "payload": {"name": "guest_user"}
        }).json()

        state["customer_id"] = res.get("data", {}).get("customer_id", "NA")
    except Exception:
        state["customer_id"] = "NA"

    return state


def deal_node(state: State):
    parsed = state["parsed_data"]

    try:
        res = requests.post("http://localhost:8002/onboard", json={
            "payload": {
                "location": parsed.get("location"),
                "budget": parsed.get("budget"),
                "type": parsed.get("property_type")
            }
        }).json()

        state["property_id"] = res.get("data", {}).get("property_id", "N/A")

    except Exception as e:
        state["property_id"] = "FAILED"
        logging.error(str(e))

    return state

def marketing_node(state: State):
    try:
        results = collection.query(query_texts=["Bangalore property"], n_results=1)
        # state["insights"] = str(results)
        state["insights"] = "Market: Stable | Demand: High | ROI: Good"
    except Exception:
        state["insights"] = "No insights available"
    return state

def final_node(state: State):
    return {
        "summary": f"""
        Customer ID: {state['customer_id']}
        Property ID: {state['property_id']}
        Insights: {state['insights']}
        """,
        "raw": state
    }


# ---------- GRAPH ----------
graph = StateGraph(State)

graph.add_node("parse", parse_node)
graph.add_node("customer", customer_node)
graph.add_node("deal", deal_node)
graph.add_node("marketing", marketing_node)
graph.add_node("final", final_node)

graph.set_entry_point("parse")

graph.add_edge("parse", "customer")
graph.add_edge("customer", "deal")
graph.add_edge("deal", "marketing")
graph.add_edge("marketing", "final")

workflow = graph.compile()

# ---------- API ----------
@app.post("/query")
def query(req: dict):
    try:
        state = {
            "user_query": req.get("query"),
            "parsed_data": {},
            "customer_id": "",
            "property_id": "",
            "insights": ""
        }

        result = workflow.invoke(state)

        logging.info("Workflow completed")
        return result

    except Exception as e:
        logging.exception("ERROR OCCURRED")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
