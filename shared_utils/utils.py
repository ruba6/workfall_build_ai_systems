import uuid
import requests
import logging

logging.basicConfig(level=logging.INFO)

def generate_id():
    return str(uuid.uuid4())

def call_agent(url, path, payload):
    try:
        res = requests.post(url + path, json=payload)
        return res.json()
    except Exception as e:
        logging.error(f"Agent call failed: {e}")
        return None
