# AI Finance Agent - Complete Web Application

A complete web application featuring AI-powered financial analysis with separate backend and frontend components.

## 🏗️ Architecture

- **Backend**: FastAPI server that wraps the AI finance agent functionality
- **Frontend**: Next.js React application with a clean chat interface
- **AI Agents**: Multi-agent system with web search and financial data capabilities

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** for the backend
2. **Node.js 18+** for the frontend
3. **GROQ API Key (FREE)** - Get from [console.groq.com](https://console.groq.com/)

### Setup Instructions

1. **Clone and navigate to the project**:
```bash
git clone <your-repo>
cd ai_finance_agent
```

2. **Set up your GROQ API Key (FREE)**:
   - Visit [GROQ Console](https://console.groq.com/) and sign up for free
   - Get your API key from the dashboard
   
```bash
# Windows
set GROQ_API_KEY=your-groq-api-key-here

# Linux/Mac
export GROQ_API_KEY=your-groq-api-key-here
```

3. **Install backend dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

4. **Install frontend dependencies**:
```bash
cd ..
npm install
```

5. **Start the application**:

**Option A: Using batch files (Windows)**
```bash
# Terminal 1 - Start backend
start-backend.bat

# Terminal 2 - Start frontend  
start-frontend.bat
```

**Option B: Manual start**
```bash
# Terminal 1 - Start backend
cd backend
python main.py

# Terminal 2 - Start frontend
npm run dev
```

6. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🤖 Features

### AI Agents
- **Web Agent**: Searches the internet for financial information using DuckDuckGo
- **Finance Agent**: Retrieves real-time financial data using YFinance
- **Team Agent**: Coordinates between agents for comprehensive analysis

### Web Interface
- Clean, modern chat interface
- Real-time communication with AI agents
- Example questions to get started
- Responsive design with dark mode support

### API Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /agents` - List available agents
- `POST /query` - Send queries to AI agents

## 📁 Project Structure

```
ai_finance_agent/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend documentation
├── app/                    # Next.js frontend
│   ├── components/         # React components
│   ├── page.tsx           # Main page
│   └── globals.css        # Global styles
├── ai_finance_agent_team/  # Original agent code
│   ├── finance_agent_team.py
│   └── requirements.txt
└── package.json           # Frontend dependencies
```

## 💡 Usage Examples

Ask the AI agents questions like:
- "What's the current stock price of Apple?"
- "Analyze Tesla's recent performance"
- "What are the latest market trends?"
- "Give me analyst recommendations for Microsoft"
- "Search for recent news about cryptocurrency"

## 🔧 Development

### Backend Development
The backend is built with FastAPI and provides a REST API wrapper around the AI agents.

### Frontend Development
The frontend is built with Next.js and React, featuring:
- TypeScript for type safety
- Tailwind CSS for styling
- Real-time chat interface
- Responsive design

## 🛠️ Troubleshooting

1. **Backend not starting**: Make sure you have set the GROQ_API_KEY environment variable
2. **Frontend can't connect**: Ensure the backend is running on port 8000
3. **Dependencies issues**: Try deleting node_modules and running `npm install` again
4. **GROQ API issues**: Check your API key at [console.groq.com](https://console.groq.com/)

## 📝 License

This project is open source and available under the MIT License.
