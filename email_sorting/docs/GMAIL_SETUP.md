# Gmail OAuth2 Setup Guide

This guide will help you set up Gmail API access for the email sorting agent.

## Prerequisites

- Google account with Gmail
- Python 3.10+ installed
- Project dependencies installed

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Enter project name: `Email Sorting Agent`
4. Click "Create"

## Step 2: Enable Gmail API

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: External
   - App name: Email Sorting Agent
   - User support email: your email
   - Developer contact: your email
   - Click "Save and Continue"
   - Scopes: Skip for now
   - Test users: Add your Gmail address
   - Click "Save and Continue"

4. Back to "Create OAuth client ID":
   - Application type: **Desktop app**
   - Name: Email Sorting Agent
   - Click "Create"

5. Download the credentials:
   - Click the download icon (⬇️) next to your OAuth 2.0 Client ID
   - Save as `credentials.json` in the project root directory

## Step 4: Project Structure

Your project should look like this:

```
email_sorting/
├── credentials.json          ← Place downloaded file here
├── src/
├── data/
├── requirements.txt
└── main.py
```

## Step 5: Run Setup

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Run setup command
python main.py setup --provider gmail
```

This will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request permissions for Gmail access
4. Save authentication token to `token.pickle`

## Step 6: Test the System

```bash
# Test with sample email
python main.py test

# Process real emails
python main.py process --batch-size 5
```

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the OAuth credentials
- Place it in the project root (same directory as main.py)

### "Access blocked: This app's request is invalid"
- Make sure you selected "Desktop app" not "Web application"
- Try creating new credentials

### "The app is not verified"
- This is normal for personal projects
- Click "Advanced" → "Go to Email Sorting Agent (unsafe)"
- This is safe because it's your own app

### "Token has been expired or revoked"
- Delete `token.pickle`
- Run `python main.py setup --provider gmail` again

## Security Notes

- `credentials.json` contains your OAuth client ID and secret
- `token.pickle` contains your access token
- Both files are in `.gitignore` - never commit them
- Keep these files secure

## Scopes Requested

The app requests these Gmail permissions:
- `gmail.readonly` - Read emails
- `gmail.modify` - Modify labels and flags
- `gmail.labels` - Create and manage labels

## Next Steps

Once setup is complete, you can:
- Process emails: `python main.py process`
- View stats: `python main.py stats`
- Visualize workflow: `python main.py visualize`
