# WhatsApp Appointment Automation Agent

A fully automated WhatsApp bot that handles appointment bookings from start to finish using LangGraph and Google Gemini.

## Features

✅ **Instant Message Response** - Automatically replies to WhatsApp messages  
✅ **Smart Booking** - Collects client details and checks availability  
✅ **Automatic Reminders** - Sends reminders 2 hours and 1 hour before appointments  
✅ **Cancellation Handling** - Smoothly processes appointment cancellations  
✅ **Lead Management** - Captures and stores client information without duplicates  
✅ **FAQ Support** - Answers business-related questions using AI  

## Architecture

- **LangGraph**: Orchestrates the conversation flow with intent detection and routing
- **Google Gemini**: Powers natural language understanding and response generation
- **FastAPI**: Handles WhatsApp Cloud API webhooks
- **SQLModel**: Manages database operations for leads and appointments
- **APScheduler**: Runs background jobs for sending reminders

## Setup

### 1. Install Dependencies

```bash
cd whatsapp_appointment_agent
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `WHATSAPP_API_TOKEN`: Your WhatsApp Cloud API access token
- `WHATSAPP_PHONE_NUMBER_ID`: Your WhatsApp Business phone number ID
- `GEMINI_API_KEY`: Your Google Gemini API key

### 3. Set Up WhatsApp Cloud API

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app and add WhatsApp product
3. Get your access token and phone number ID
4. Configure webhook URL: `https://your-domain.com/webhook`
5. Set verify token to match `WHATSAPP_VERIFY_TOKEN` in `.env`

### 4. Run the Application

**Start the webhook server:**
```bash
python main.py
```

**Start the reminder scheduler (in a separate terminal):**
```bash
python scheduler.py
```

For production, use a process manager like `supervisor` or `systemd` to run both services.

## Usage

### Booking an Appointment

User sends:
> "Hi, I'd like to book an appointment for a haircut on January 15th at 2pm"

Bot responds with confirmation and stores the appointment.

### Cancelling an Appointment

User sends:
> "I need to cancel my appointment"

Bot finds and cancels the upcoming appointment.

### Asking Questions

User sends:
> "What are your business hours?"

Bot uses AI to provide relevant information.

## Database Schema

### Lead Table
- `id`: Primary key
- `phone_number`: Unique phone number
- `name`: Client name
- `created_at`, `updated_at`: Timestamps

### Appointment Table
- `id`: Primary key
- `lead_id`: Foreign key to Lead
- `service`: Service type
- `appointment_time`: Scheduled time
- `status`: confirmed/cancelled/completed
- `reminder_2h_sent`, `reminder_1h_sent`: Reminder tracking

## Deployment

### Using ngrok (Development)

```bash
ngrok http 8000
```

Use the ngrok URL as your webhook URL in Meta's dashboard.

### Production Deployment

1. Deploy to a cloud provider (AWS, GCP, Azure, Heroku, etc.)
2. Use PostgreSQL instead of SQLite:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```
3. Set up SSL/HTTPS for webhook security
4. Use a process manager to keep services running

## File Structure

```
whatsapp_appointment_agent/
├── main.py              # FastAPI webhook server
├── agent.py             # LangGraph workflow
├── models.py            # Database models
├── database.py          # Database utilities
├── config.py            # Configuration management
├── whatsapp_utils.py    # WhatsApp API wrapper
├── scheduler.py         # Reminder scheduler
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

## Customization

### Business Hours
Edit in `.env`:
```
BUSINESS_HOURS_START=9
BUSINESS_HOURS_END=18
```

### Reminder Messages
Modify the message templates in `scheduler.py`.

### Intent Detection
Adjust the prompts in `agent.py` to customize how the bot understands user messages.

## Troubleshooting

**Webhook not receiving messages:**
- Verify webhook URL is publicly accessible
- Check verify token matches in both Meta dashboard and `.env`
- Review webhook logs in Meta's dashboard

**Reminders not sending:**
- Ensure `scheduler.py` is running
- Check database for `reminder_*_sent` flags
- Verify WhatsApp API credentials

**Database errors:**
- Run `init_db()` to create tables
- Check `DATABASE_URL` format

## License

MIT License - feel free to use and modify for your projects.
