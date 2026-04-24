from fastapi import FastAPI
from shared_utils.com import generate_id
import json, logging


app = FastAPI()
DB_FILE = "customers.json"

@app.get("/agent-card")
def agent_card():
    return {
        "agent_name": "customer_agent",
        "capabilities": ["onboard_customer"],
        "endpoint": "http://localhost:8001"
    }

@app.post("/onboard")
def onboard_customer(req: dict):
    data = req.get("payload", {})

    if not data.get("name"):
        return {"status": "error", "error": "Name is required"}

    customer_id = generate_id()
    record = {"customer_id": customer_id, **data}

    try:
        with open(DB_FILE, "r") as f:
            db = json.load(f)
    except:
        db = []

    db.append(record)

    with open(DB_FILE, "w") as f:
        json.dump(db, f)

    logging.info(f"Customer created: {customer_id}")

    return {"status": "success", "data": {"customer_id": customer_id}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
