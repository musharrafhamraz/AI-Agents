# Facebook Automation Crew

An autonomous Facebook Page management system built with CrewAI. This crew of specialized AI agents collaborates to handle content creation, publishing, and engagement monitoring for Facebook Pages.

## 🚀 Features

- **Content Strategist**: Coordinates the pipeline and ensures brand consistency
- **Creative Copywriter**: Generates engaging, trend-aware post variations with hashtags
- **Visual Artist**: Creates eye-catching images using AI (Pollinations.ai)
- **Social Media Publisher**: Handles Facebook Graph API publishing
- **Community Analyst**: Analyzes insights and provides recommendations
- **Powered by Groq Llama 3.3**: Ultra-fast model with no quota issues (14,400 requests/day)

## 📋 Prerequisites

- Python 3.10 - 3.13
- Facebook Page with admin access
- Groq API key (free, fast, generous quotas)

## 🛠️ Installation

1. **Install dependencies using UV (recommended):**
   ```bash
   crewai install
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

2. **Configure environment variables:**
   
   Edit the `.env` file and add your credentials:
   ```env
   GROQ_API_KEY=your_groq_api_key
   FACEBOOK_PAGE_ACCESS_TOKEN=your_facebook_page_access_token
   FACEBOOK_PAGE_ID=your_facebook_page_id
   ```

## 🔑 Getting Your Credentials

### Groq API Key (Recommended - No Quota Issues!)

1. Go to [Groq Console](https://console.groq.com/)
2. Sign up (free, no credit card required)
3. Go to [API Keys](https://console.groq.com/keys)
4. Click "Create API Key"
5. Copy the key to your `.env` file

**Why Groq?**
- ⚡ Ultra-fast (500+ tokens/second)
- ✅ 14,400 requests/day (vs 1,500 for Gemini)
- ✅ No quota issues
- ✅ Free tier is very generous

See [GROQ_SETUP.md](GROQ_SETUP.md) for detailed instructions.

### Facebook Credentials

**Get Page Access Token:**
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app or use an existing one
3. Add "Facebook Login" product
4. Go to Tools > Graph API Explorer
5. Select your app and page
6. Generate a token with these permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`
7. Copy the token to your `.env` file

**Get Page ID:**
1. Go to your Facebook Page
2. Click "About" in the left menu
3. Scroll down to find "Page ID"
4. Copy it to your `.env` file

## 🎯 Usage

### Run the Crew

```bash
crewai run
```

Or:
```bash
python -m facebook_automation.main
```

### Customize Inputs

Edit `src/facebook_automation/main.py` to customize:
```python
inputs = {
    'topic': 'Your Topic Here',
    'target_audience': 'Your Target Audience',
    'brand_voice': 'Your Brand Voice'
}
```

### Train the Crew

```bash
crewai train 5 training_data.pkl
```

### Test the Crew

```bash
crewai test 3 gpt-4
```

## 📁 Project Structure

```
facebook_automation/
├── src/
│   └── facebook_automation/
│       ├── config/
│       │   ├── agents.yaml       # Agent definitions
│       │   └── tasks.yaml        # Task definitions
│       ├── tools/
│       │   └── custom_tool.py    # Custom tools (Facebook API, Image Gen)
│       ├── crew.py               # Crew assembly
│       └── main.py               # Entry point
├── .env                          # Environment variables
├── pyproject.toml                # Project configuration
└── README.md                     # This file
```

## 🔧 Customization

### Modify Agents

Edit `src/facebook_automation/config/agents.yaml` to adjust agent roles, goals, and backstories.

### Modify Tasks

Edit `src/facebook_automation/config/tasks.yaml` to change task descriptions and expected outputs.

### Add Custom Tools

Create new tools in `src/facebook_automation/tools/custom_tool.py`:

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param: str = Field(..., description="Parameter description")

class MyCustomTool(BaseTool):
    name: str = "My Custom Tool"
    description: str = "Tool description"
    args_schema: Type[BaseModel] = MyToolInput

    def _run(self, param: str) -> str:
        # Your tool logic here
        return "result"
```

Then add it to the appropriate agent in `crew.py`.

## 🔄 Workflow

The crew executes tasks sequentially:

1. **Ideation**: Research current trends in the niche
2. **Drafting**: Write 3 post variations based on trends
3. **Visualization**: Generate complementary images
4. **Review**: Quality check and approval
5. **Publishing**: Post to Facebook via Graph API
6. **Analytics**: Analyze performance and provide recommendations

## 🐛 Troubleshooting

**Missing API Key Error:**
- Ensure `.env` file exists with all required variables
- Check that API keys are valid

**Facebook Publishing Fails:**
- Verify Page Access Token has correct permissions
- Check that token hasn't expired (tokens expire after 60 days)
- Ensure Page ID is correct

**Image Generation Issues:**
- Pollinations.ai may be rate-limited
- Try simpler prompts
- Check internet connection

## 📝 Output

The crew generates:
- `facebook_analytics_report.md` - Performance analytics report
- Console logs showing the entire workflow

## 🚀 Future Enhancements

- [ ] Human-in-the-loop review before publishing
- [ ] Memory/history for agents to learn from past posts
- [ ] Scheduled posting at optimal times
- [ ] Multi-language support
- [ ] A/B testing different post variations
- [ ] Integration with analytics dashboards
- [ ] Comment monitoring and auto-responses

## 📄 License

MIT

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

For more information about CrewAI:
- Visit [CrewAI documentation](https://docs.crewai.com)
- Check out the [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join the Discord](https://discord.com/invite/X4JWnZnxPb)
