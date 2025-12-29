# AI Finance Agent Backend

FastAPI backend for the AI Finance Agent system using GROQ API (free alternative to OpenAI).

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get your GROQ API key (FREE):
   - Visit [GROQ Console](https://console.groq.com/)
   - Sign up for a free account
   - Get your API key from the dashboard

3. Set your GROQ API key:
```bash
# Windows
set GROQ_API_KEY=your-groq-api-key-here

# Linux/Mac
export GROQ_API_KEY=your-groq-api-key-here
```

4. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check (shows GROQ configuration status)
- `GET /agents` - List available agents
- `POST /query` - Send query to agents

## Features

- **FREE GROQ API**: Uses Llama-3.1-70B model (no cost)
- **Multi-agent system**: Web search + Financial analysis
- **Real-time data**: Stock prices, news, market analysis
- **Fast responses**: GROQ provides very fast inference

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.