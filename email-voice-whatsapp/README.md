# Email to WhatsApp Summary System

An intelligent automated system that monitors your Gmail inbox, identifies important emails using AI, generates concise summaries, and delivers them directly to your WhatsApp as text messages.

## ✨ Features

- 🔄 **Automated Email Monitoring** - Periodic checking (hourly/daily/custom)
- 🤖 **AI-Powered Analysis** - Smart importance classification and summarization using Groq
- 📱 **WhatsApp Delivery** - Direct text message delivery via Twilio
- ⚙️ **Customizable** - Flexible filters and preferences
- 🔒 **Secure** - OAuth2 Gmail authentication
- 📊 **REST API** - Full API for management and monitoring
- ⏰ **Scheduled Tasks** - Automated background processing with Celery

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Redis** - [Installation Guide](https://redis.io/docs/getting-started/installation/)
- **Gmail Account** - For email monitoring
- **Groq API Key** - [Get Free Key](https://console.groq.com/)
- **Twilio Account** - [Sign Up](https://www.twilio.com/try-twilio)

### Installation (Windows)

```bash
# 1. Navigate to project
cd email-voice-whatsapp

# 2. Run installation script
install.bat

# 3. Edit .env with your API keys
notepad .env

# 4. Start Redis (in separate terminal)
redis-server

# 5. Start all services
start_all.bat
```

### Installation (Mac/Linux)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# 4. Initialize database
python setup.py

# 5. Start services (4 separate terminals)
redis-server                    # Terminal 1
python run.py                   # Terminal 2
python start_celery_worker.py   # Terminal 3
python start_celery_beat.py     # Terminal 4
```

### Access Points

- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## ⚙️ Configuration

### Required API Keys

1. **Gmail API** - [Setup Guide](https://console.cloud.google.com/)
   - Create project and enable Gmail API
   - Create OAuth 2.0 credentials
   - Add redirect URI: `http://localhost:8000/api/auth/gmail/callback`

2. **Groq API** - [Get Key](https://console.groq.com/)
   - Sign up for free account
   - Create API key
   - Free tier includes generous limits

3. **Twilio WhatsApp** - [Setup Guide](https://www.twilio.com/)
   - Sign up for account
   - Get WhatsApp sandbox number (for testing)
   - Copy Account SID and Auth Token

### Environment Variables (.env)

```env
# Gmail API
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret

# Groq AI
GROQ_API_KEY=gsk_your_groq_api_key
GROQ_MODEL=mixtral-8x7b-32768

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Settings
DEFAULT_IMPORTANCE_THRESHOLD=7
MAX_EMAILS_PER_CHECK=10
```

### User Preferences

Configure via API:

```bash
curl -X PUT "http://localhost:8000/api/users/1/preferences" \
  -H "Content-Type: application/json" \
  -d '{
    "importance_threshold": 8,
    "check_frequency": "hourly",
    "phone_number": "whatsapp:+1234567890"
  }'
```

Options:
- `importance_threshold`: 1-10 (emails with score >= threshold are sent)
- `check_frequency`: "hourly" or "daily"
- `phone_number`: WhatsApp number with country code

## 📖 Usage

### 1. Register User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"your@gmail.com","phone_number":"whatsapp:+1234567890"}'
```

### 2. Connect Gmail

```bash
curl "http://localhost:8000/api/auth/gmail/connect/1"
```

Visit the `authorization_url` in response to authorize Gmail access.

### 3. Trigger Email Check

```bash
curl -X POST "http://localhost:8000/api/emails/check/1"
```

### 4. View History

```bash
# Processed emails
curl "http://localhost:8000/api/emails/history/1"

# WhatsApp messages
curl "http://localhost:8000/api/emails/messages/1"

# Statistics
curl "http://localhost:8000/api/emails/stats/1"
```

## 📁 Project Structure

```
email-voice-whatsapp/
├── src/
│   ├── api/
│   │   ├── main.py                    # FastAPI application
│   │   └── routes/
│   │       ├── auth.py                # Authentication endpoints
│   │       ├── users.py               # User management
│   │       └── emails.py              # Email operations
│   ├── models/
│   │   ├── user.py                    # User model
│   │   ├── email.py                   # ProcessedEmail model
│   │   └── message.py                 # WhatsAppMessage model
│   ├── services/
│   │   ├── email_monitor.py           # Gmail integration
│   │   ├── ai_analyzer.py             # Groq AI service
│   │   └── whatsapp_service.py        # Twilio WhatsApp
│   ├── tasks/
│   │   ├── celery_app.py              # Celery configuration
│   │   └── email_tasks.py             # Background tasks
│   ├── config/
│   │   └── settings.py                # Configuration
│   └── database.py                    # Database setup
├── data/                              # SQLite database
├── requirements.txt                   # Dependencies
├── .env.example                       # Environment template
├── run.py                             # Start API server
├── setup.py                           # Initialize database
├── test_services.py                   # Test script
├── start_celery_worker.py             # Start Celery worker
├── start_celery_beat.py               # Start Celery beat
├── install.bat                        # Windows installer
├── start_all.bat                      # Windows startup script
├── QUICKSTART.md                      # Quick start guide
└── SETUP_INSTRUCTIONS.md              # Detailed setup
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Detailed setup guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Implementation details
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (when running)

## 🧪 Testing

### Test Services

```bash
python test_services.py
```

This verifies:
- Groq AI connection and analysis
- WhatsApp message formatting
- Configuration is correct

### Manual Testing

1. Register a user
2. Connect Gmail account
3. Trigger email check
4. Verify WhatsApp message received
5. Check history and statistics via API

## 🔄 How It Works

1. **Scheduled Check**: Celery Beat triggers email check every hour (configurable)
2. **Fetch Emails**: Gmail API retrieves unread emails
3. **AI Analysis**: Groq AI classifies importance (1-10) and generates summaries
4. **Filter**: Only emails meeting importance threshold are processed
5. **Format**: Summaries are formatted into a WhatsApp message
6. **WhatsApp Delivery**: Text message sent via Twilio
7. **Logging**: All activities logged in database for tracking

### Example WhatsApp Message

```
📧 Email Summary (2 important emails)

*1. boss@company.com*
Subject: Urgent: Project Deadline
Priority: 🔴 9/10
Your boss needs the Q4 report completed by tomorrow EOD. 
The client is waiting for final numbers.
──────────────────────────────────

*2. client@example.com*
Subject: Meeting Request
Priority: 🟡 7/10
Client wants to schedule a meeting next week to discuss 
the new requirements.
──────────────────────────────────
```

## 💰 Cost Estimation

Monthly costs per user (approximate):
- **Groq API**: Free tier (generous limits) or ~$0.10-1.00
- **Twilio WhatsApp**: ~$0.005 per message (~$1-5/month)
- **Gmail API**: Free (within quota)
- **Server/Redis**: Free (local) or ~$5-10 (cloud)

**Total: ~$1-15/month** (much cheaper than original plan!)

## 🔧 Troubleshooting

### Redis Connection Error
**Solution:** Make sure Redis is running: `redis-server`

### Gmail API Error
**Solution:** 
- Check OAuth credentials in .env
- Ensure redirect URI matches exactly
- Reconnect Gmail account

### Groq API Error
**Solution:**
- Verify API key is correct
- Check you have credits available
- Ensure no extra spaces in .env

### Twilio WhatsApp Error
**Solution:**
- Verify Account SID and Auth Token
- Check phone number format: `whatsapp:+1234567890`
- For sandbox, join the sandbox first

### No Emails Being Processed
**Check:**
1. User is active and Gmail is connected
2. Celery worker and beat are running
3. Check logs for errors
4. Verify importance threshold setting

## 🔒 Security

- Gmail OAuth tokens stored securely in database
- API keys in environment variables (never committed)
- No plaintext password storage
- HTTPS recommended for production
- Rate limiting recommended for production

## 🚧 Phase 1 Limitations

This is Phase 1 implementation. The following are NOT included:
- ❌ Text-to-Speech / Voice messages (text only)
- ❌ Docker deployment
- ❌ PostgreSQL (using SQLite)
- ❌ User authentication
- ❌ Web dashboard
- ❌ Advanced email filters

## 🗺️ Roadmap (Future Phases)

### Phase 2
- [ ] Add Text-to-Speech (ElevenLabs/Google TTS)
- [ ] Voice message delivery
- [ ] Docker Compose setup
- [ ] PostgreSQL migration

### Phase 3
- [ ] Web dashboard
- [ ] User authentication
- [ ] Advanced email filters
- [ ] Multiple email providers (Outlook, Yahoo)

### Phase 4
- [ ] Mobile app
- [ ] Calendar integration
- [ ] Email response suggestions
- [ ] Telegram/Slack delivery options

## 📄 License

MIT License

## 🤝 Support

- **Documentation:** See QUICKSTART.md and SETUP_INSTRUCTIONS.md
- **API Docs:** http://localhost:8000/docs (when running)
- **Issues:** Check logs in terminal outputs

---

**Built with:** Python • FastAPI • Groq AI • Twilio • Celery • Redis

**Phase 1 Complete** ✅ - Ready for testing and deployment!
