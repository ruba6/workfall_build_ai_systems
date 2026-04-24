from fastapi import FastAPI
from shared_utils.utils import generate_id, call_agent
import json, logging

app = FastAPI()
DB_FILE = "properties.json"
MARKETING_URL = "http://localhost:8003"

@app.get("/agent-card")
def agent_card():
    return {
        "agent_name": "deal_agent",
        "capabilities": ["onboard_property"],
        "endpoint": "http://localhost:8002"
    }

@app.post("/onboard")
def onboard_property(req: dict):
    data = req.get("payload", {})

    if not data.get("location"):
        return {"status": "error", "error": "Location required"}

    property_id = generate_id()
    record = {"property_id": property_id, **data}

    try:
        with open(DB_FILE, "r") as f:
            db = json.load(f)
    except:
        db = []

    db.append(record)

    with open(DB_FILE, "w") as f:
        json.dump(db, f)

    logging.info(f"Property created: {property_id}")

    # Auto trigger marketing agent
    call_agent(MARKETING_URL, "/analyze", {"payload": record})

    return {"status": "success", "data": {"property_id": property_id}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
