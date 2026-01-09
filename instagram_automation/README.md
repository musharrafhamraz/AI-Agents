# Instagram Automation Agent 🤖📸

An AI-powered Instagram automation agent built with **LangGraph**, **Google Gemini**, and **Nano Banana** for intelligent content creation, image generation, and social media management.

## 🌟 Features

- **🎨 AI Content Creation**: Generate engaging captions and hashtags using Google Gemini
- **🖼️ AI Image Generation**: Create stunning visuals with Google's Nano Banana (Gemini Image) model
- **📱 Instagram Integration**: Seamless posting via Instagram Graph API
- **💬 Smart Engagement**: Automated comment responses with sentiment analysis
- **🔄 Multi-Agent Architecture**: LangGraph orchestration with specialized agents
- **🛡️ Human-in-the-Loop**: Optional review workflow for quality control

## 🏗️ Architecture

The system uses a **multi-agent architecture** with LangGraph orchestrating specialized agents:

- **Supervisor Agent**: Routes tasks to appropriate specialized agents
- **Content Creator Agent**: Generates captions and hashtags (Google Gemini)
- **Image Generator Agent**: Creates images from prompts (Nano Banana)
- **Posting Agent**: Publishes content to Instagram
- **Engagement Agent**: Handles comments and interactions

## 📋 Prerequisites

- Python 3.10+
- Instagram Business or Creator account
- Facebook Page linked to Instagram account
- Google AI API key (for both Text and Image generation)
- Instagram Graph API access

## 🚀 Deployment Options

### Option 1: Deploy to Cloud (Render.com) ☁️

Deploy to the cloud in 5 minutes! See **[RENDER_QUICKSTART.md](RENDER_QUICKSTART.md)** for step-by-step instructions.

Benefits:
- ✅ Accessible from anywhere via REST API
- ✅ No local setup required
- ✅ Free tier available
- ✅ Auto-scaling and monitoring
- ✅ HTTPS enabled by default

### Option 2: Run Locally 💻

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd instagram_posting_agent
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required configuration:
```env
# Google Gemini (Text & Image)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-pro
IMAGE_MODEL=gemini-2.5-flash-image

# Instagram Graph API
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id
FACEBOOK_PAGE_ID=your_facebook_page_id

# Brand Settings
BRAND_NAME=Your Brand Name
BRAND_VOICE=professional and friendly
TARGET_AUDIENCE=young professionals aged 25-35
```

### 3. Test Connections

```bash
python main.py test-connection
```

### 4. Create Your First Post

```bash
python main.py create-post --theme "morning coffee" --auto-publish
```

## 📖 Usage

### Create a Post

```bash
# Create post with default settings
python main.py create-post --theme "your theme"

# Customize brand voice and audience
python main.py create-post \
  --theme "fitness motivation" \
  --brand-voice "energetic and inspiring" \
  --audience "fitness enthusiasts"

# Auto-publish without review
python main.py create-post --theme "product launch" --auto-publish
```

### Process Comments

```bash
# Process comments on a post
python main.py process-comments --media-id YOUR_MEDIA_ID

# Auto-reply to comments
python main.py process-comments --media-id YOUR_MEDIA_ID --auto-reply
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI API key for Gemini (Text & Image) | Yes |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram Graph API access token | Yes |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram business account ID | Yes |
| `FACEBOOK_PAGE_ID` | Facebook page ID linked to Instagram | Yes |
| `BRAND_NAME` | Your brand name | Yes |
| `BRAND_VOICE` | Brand voice description | No |
| `TARGET_AUDIENCE` | Target audience description | No |
| `ENABLE_HUMAN_REVIEW` | Enable human review before posting | No (default: true) |
| `AUTO_PUBLISH` | Auto-publish without review | No (default: false) |

### Getting Instagram API Credentials

1. Create a Facebook App at [developers.facebook.com](https://developers.facebook.com)
2. Add Instagram Graph API product
3. Link your Instagram Business account to a Facebook Page
4. Generate an access token with required permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_comments`
   - `instagram_manage_insights`
5. Get your Instagram Business Account ID from the Graph API Explorer

### Getting Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file
4. This one key works for both text (Gemini) and image (Nano Banana) generation!

## 🎯 Workflow Examples

### Content Creation Workflow

```python
from src.agents import ContentCreatorAgent, ImageGeneratorAgent, PostingAgent

# 1. Generate content
content_agent = ContentCreatorAgent()
content = await content_agent.create_content(
    theme="summer vibes",
    brand_voice="casual and fun",
    target_audience="millennials"
)

# 2. Generate image
image_agent = ImageGeneratorAgent()
image = await image_agent.generate_image(
    prompt=content["image_prompt"]
)

# 3. Publish
posting_agent = PostingAgent()
result = await posting_agent.publish_post(
    image_url=image["image_url"],
    caption=content["caption"],
    hashtags=content["hashtags"],
    auto_publish=True
)
```

### Engagement Workflow

```python
from src.agents import EngagementAgent

engagement_agent = EngagementAgent()
result = await engagement_agent.process_comments(
    media_id="your_media_id",
    brand_voice="friendly and helpful",
    post_caption="Your original caption",
    auto_reply=True
)

# Review flagged comments
for comment in result["flagged_for_review"]:
    print(f"Comment: {comment['text']}")
    print(f"Suggested reply: {comment['suggested_reply']}")
```

## 🛠️ Development

### Project Structure

```
instagram_posting_agent/
├── src/
│   ├── agents/          # Specialized agents
│   ├── graph/           # LangGraph state and workflows
│   ├── tools/           # API wrappers and utilities
│   ├── models/          # Data models
│   ├── config/          # Configuration management
│   └── cli/             # CLI interface
├── data/                # Data storage
├── tests/               # Tests
├── main.py              # Entry point
├── requirements.txt     # Dependencies
└── .env.example         # Environment template
```

### Adding Custom Agents

1. Create agent file in `src/agents/`
2. Define agent node function
3. Add to workflow in `src/graph/workflow.py`
4. Update supervisor routing logic

## 🔒 Security & Best Practices

- **Never commit `.env`** - Keep API keys secure
- **Rate Limiting** - Instagram API has limits (200 calls/hour)
- **Human Review** - Enable for sensitive content
- **Compliance** - Follow Instagram's Terms of Service
- **Content Safety** - Review generated content before publishing

## 📊 Monitoring & Logging

Logs are stored in `logs/` directory with daily rotation:

```python
from loguru import logger

logger.info("Your log message")
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **LangGraph** - Multi-agent orchestration framework
- **Google Gemini** - Advanced language and image models
- **Nano Banana** - State-of-the-art image generation
- **Instagram Graph API** - Instagram integration

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the [implementation plan](implementation_plan.md) for detailed architectural plans

## 🚧 Roadmap

- [ ] Scheduler Agent for optimal posting times
- [ ] Analytics Agent for performance insights
- [ ] Multi-account management
- [ ] Story and Reel automation
- [ ] Competitor analysis
- [ ] A/B testing for captions

---

**Built with ❤️ using LangGraph and Google Gemini**
