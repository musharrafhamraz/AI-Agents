from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import public, admin
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="DJ Automation Scheduler API",
    description="API for managing DJ mixes and scheduling playback",
    version="1.0.0"
)

# CORS Configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup_event():
    init_db()
    print("Database initialized")

# Include routers
app.include_router(public.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "message": "DJ Automation Scheduler API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
