# Federated Multi-Agent Real Estate System using A2A Protocol



# Overview
This project is an AI based real estate concierge system built using a multi-agent architecture. It processes natural language queries from users and orchestrates multiple agents to:

- Extract user intent using an LLM  
- Create a customer profile  
- Register property requirements  
- Generate market insights  
- Store and retrieve data using a vector database  


# Setup Instructions

1. Clone the repository
    git clone https://github.com/ruba6/workfall_build_ai_systems
    cd workfall_task_build_ai_system

2. Create virtual environment
    python3 -m venv venv
    source venv/bin/activate

3. Install dependencies
    pip install -r requirements.txt

4. Setup environment variables
   create a file keys.env in root folder:
   GROQ_API_KEY="apikey"

5. Activate environment variables
   export $(grep -v '^#' keys.env | xargs)


# Execution Steps

Step 1: Start all agents (in separate terminals)
In terminal run command
bash run_all_agents.sh

All agent will start
Customer Agent (Port 8001)
Deal Agent (Port 8002)
Marketing Agent (Port 8003)
Orchestrator (Main API - Port 8000)


Step 2: Open Swagger UI
Go to: http://localhost:8000/docs

Step 3: Test API
Use POST /query endpoint:
{
  "query": "I want to buy a 2BHK in Bangalore under 50 lakhs"
}

# Sample Test Cases
1. Basic Buy
I want to buy a 2BHK in Bangalore under 50 lakhs

2. Rent Case
I am looking to rent a 1BHK in Chennai under 15k

3. Luxury Property
Looking to buy a villa in Hyderabad under 3 crores

4. Missing Budget
I want a 2BHK in Mumbai

5. Ambiguous Query
Should I rent or buy a flat in Pune?

6. Edge Case testing
I need a house


# Architecture Explanation

1. User Query
2. Orchestrator (Port 8000)
3. Parse Node (LLM)
4. Customer Agent (8001)
5. Deal Agent (8002)
6. Marketing Agent (8003)
7. ChromaDB (Vector Store)
