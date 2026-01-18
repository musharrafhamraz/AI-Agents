# Validata - AI-Native Survey & Insights Platform

<div align="center">

![Status](https://img.shields.io/badge/status-production--ready-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Next.js](https://img.shields.io/badge/next.js-14-black)
![License](https://img.shields.io/badge/license-MIT-green)

**AI-powered survey platform with 7-Layer Reasoning Engine for hallucination detection**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Deployment](#-deployment)

</div>

---

## 🎯 Overview

Validata is a production-ready AI-Native Survey & Insights Platform built on Model Context Protocol (MCP) architecture. It combines intelligent survey creation, multi-layer response validation, and AI-powered analytics to deliver trustworthy insights from survey data.

### Key Innovation: 7-Layer Reasoning Engine

The platform's core innovation is a sophisticated validation system that uses adversarial AI agents to detect and eliminate hallucinations in survey responses, ensuring data quality and reliability.

---

## ✨ Features

### 🎯 AI-Assisted Survey Creation
- Generate context-aware questions using GPT-4
- Pre-built templates for common use cases
- Multiple question types (text, multiple choice, rating, conditional)
- Integration with account memory for personalization

### ✓ 7-Layer Validation System
1. **Syntax Layer** - Format and structure validation
2. **Semantic Layer** - Meaning and coherence checking
3. **Consistency Layer** - Internal consistency verification
4. **Context Layer** - Survey context and memory validation
5. **Adversarial Layer** - Counter-argument challenges
6. **Hallucination Layer** - Fabricated claim detection
7. **Confidence Layer** - Aggregate confidence scoring

### 📊 AI-Powered Analytics
- Automated insight generation from validated responses
- Pattern detection across survey data
- Full traceability from insights to source data
- Historical context integration

### 🔄 Multi-Channel Data Collection
- Form-based collection (web UI)
- Chat-based collection (conversational)
- API-based collection (programmatic)
- Metadata tracking for all channels

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis
- Pinecone account
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/validata.git
cd validata

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Start infrastructure
docker-compose up -d

# Initialize database
python scripts/setup_db.py
alembic upgrade head
python scripts/seed_data.py  # Optional: Add sample data

# Start all services
python scripts/start_all.py
```

### Access the Platform

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📚 Documentation

### Core Documentation
- **[README_COMPLETE.md](README_COMPLETE.md)** - Comprehensive setup and usage guide
- **[FRONTEND_COMPLETE.md](FRONTEND_COMPLETE.md)** - Frontend implementation details
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[FINAL_IMPLEMENTATION_SUMMARY.md](FINAL_IMPLEMENTATION_SUMMARY.md)** - Complete implementation overview

### Specification Documents
- **[Requirements](.kiro/specs/validata-platform/requirements.md)** - EARS-compliant requirements
- **[Design](.kiro/specs/validata-platform/design.md)** - Architecture and design decisions
- **[Tasks](.kiro/specs/validata-platform/tasks.md)** - Implementation task breakdown

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐
│  Next.js        │
│  Frontend       │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│  FastAPI        │
│  Backend        │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│LangGraph│ │   MCP   │
│Agents   │ │ Servers │
└─────────┘ └────┬────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │Postgres│ │ Redis  │ │Pinecone│
    └────────┘ └────────┘ └────────┘
```

### Components

**Backend (Python)**
- 4 MCP Servers (Memory, Survey, Validation, Analytics)
- 3 LangGraph Orchestrators
- FastAPI REST API (16 endpoints)
- PostgreSQL database with Alembic migrations
- Vector database integration (Pinecone)
- JWT authentication

**Frontend (TypeScript/React)**
- Next.js 14 with App Router
- 6 React components
- 6 pages covering all user flows
- Tailwind CSS styling
- TypeScript type safety

**Infrastructure**
- Docker Compose for local development
- Database setup and seeding scripts
- Automated startup script
- Configuration management

---

## 📊 API Endpoints

### Surveys
```
POST   /api/surveys              Create survey
GET    /api/surveys/{id}         Get survey details
PUT    /api/surveys/{id}         Update survey
DELETE /api/surveys/{id}         Delete survey
GET    /api/surveys              List all surveys
GET    /api/surveys/templates/   Get templates
```

### Responses
```
POST   /api/responses/                    Submit response
GET    /api/responses/{id}                Get response
GET    /api/responses/survey/{survey_id}  List responses
```

### Validation
```
GET    /api/validation/{response_id}              Get validation status
POST   /api/validation/{response_id}/revalidate   Revalidate response
```

### Analytics
```
GET    /api/analytics/{survey_id}/insights        Get insights
POST   /api/analytics/{survey_id}/insights        Generate insights
GET    /api/analytics/{survey_id}/patterns        Get patterns
GET    /api/analytics/insights/{insight_id}/trace Get traceability
```

Full API documentation available at `/docs` when running.

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **Cache**: Redis
- **Vector DB**: Pinecone
- **AI**: OpenAI GPT-4
- **Orchestration**: LangGraph
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Auth**: JWT (python-jose)

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Hooks
- **HTTP Client**: Fetch API

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx (production)

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# Specific test suites
pytest tests/mcp_servers/
pytest tests/agents/
pytest tests/integration/

# With coverage
pytest --cov=validata --cov-report=html
```

### Test Structure
- Unit tests for MCP servers and tools
- Integration tests for workflows
- Property-based tests for data models
- End-to-end tests for user flows

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build images
docker build -t validata-backend -f Dockerfile.backend .
docker build -t validata-frontend -f frontend/Dockerfile ./frontend

# Run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment

**AWS**: ECS/Fargate + RDS + ElastiCache  
**GCP**: Cloud Run + Cloud SQL + Memorystore  
**Azure**: Container Instances + Azure Database + Azure Cache

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)
- CORS configuration
- Environment variable management
- Rate limiting (production)

---

## 📈 Performance

- Async/await for I/O operations
- Database connection pooling
- Redis caching for frequent queries
- Vector database for semantic search
- Optimized database indexes
- Next.js image optimization
- Code splitting and lazy loading

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint/Prettier for TypeScript/React
- Write tests for new features
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [OpenAI](https://openai.com/) - AI models
- [Pinecone](https://www.pinecone.io/) - Vector database
- [PostgreSQL](https://www.postgresql.org/) - Relational database

---

## 📞 Support

- **Documentation**: See docs in this repository
- **Issues**: Open an issue on GitHub
- **Email**: support@validata.example.com

---

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Real-time collaboration
- [ ] Advanced analytics visualizations
- [ ] Export to CSV/PDF
- [ ] Email notifications
- [ ] Survey scheduling

### Version 1.2 (Planned)
- [ ] Multi-language support
- [ ] Custom branding
- [ ] Advanced conditional logic
- [ ] Integration with third-party tools
- [ ] Mobile app

---

## 📊 Project Stats

- **Total Lines of Code**: ~8,000+
- **Backend Files**: 35+
- **Frontend Files**: 15+
- **API Endpoints**: 16
- **MCP Servers**: 4
- **Validation Layers**: 7
- **Test Files**: 4+

---

<div align="center">

**Built with ❤️ using spec-driven development**

[⬆ Back to Top](#validata---ai-native-survey--insights-platform)

</div>
