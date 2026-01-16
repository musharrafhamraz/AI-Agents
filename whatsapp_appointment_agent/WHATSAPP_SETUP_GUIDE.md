# WhatsApp Cloud API Setup Guide

This guide will walk you through getting your WhatsApp Cloud API credentials.

## Prerequisites

- A Facebook Business Account
- A Meta Developer Account
- A phone number to use for WhatsApp Business (cannot be already registered with WhatsApp)

## Step-by-Step Setup

### 1. Create a Meta Developer Account

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **"Get Started"** in the top right
3. Log in with your Facebook account
4. Complete the registration process

### 2. Create a New App

1. Go to [Meta Apps Dashboard](https://developers.facebook.com/apps)
2. Click **"Create App"**
3. Select **"Business"** as the app type
4. Click **"Next"**
5. Fill in the app details:
   - **App Name**: Choose a name (e.g., "Appointment Bot")
   - **App Contact Email**: Your email
   - **Business Account**: Select or create one
6. Click **"Create App"**

### 3. Add WhatsApp Product

1. In your app dashboard, scroll down to **"Add products to your app"**
2. Find **"WhatsApp"** and click **"Set up"**
3. You'll be redirected to the WhatsApp setup page

### 4. Get Your Credentials

#### A. Get the Access Token (WHATSAPP_API_TOKEN)

1. In the WhatsApp setup page, look for **"Temporary access token"**
2. Click **"Copy"** to copy the token
3. **IMPORTANT**: This is a temporary token (24 hours). For production, you'll need to:
   - Go to **"System Users"** in Business Settings
   - Create a system user
   - Generate a permanent token with `whatsapp_business_messaging` permission

**For now, use the temporary token to test:**
```
WHATSAPP_API_TOKEN=your_temporary_token_here
```

#### B. Get the Phone Number ID (WHATSAPP_PHONE_NUMBER_ID)

1. On the same WhatsApp setup page, scroll to **"From"** section
2. You'll see a test phone number provided by Meta
3. Below it, you'll see **"Phone number ID"** (looks like: `123456789012345`)
4. Copy this number

```
WHATSAPP_PHONE_NUMBER_ID=123456789012345
```

#### C. Set Your Verify Token (WHATSAPP_VERIFY_TOKEN)

This can be any string you choose. It's used to verify your webhook.

```
WHATSAPP_VERIFY_TOKEN=whatsapp_verify_token_123
```

You can keep the default or change it to something more secure.

### 5. Configure Webhook (After Deploying)

Once you deploy your app (using ngrok for testing or a production server):

1. In the WhatsApp setup page, scroll to **"Configuration"**
2. Click **"Edit"** next to Webhook
3. Enter your webhook details:
   - **Callback URL**: `https://your-domain.com/webhook`
   - **Verify Token**: Same as `WHATSAPP_VERIFY_TOKEN` in your `.env`
4. Click **"Verify and Save"**
5. Subscribe to webhook fields:
   - Check **"messages"**
6. Click **"Save"**

### 6. Test Phone Number (For Development)

Meta provides a test phone number. To send messages to yourself:

1. In the WhatsApp setup page, find **"To"** section
2. Click **"Add phone number"**
3. Enter your personal WhatsApp number (with country code, no + or spaces)
4. You'll receive a verification code on WhatsApp
5. Enter the code to verify

**Note**: With the test number, you can only send messages to up to 5 verified numbers.

### 7. Production Setup (When Ready)

For production use:

#### A. Get a Permanent Access Token

1. Go to [Business Settings](https://business.facebook.com/settings)
2. Click **"System Users"** under Users
3. Click **"Add"** to create a new system user
4. Give it a name and role (Admin)
5. Click **"Add Assets"**
6. Select your app and give it full control
7. Click **"Generate New Token"**
8. Select permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
9. Copy and save this token securely

#### B. Add Your Own Phone Number

1. In WhatsApp setup, click **"Add phone number"**
2. Follow the process to verify your business phone number
3. This number cannot be registered with regular WhatsApp

#### C. Business Verification

For higher message limits and to remove test restrictions:

1. Complete Business Verification in Business Settings
2. Submit required documents
3. Wait for approval (can take several days)

## Quick Start Configuration

For testing right now, your `.env` should look like:

```env
# WhatsApp Cloud API Configuration
WHATSAPP_API_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=whatsapp_verify_token_123

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash-exp

# Database
DATABASE_URL=sqlite:///./appointments.db

# Business Configuration
BUSINESS_NAME=My Business
BUSINESS_HOURS_START=9
BUSINESS_HOURS_END=18
SLOT_DURATION_MINUTES=60
```

## Testing Locally with ngrok

1. Install ngrok: https://ngrok.com/download
2. Start your FastAPI server:
   ```bash
   python main.py
   ```
3. In another terminal, expose it:
   ```bash
   ngrok http 8000
   ```
4. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
5. Set this as your webhook URL in Meta dashboard: `https://abc123.ngrok.io/webhook`

## Troubleshooting

### "Invalid Access Token"
- Token might be expired (temporary tokens last 24 hours)
- Generate a new temporary token or create a permanent one

### "Webhook Verification Failed"
- Ensure `WHATSAPP_VERIFY_TOKEN` in `.env` matches the one in Meta dashboard
- Check that your server is running and accessible
- Verify the webhook URL is correct

### "Cannot Send Messages"
- Add recipient phone numbers in the "To" section
- Verify phone numbers with the code sent via WhatsApp
- Check that you're using the correct phone number format (no + or spaces)

### "Message Template Required"
- For the first 24 hours after a user messages you, you can send free-form messages
- After that, you need approved message templates
- For reminders, you'll need to create and get templates approved

## Next Steps

1. Get your credentials from Meta Developer Dashboard
2. Fill in the `.env` file
3. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
4. Test locally with ngrok
5. Send a test message to your bot!

## Useful Links

- [Meta Developer Dashboard](https://developers.facebook.com/apps)
- [WhatsApp Cloud API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Business Manager](https://business.facebook.com/)
- [ngrok](https://ngrok.com/)
