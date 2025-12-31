"""Agent prompts for email classification and analysis"""

# Classification Agent Prompt
CLASSIFICATION_PROMPT = """You are an expert email classifier. Analyze the email and categorize it.

Email Details:
Sender: {sender}
Subject: {subject}
Body: {body}

Available Categories:
{categories}

Context from similar emails:
{similar_emails}

Sender history:
{sender_history}

Provide your classification in JSON format:
{{
    "category": "the most appropriate category",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of your decision"
}}

Be precise and confident in your classification."""

# Priority Scoring Prompt
PRIORITY_PROMPT = """You are an expert at determining email priority and urgency.

Email Details:
Sender: {sender}
Subject: {subject}
Body: {body}

Sender Context:
{sender_history}

Score this email's priority from 0-10 considering:
- Urgency keywords (urgent, ASAP, deadline, important)
- Sender importance (VIP, boss, client, colleague)
- Time sensitivity (deadlines, meeting times)
- Action requirements

Provide your assessment in JSON format:
{{
    "priority_score": 0-10,
    "urgency_level": "Low/Medium/High",
    "recommended_response_time": "immediate/within 1 hour/within 1 day/when convenient",
    "reasoning": "brief explanation"
}}"""

# Intent Detection Prompt
INTENT_PROMPT = """You are an expert at understanding email intent and purpose.

Email Details:
Sender: {sender}
Subject: {subject}
Body: {body}

Identify the sender's primary intent from these options:
- REQUEST_ACTION: Asking you to do something specific
- SHARE_INFO: Providing information or updates
- ASK_QUESTION: Seeking an answer or clarification
- SCHEDULE_MEETING: Coordinating a meeting or event
- NOTIFY: Informing about an event or status
- FOLLOW_UP: Continuing a previous conversation
- SOCIAL: Social interaction or networking

Provide your analysis in JSON format:
{{
    "intent": "the primary intent",
    "confidence": 0.0-1.0,
    "action_items": ["list of specific actions requested, if any"],
    "requires_response": true/false,
    "reasoning": "brief explanation"
}}"""

# Email Parsing Prompt
PARSING_PROMPT = """Extract structured information from this email.

Raw Email:
{raw_email}

Extract:
1. Main topic/subject matter
2. Key entities (people, companies, dates, locations)
3. Action items mentioned
4. Urgency indicators
5. Distinguish between email signature and actual content

Provide in JSON format:
{{
    "main_topic": "concise topic",
    "entities": {{
        "people": [],
        "companies": [],
        "dates": [],
        "locations": []
    }},
    "action_items": [],
    "urgency_indicators": [],
    "has_signature": true/false
}}"""

# Router Decision Prompt
ROUTER_PROMPT = """Based on the email analysis, decide what actions to take.

Email Classification: {classification}
Priority Score: {priority_score}
Intent: {intent}
Confidence: {confidence}

Available Actions:
- apply_label:<label_name>
- move_to_folder:<folder_name>
- mark_important
- mark_for_followup
- archive
- mark_as_spam

Decide the appropriate actions in JSON format:
{{
    "actions": ["list of actions to take"],
    "reasoning": "brief explanation of decisions"
}}

Be conservative - only take actions you're confident about."""
