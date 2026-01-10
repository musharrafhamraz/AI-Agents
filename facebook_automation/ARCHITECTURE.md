# Facebook Automation - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Facebook Automation Crew                 │
│                         (CrewAI)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      main.py (Entry Point)                   │
│  • Loads inputs (topic, audience, brand_voice)              │
│  • Initializes crew                                          │
│  • Executes kickoff()                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    crew.py (Crew Assembly)                   │
│  • Loads agents from agents.yaml                            │
│  • Loads tasks from tasks.yaml                              │
│  • Assigns tools to agents                                   │
│  • Configures sequential process                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────┴─────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────────┐                      ┌──────────────────┐
│  agents.yaml     │                      │   tasks.yaml     │
│  (5 Agents)      │                      │   (6 Tasks)      │
└──────────────────┘                      └──────────────────┘
        │                                             │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Sequential Execution                      │
└─────────────────────────────────────────────────────────────┘
```

## Agent-Task-Tool Flow

```
┌──────────────────────────────────────────────────────────────┐
│ Task 1: Ideation                                             │
│ Agent: Content Strategist                                    │
│ Tools: None (uses LLM reasoning)                            │
│ Output: 3-5 trending topics                                  │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Task 2: Drafting                                             │
│ Agent: Creative Copywriter                                   │
│ Tools: TrendSearchTool, WebScrapeTool                       │
│ Output: 3 post variations                                    │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Task 3: Visualization                                        │
│ Agent: Visual Artist                                         │
│ Tools: ImageGenerationTool                                   │
│ Output: Image URL                                            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Task 4: Review                                               │
│ Agent: Content Strategist                                    │
│ Tools: None (uses LLM reasoning)                            │
│ Output: Approval/Revision request                            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Task 5: Publishing                                           │
│ Agent: Social Media Publisher                                │
│ Tools: FacebookPublishTool                                   │
│ Output: Post ID and link                                     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│ Task 6: Analytics                                            │
│ Agent: Community Analyst                                     │
│ Tools: FacebookInsightsTool                                  │
│ Output: facebook_analytics_report.md                         │
└──────────────────────────────────────────────────────────────┘
```

## Tool Integration

```
┌─────────────────────────────────────────────────────────────┐
│                      Custom Tools                            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Facebook API │    │ Pollinations │    │ Web Scraping │
│   Tools      │    │     AI       │    │    Tools     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ • Publish    │    │ • Generate   │    │ • Trend      │
│ • Insights   │    │   Images     │    │   Search     │
│              │    │              │    │ • Web Scrape │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Data Flow

```
User Input
    │
    ├─ topic: "Technology and Innovation"
    ├─ target_audience: "Tech enthusiasts"
    └─ brand_voice: "Informative, inspiring"
    │
    ▼
┌─────────────────────────────────────────┐
│         YAML Variable Injection          │
│  Tasks use {topic}, {target_audience},  │
│  {brand_voice} in descriptions          │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│         Agent Execution Loop             │
│  Each agent processes its task with     │
│  context from previous tasks            │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│         Tool Invocation                  │
│  Agents call tools as needed:           │
│  • Search trends                         │
│  • Generate images                       │
│  • Publish to Facebook                   │
│  • Fetch analytics                       │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│         Output Generation                │
│  • Console logs (verbose)                │
│  • facebook_analytics_report.md          │
└─────────────────────────────────────────┘
```

## Configuration Hierarchy

```
┌─────────────────────────────────────────┐
│          pyproject.toml                  │
│  • Project metadata                      │
│  • Dependencies                          │
│  • CLI scripts                           │
└─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│              .env                        │
│  • GEMINI_API_KEY                       │
│  • FACEBOOK_PAGE_ACCESS_TOKEN           │
│  • FACEBOOK_PAGE_ID                     │
└─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         config/agents.yaml               │
│  • Agent definitions                     │
│  • Roles, goals, backstories            │
└─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         config/tasks.yaml                │
│  • Task descriptions                     │
│  • Expected outputs                      │
│  • Agent assignments                     │
└─────────────────────────────────────────┘
```

## External Integrations

```
┌─────────────────────────────────────────────────────────────┐
│                    Facebook Automation Crew                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Google       │    │ Facebook     │    │ Pollinations │
│ Gemini API   │    │ Graph API    │    │     AI       │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ • LLM        │    │ • POST /feed │    │ • Free image │
│   reasoning  │    │ • GET        │    │   generation │
│ • Content    │    │   /insights  │    │ • No API key │
│   generation │    │ • Page data  │    │   required   │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────┐
│         Task Execution                   │
└─────────────────────────────────────────┘
                │
                ▼
        ┌───────┴───────┐
        │ Success?      │
        └───────┬───────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
    ┌──────┐      ┌──────────┐
    │ Yes  │      │   No     │
    └──────┘      └──────────┘
        │               │
        ▼               ▼
┌──────────┐    ┌──────────────┐
│ Continue │    │ Tool returns │
│ to next  │    │ error string │
│ task     │    │ Agent adapts │
└──────────┘    └──────────────┘
                        │
                        ▼
                ┌──────────────┐
                │ Retry or     │
                │ alternative  │
                │ approach     │
                └──────────────┘
```

## Scalability Considerations

```
Current: Sequential Process
┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐
│ T1 │→ │ T2 │→ │ T3 │→ │ T4 │→ │ T5 │→ │ T6 │
└────┘  └────┘  └────┘  └────┘  └────┘  └────┘

Future: Hierarchical Process (Optional)
                ┌────────────┐
                │  Manager   │
                └────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    ┌──────┐      ┌──────┐      ┌──────┐
    │ Team │      │ Team │      │ Team │
    │  A   │      │  B   │      │  C   │
    └──────┘      └──────┘      └──────┘
```

## Key Design Patterns

1. **Separation of Concerns**
   - Agents: Behavior and expertise
   - Tasks: What needs to be done
   - Tools: How to interact with external systems

2. **Configuration over Code**
   - YAML for agent/task definitions
   - Easy to modify without code changes

3. **Dependency Injection**
   - Tools injected into agents
   - Agents assigned to tasks

4. **Chain of Responsibility**
   - Sequential task execution
   - Each agent handles its specialty

5. **Strategy Pattern**
   - Different tools for different needs
   - Agents choose appropriate tools

## Performance Characteristics

- **Latency**: ~2-5 minutes per full pipeline
- **API Calls**: 
  - Gemini: ~10-15 calls per run
  - Facebook: 2 calls (publish + insights)
  - Pollinations: 1 call per image
- **Cost**: Free tier friendly (Gemini has free quota)
- **Scalability**: Can handle multiple topics/posts per day

## Security Considerations

- ✅ Credentials in `.env` (not committed)
- ✅ `.gitignore` configured
- ✅ Token-based authentication
- ✅ No hardcoded secrets
- ⚠️ Token expiration (60 days for Facebook)
- ⚠️ Rate limiting (handle gracefully)
