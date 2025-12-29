from agno.agent import Agent
from agno.team import Team
from agno.models.groq import Groq
from agno.db.sqlite import SqliteDb
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
import os

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
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")

# Load environment variables
load_env_file()

# Setup database for storage
db = SqliteDb(db_file="agents.db")

# Initialize GROQ model - Using Llama 3.1 8B Instant (fast and accurate)
groq_model = Groq(
    id="llama-3.1-8b-instant",  # Fast, production-ready model
    api_key=os.getenv("GROQ_API_KEY")
)

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
    tools=[YFinanceTools()],  # Simplified initialization
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

# Don't use AgentOS for now, just export the team
if __name__ == "__main__":
    print("Finance agent team initialized successfully!")
    print("Use this module by importing agent_team")