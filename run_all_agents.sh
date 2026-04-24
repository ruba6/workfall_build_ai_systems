echo "Starting all agents..."

# Kill old processes (important)
fuser -k 8001/tcp
fuser -k 8002/tcp
fuser -k 8003/tcp
fuser -k 8000/tcp

uvicorn customer_agent.app_customer:app --port 8001 &
uvicorn deal_agent.app_deal:app --port 8002 &
uvicorn marketing_agent.app_market:app --port 8003 &
uvicorn concierge_agent.app_concierge:app --port 8000 &


echo "All agents started!"

wait