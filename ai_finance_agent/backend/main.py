from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys

# Add the current directory to the path for importing the GROQ agent
sys.path.append(os.path.dirname(__file__))

from finance_agent_groq import agent_team

app = FastAPI(title="AI Finance Agent API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    message: str
    agent_type: Optional[str] = "team"  # "team", "web", or "finance"

class QueryResponse(BaseModel):
    response: str
    agent_used: str

@app.get("/")
async def root():
    return {"message": "AI Finance Agent API is running with GROQ"}

@app.get("/health")
async def health_check():
    groq_key = os.getenv("GROQ_API_KEY")
    return {
        "status": "healthy",
        "groq_configured": bool(groq_key),
        "message": "Set GROQ_API_KEY environment variable" if not groq_key else "GROQ API configured"
    }

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        # Check if GROQ API key is set
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="GROQ_API_KEY environment variable not set. Please set it to use the AI agents."
            )
        
        # Use the agent team to process the query
        response = agent_team.run(request.message)
        
        return QueryResponse(
            response=response.content if hasattr(response, 'content') else str(response),
            agent_used="team"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/agents")
async def get_agents():
    return {
        "agents": [
            {
                "name": "Web Agent",
                "role": "Search the web for information",
                "tools": ["DuckDuckGo Search"],
                "model": "llama-3.3-70b-versatile"
            },
            {
                "name": "Finance Agent", 
                "role": "Get financial data",
                "tools": ["YFinance - Stock prices, analyst recommendations, company info, news"],
                "model": "llama-3.3-70b-versatile"
            },
            {
                "name": "Agent Team",
                "role": "Coordinate between web and finance agents",
                "tools": ["Combined web search and financial analysis"],
                "model": "llama-3.3-70b-versatile"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)