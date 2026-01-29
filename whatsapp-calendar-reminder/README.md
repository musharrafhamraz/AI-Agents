# WhatsApp Calendar Reminder System

An automated system that sends WhatsApp reminders 24 hours before Google Calendar events using WhatsApp Business API.

## Features

- ✅ **Google Calendar Integration**: Automatic sync with Google Calendar using OAuth 2.0
- ✅ **WhatsApp Business API**: Send template-based reminders via WhatsApp
- ✅ **24-Hour Advance Reminders**: Configurable reminder timing
- ✅ **Reliable Scheduling**: Celery-based task queue with retry logic
- ✅ **Message Logging**: Complete audit trail of all sent messages
- ✅ **Per-Event Control**: Enable/disable reminders for specific events
- ✅ **REST API**: Full API for management and monitoring
- ✅ **Docker Support**: Easy deployment with Docker Compose

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│ Google Calendar │◄────────┤  Calendar Sync   │
└─────────────────┘         │     Service      │
                            └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   PostgreSQL     │
                            │    Database      │
                            └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │ Reminder Engine  │
                            │  (Celery Tasks)  │
                            └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │ WhatsApp Business│
                            │       API        │
                            └──────────────────┘
```

## Prerequisites

### Required
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Google Cloud account with Calendar API enabled
- WhatsApp Business API access (Meta Business Manager)

### API Setup Required
1. **Google Calendar API**
   - Create project in Google Cloud Console
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Download credentials JSON

2. **WhatsApp Business API**
   - Facebook Business Manager account
   - WhatsApp Business API access
   - Approved message templates
   - Phone number verification

## Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whatsapp-calendar-reminder
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**
   ```bash
   docker-compose exec api python -c "from src.database import init_db; init_db()"
   ```

5. **Authenticate with Google**
   ```bash
   docker-compose exec api python -c "from src.integrations.google_calendar import GoogleCalendarClient; client = GoogleCalendarClient(); client.authenticate()"
   ```

### Option 2: Local Development

1. **Install Poetry**
   ```bash
   pip install poetry
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Set up PostgreSQL and Redis**
   ```bash
   # Install and start PostgreSQL
   # Install and start Redis
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Initialize database**
   ```bash
   poetry run python -c "from src.database import init_db; init_db()"
   ```

6. **Run services**
   ```bash
   # Terminal 1: API
   poetry run uvicorn src.api.main:app --reload

   # Terminal 2: Celery Worker
   poetry run celery -A src.celery_app worker --loglevel=info

   # Terminal 3: Celery Beat
   poetry run celery -A src.celery_app beat --loglevel=info
   ```

## Configuration

### Environment Variables

See `.env.example` for all configuration options. Key settings:

```env
# Google Calendar
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
GOOGLE_CALENDAR_ID=primary

# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-id

# User Settings
USER_EMAIL=your-email@example.com
USER_PHONE_NUMBER=+1234567890
USER_TIMEZONE=America/New_York

# Reminder Settings
DEFAULT_REMINDER_HOURS=24
SYNC_INTERVAL_MINUTES=15
```

## Usage

### API Endpoints

**Health & Status**
- `GET /health` - Health check
- `GET /status` - System status

**Calendar Management**
- `POST /sync` - Trigger manual sync
- `GET /events` - List upcoming events
- `GET /events/{id}` - Get event details

**Reminder Management**
- `GET /reminders` - List reminders
- `PUT /events/{id}/reminder` - Toggle reminder
- `POST /reminders/test` - Send test reminder

**Logs & Stats**
- `GET /logs` - Query message logs
- `GET /stats` - Delivery statistics

**User Preferences**
- `GET /preferences` - Get preferences
- `PUT /preferences` - Update preferences

### Example API Calls

```bash
# Check system status
curl http://localhost:8000/status

# Trigger calendar sync
curl -X POST http://localhost:8000/sync

# Send test reminder
curl -X POST http://localhost:8000/reminders/test

# List upcoming events
curl http://localhost:8000/events

# Disable reminder for an event
curl -X PUT http://localhost:8000/events/{event_id}/reminder?enabled=false
```

## WhatsApp Template Setup

You need to create and get approval for message templates in Meta Business Manager:

**Example Template Name**: `event_reminder_24h`

**Template Content**:
```
Hi! This is a reminder for your upcoming event:

📅 *{{1}}*
🕐 {{2}}
📍 {{3}}

See you there!
```

**Parameters**:
1. Event title
2. Event time
3. Event location

## Monitoring

### Logs

View logs for each service:

```bash
# API logs
docker-compose logs -f api

# Worker logs
docker-compose logs -f celery-worker

# Beat logs
docker-compose logs -f celery-beat
```

### Statistics

Access statistics via API:

```bash
curl http://localhost:8000/stats
```

## Troubleshooting

### Google Authentication Issues

If you get authentication errors:

1. Delete `token.pickle`
2. Re-run authentication:
   ```bash
   docker-compose exec api python -c "from src.integrations.google_calendar import GoogleCalendarClient; client = GoogleCalendarClient(); client.authenticate()"
   ```

### WhatsApp Message Failures

Common issues:
- Template not approved
- Phone number format incorrect (must include country code with +)
- Access token expired
- Rate limits exceeded

Check logs in `/logs` endpoint for detailed error messages.

### Database Connection Issues

Ensure PostgreSQL is running and credentials are correct:

```bash
# Test connection
docker-compose exec postgres psql -U reminder_user -d whatsapp_reminder
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black src/
poetry run ruff check src/
```

### Database Migrations

```bash
# Create migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head
```

## Production Deployment

### Recommendations

1. **Use managed services**
   - Managed PostgreSQL (AWS RDS, Google Cloud SQL)
   - Managed Redis (AWS ElastiCache, Redis Cloud)

2. **Security**
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
   - Enable HTTPS with SSL certificates
   - Implement rate limiting
   - Use firewall rules

3. **Monitoring**
   - Set up application monitoring (Datadog, New Relic)
   - Configure alerts for failures
   - Monitor API response times
   - Track message delivery rates

4. **Scaling**
   - Run multiple Celery workers
   - Use load balancer for API
   - Implement database connection pooling

## License

MIT License

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review API documentation at `/docs`

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
