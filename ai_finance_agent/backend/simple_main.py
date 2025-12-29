#!/usr/bin/env python3
"""
Simplified FastAPI backend for AI Finance Agent with better error handling
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys

def load_env_file():
    """Load environment variables from .env file"""
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("✓ Loaded environment variables from .env file")
            return True
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
    return False

# Load .env file at startup
load_env_file()

app = FastAPI(title="AI Finance Agent API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store agent team
agent_team = None

class QueryRequest(BaseModel):
    message: str
    agent_type: Optional[str] = "team"

class QueryResponse(BaseModel):
    response: str
    agent_used: str

def initialize_agents():
    """Initialize the agent team with proper error handling"""
    global agent_team
    
    try:
        # Check if GROQ API key is set
        if not os.getenv("GROQ_API_KEY"):
            print("Warning: GROQ_API_KEY not set. Agent functionality will be limited.")
            return False
            
        # Import and initialize agents
        from agno.agent import Agent
        from agno.team import Team
        from agno.models.groq import Groq
        from agno.db.sqlite import SqliteDb
        from agno.tools.duckduckgo import DuckDuckGoTools
        from agno.tools.yfinance import YFinanceTools
        
        # Setup database
        db = SqliteDb(db_file="agents.db")
        
        # Initialize GROQ model - Using Llama 3.1 8B Instant (fast and accurate)
        groq_model = Groq(
            id="llama-3.1-8b-instant",  # Fast, production-ready model
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Create agents
        web_agent = Agent(
            name="Web Agent",
            role="Search the web for information",
            model=groq_model,
            tools=[DuckDuckGoTools()],
            db=db,
            add_history_to_context=True,
            markdown=True,
        )
        
        finance_agent = Agent(
            name="Finance Agent",
            role="Get financial data",
            model=groq_model,
            tools=[YFinanceTools()],
            instructions=["Always use tables to display data"],
            db=db,
            add_history_to_context=True,
            markdown=True,
        )
        
        agent_team = Team(
            name="Agent Team (Web+Finance)",
            model=groq_model,
            members=[web_agent, finance_agent],
            debug_mode=True,
            markdown=True,
        )
        
        print("✅ Agents initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup"""
    initialize_agents()

@app.get("/")
async def root():
    return {
        "message": "AI Finance Agent API is running with GROQ",
        "status": "online",
        "agents_initialized": agent_team is not None
    }

@app.get("/health")
async def health_check():
    groq_key = os.getenv("GROQ_API_KEY")
    return {
        "status": "healthy",
        "groq_configured": bool(groq_key),
        "agents_ready": agent_team is not None,
        "message": "Set GROQ_API_KEY environment variable" if not groq_key else "GROQ API configured"
    }

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        # Check if agents are initialized
        if not agent_team:
            # Try to initialize agents
            if not initialize_agents():
                raise HTTPException(
                    status_code=500,
                    detail="Agents not initialized. Please check GROQ_API_KEY and dependencies."
                )
        
        # Check if GROQ API key is set
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GROQ_API_KEY environment variable not set. Get your free key from console.groq.com"
            )
        
        # Process the query
        response = agent_team.run(request.message)
        
        return QueryResponse(
            response=response.content if hasattr(response, 'content') else str(response),
            agent_used="team"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/agents")
async def get_agents():
    return {
        "agents": [
            {
                "name": "Web Agent",
                "role": "Search the web for information",
                "tools": ["DuckDuckGo Search"],
                "model": "GROQ Llama-3.1-8B-Instant",
                "status": "ready" if agent_team else "not initialized"
            },
            {
                "name": "Finance Agent",
                "role": "Get financial data",
                "tools": ["YFinance - Stock prices, analyst recommendations, company info, news"],
                "model": "GROQ Llama-3.1-8B-Instant",
                "status": "ready" if agent_team else "not initialized"
            },
            {
                "name": "Agent Team",
                "role": "Coordinate between web and finance agents",
                "tools": ["Combined web search and financial analysis"],
                "model": "GROQ Llama-3.1-8B-Instant",
                "status": "ready" if agent_team else "not initialized"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting AI Finance Agent API...")
    print("Loading environment variables...")
    uvicorn.run(app, host="0.0.0.0", port=8000)