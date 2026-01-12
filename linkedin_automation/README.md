# LinkedIn Automation with CrewAI

Autonomous LinkedIn content creation and publishing system powered by CrewAI and Groq LLM.

## 🚀 Features

- **Automated Content Creation**: AI-powered professional content generation
- **Thought Leadership**: Creates insightful, industry-focused posts
- **Professional Visuals**: Generates corporate-style images using Pollinations.ai
- **LinkedIn Publishing**: Automatically posts to your LinkedIn profile or company page
- **Analytics Tracking**: Monitors post performance and engagement
- **Token Optimized**: Efficient LLM usage (~2,200 tokens per run)

## 🏗️ Architecture

The system uses 5 specialized AI agents working in sequence:

1. **Content Strategist** - Identifies trending professional topics
2. **Professional Writer** - Creates compelling LinkedIn posts (200-300 words)
3. **Visual Designer** - Generates professional corporate images
4. **LinkedIn Publisher** - Handles API integration and posting
5. **Engagement Analyst** - Tracks performance and provides insights

## 📋 Prerequisites

- Python 3.10 or higher
- LinkedIn account (personal or company page admin)
- Groq API key ([Get one here](https://console.groq.com))
- LinkedIn Developer App ([Create here](https://www.linkedin.com/developers/apps))

## 🔧 Quick Start

### 1. Install Dependencies

```bash
cd linkedin_automation
uv sync
```

Or with pip:
```bash
pip install -e .
```

### 2. Configure LinkedIn App

1. Create a LinkedIn Developer App at https://www.linkedin.com/developers/apps
2. Add redirect URL: `http://localhost:8000/callback`
3. Request these products:
   - **Sign In with LinkedIn using OpenID Connect**
   - **Share on LinkedIn** (for personal profile)
   - OR **Marketing Developer Platform** (for company page)

### 3. Set Up Environment Variables

```bash
copy .env.example .env
```

Edit `.env` and add:
```env
GROQ_API_KEY=your_groq_api_key
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
MODEL=groq/llama-3.3-70b-versatile
```

### 4. Get LinkedIn Access Token

```bash
python get_linkedin_token.py
```

Follow the instructions to authorize and get your access token. Copy the output to your `.env` file.

### 5. Test Your Setup

```bash
python test_linkedin_post.py
```

### 6. Run the Automation

```bash
crewai run
```

## 📁 Project Structure

```
linkedin_automation/
├── src/
│   └── linkedin_automation/
│       ├── config/
│       │   ├── agents.yaml          # Agent definitions
│       │   └── tasks.yaml           # Task definitions
│       ├── tools/
│       │   └── custom_tool.py       # LinkedIn API tools
│       ├── crew.py                  # Crew orchestration
│       └── main.py                  # Entry point
├── .env                             # Your credentials (not in git)
├── .env.example                     # Template
├── get_linkedin_token.py            # OAuth helper
├── test_linkedin_post.py            # Setup verification
├── LINKEDIN_SETUP.md                # Detailed setup guide
└── README.md                        # This file
```

## 🛠️ Available Tools

### LinkedInPublishTool
Posts text and images to LinkedIn profile or company page.

**Parameters:**
- `text` (required): Post content
- `image_url` (optional): URL to image

### LinkedInAnalyticsTool
Retrieves profile/page analytics and performance metrics.

### LinkedInEngagementTool
Fetches engagement data for recent posts (likes, comments, shares).

### ImageGenerationTool
Generates professional corporate images using Pollinations.ai.

**Parameters:**
- `prompt` (required): Image description
- `style` (optional): Image style (default: "professional")

## 📊 Content Strategy

### Post Characteristics
- **Length**: 200-300 words (LinkedIn favors longer content)
- **Tone**: Professional, insightful, educational
- **Hashtags**: 3-5 industry-specific tags
- **Images**: 1200x627px professional corporate style
- **Frequency**: 3-5 posts per week

### Best Posting Times
- **Days**: Tuesday, Wednesday, Thursday
- **Times**: 7-8 AM, 12 PM, 5-6 PM (business hours)

### Content Types
- Thought leadership and industry insights
- How-to guides and tutorials
- Professional tips and best practices
- Company updates and achievements
- Discussion-sparking questions

## 🔑 LinkedIn API Permissions

### Personal Profile
- `openid` - Basic authentication
- `profile` - Read profile information
- `w_member_social` - Post content on your behalf

### Company Page
- `openid` - Basic authentication
- `profile` - Read profile information
- `w_organization_social` - Post to organization page
- `r_organization_social` - Read organization posts

## ⚙️ Configuration

### Customize Content Topics

Edit `src/linkedin_automation/main.py`:

```python
inputs = {
    'industry': 'Your Industry',
    'target_audience': 'your target audience',
    'tone': 'your preferred tone'
}
```

### Adjust Agent Behavior

Edit `src/linkedin_automation/config/agents.yaml` and `tasks.yaml` to customize:
- Agent roles and goals
- Task descriptions
- Expected outputs
- Content length and style

## 🚨 Troubleshooting

### "Invalid redirect_uri"
- Verify `http://localhost:8000/callback` is added to your LinkedIn app

### "Insufficient permissions"
- Check that required Products are approved in your LinkedIn app
- Wait for LinkedIn approval (can take 1-2 days)

### "Access token expired"
- LinkedIn tokens expire after 60 days
- Run `python get_linkedin_token.py` to get a new token

### Rate Limits
- **Personal Profile**: 100 posts/day
- **Company Page**: 250 posts/day
- **API Requests**: 500 requests/user/day

## 📈 Token Usage

Optimized for efficiency:
- ~2,200 tokens per run
- Stays within Groq's 20,000 tokens/minute limit
- Runs in ~20-30 seconds

## 🔒 Security

- Never commit `.env` file to version control
- Keep your Client Secret secure
- Access tokens expire after 60 days
- Use environment variables for all credentials

## 📚 Documentation

- [LinkedIn API Docs](https://docs.microsoft.com/en-us/linkedin/)
- [OAuth 2.0 Guide](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Groq API Docs](https://console.groq.com/docs)

## 🤝 Contributing

This project is based on the Facebook automation implementation. Feel free to:
- Add new tools and features
- Improve content quality
- Enhance error handling
- Add scheduling capabilities

## 📝 License

MIT License - feel free to use and modify as needed.

## 🎯 Next Steps

1. **Schedule Posts**: Add cron job or scheduler for automated posting
2. **Comment Monitoring**: Implement auto-response to comments
3. **Article Publishing**: Add long-form article support
4. **Multi-Account**: Manage multiple LinkedIn profiles/pages
5. **Advanced Analytics**: Deep dive into post performance

---

**Built with CrewAI** 🚀 | **Powered by Groq** ⚡ | **Images by Pollinations.ai** 🎨
