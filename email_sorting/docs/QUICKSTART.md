# Quick Start Guide

Get your AI email sorting agent up and running in minutes!

## Installation

### 1. Navigate to Project

```bash
cd email_sorting
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy environment template
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# Edit .env file
notepad .env  # Windows
nano .env     # Mac/Linux
```

**Required settings:**
```env
# Choose your LLM provider
LLM_PROVIDER=openai

# Add your API key
OPENAI_API_KEY=sk-your-key-here

# Email provider
EMAIL_PROVIDER=gmail
```

### 5. Setup Gmail Access

Follow the [Gmail Setup Guide](GMAIL_SETUP.md) to:
1. Create Google Cloud project
2. Enable Gmail API
3. Download OAuth credentials
4. Authenticate

**Quick version:**
```bash
# After placing credentials.json in project root
python main.py setup --provider gmail
```

## Usage

### Test the System

```bash
# Run with sample email
python main.py test
```

**Expected output:**
```
Category: Work
Priority: 8.5/10
Intent: REQUEST_ACTION
Confidence: 92%
Actions: apply_label:work, apply_label:urgent, mark_important
```

### Process Real Emails

```bash
# Process 10 emails
python main.py process --batch-size 10

# Dry run (preview only)
python main.py process --dry-run
```

### View Statistics

```bash
python main.py stats --days 7
```

### Visualize Workflow

```bash
python main.py visualize
```

## Understanding the Output

When processing emails, you'll see:

```
Email 1/10
From: boss@company.com
Subject: URGENT: Project deadline tomorrow
  Category: Work
  Priority: 8.5/10
  Confidence: 92%
  Status: executed

✓ Executing 4 actions on email msg-123...
  ✓ apply_label:work
  ✓ apply_label:urgent
  ✓ mark_important
  ✓ apply_label:action_required
```

## Categories

The agent classifies emails into:
- **Work** - Professional emails, projects, meetings
- **Personal** - Family, friends, personal matters
- **Promotions** - Marketing, deals, newsletters
- **Social** - Social media, forums, notifications
- **Transactional** - Receipts, confirmations, shipping
- **Spam** - Unwanted emails

## Actions

The agent can:
- Apply labels/tags
- Mark as important (star)
- Archive emails
- Move to spam
- Mark for follow-up

## Human Review

For low-confidence classifications (< 80%), the agent will ask for your input:

```
Low Confidence Classification - Please Review

From: unknown@example.com
Subject: Interesting opportunity

AI Suggestion:
  Category: Promotions
  Confidence: 65%

Accept AI classification? [Y/n]:
```

You can:
- Press `Y` to accept
- Press `N` to correct
- The agent learns from your corrections!

## Tips

### First Time Use

1. Start with a small batch: `--batch-size 5`
2. Use dry-run mode first: `--dry-run`
3. Review the classifications
4. Adjust confidence threshold in `.env` if needed

### Improving Accuracy

The agent improves over time by:
- Learning from your corrections
- Building sender reputation
- Remembering similar emails

### Customization

Edit `.env` to customize:
```env
# Lower for more human review, higher for more automation
CONFIDENCE_THRESHOLD=0.8

# Number of emails to process at once
BATCH_SIZE=10

# Enable/disable features
ENABLE_HUMAN_REVIEW=true
ENABLE_LEARNING=true
```

## Troubleshooting

### "No unread emails found"
- Check your Gmail inbox
- The agent only processes unread emails
- Mark some emails as unread to test

### "Authentication failed"
- Run `python main.py setup --provider gmail` again
- Delete `token.pickle` and re-authenticate

### "LLM API error"
- Check your API key in `.env`
- Verify you have API credits
- Check your internet connection

### Low accuracy
- Process more emails to build history
- Provide corrections when prompted
- Check that categories match your needs

## Next Steps

1. **Process your inbox**: Start with recent emails
2. **Provide feedback**: Correct misclassifications
3. **Monitor results**: Use `stats` command
4. **Adjust settings**: Tune confidence threshold
5. **Automate**: Set up scheduled runs (coming soon)

## Getting Help

- Check [README.md](../README.md) for architecture details
- Review [implementation_plan.md](../../.gemini/antigravity/brain/07cbf330-d89b-4176-bce3-9b376a84bca0/implementation_plan.md) for technical details
- Open an issue on GitHub

## What's Next?

Future features:
- [ ] Scheduled automatic processing
- [ ] Web dashboard
- [ ] Mobile app
- [ ] Team collaboration
- [ ] Custom categories
- [ ] Auto-responses

Happy email sorting! 📧✨
