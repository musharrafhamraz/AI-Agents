"""
LangGraph Agent State and Workflow
"""
from typing import TypedDict, Literal, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlmodel import Session, select
from models import Lead, Appointment
from database import engine
from whatsapp_utils import whatsapp_api
from config import settings
import json


# Define the agent state
class AgentState(TypedDict):
    """State for the appointment booking agent"""
    phone_number: str
    message: str
    intent: Optional[str]
    extracted_data: Optional[dict]
    response: Optional[str]
    appointment_id: Optional[int]


# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=settings.model_name,
    google_api_key=settings.gemini_api_key,
    temperature=0.7
)


def detect_intent(state: AgentState) -> AgentState:
    """
    Detect user intent from the message
    """
    message = state["message"]
    
    prompt = f"""
    You are an intent classifier for a WhatsApp appointment booking system.
    Analyze the following message and classify it into ONE of these intents:
    - booking: User wants to book an appointment
    - cancel: User wants to cancel an appointment
    - query: User has a question about services, hours, etc.
    - greeting: User is just saying hi or starting conversation
    
    Message: "{message}"
    
    Respond with ONLY the intent name (booking/cancel/query/greeting).
    """
    
    response = llm.invoke(prompt)
    intent = response.content.strip().lower()
    
    state["intent"] = intent
    return state


def extract_booking_details(state: AgentState) -> AgentState:
    """
    Extract booking details from the message
    """
    message = state["message"]
    
    prompt = f"""
    Extract appointment booking details from this message.
    Return a JSON object with these fields (use null if not mentioned):
    - name: Client's name
    - service: Service requested
    - date: Date in YYYY-MM-DD format
    - time: Time in HH:MM format (24-hour)
    - reason: Reason for appointment
    
    Message: "{message}"
    
    Respond with ONLY valid JSON, no other text.
    """
    
    response = llm.invoke(prompt)
    try:
        extracted = json.loads(response.content.strip())
        state["extracted_data"] = extracted
    except json.JSONDecodeError:
        state["extracted_data"] = {}
    
    return state


def check_availability(state: AgentState) -> AgentState:
    """
    Check if the requested time slot is available
    """
    extracted = state.get("extracted_data", {})
    
    if not extracted.get("date") or not extracted.get("time"):
        state["response"] = "I'd be happy to book an appointment for you! Could you please provide your preferred date and time?"
        return state
    
    # Parse datetime
    try:
        date_str = extracted["date"]
        time_str = extracted["time"]
        appointment_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except (ValueError, KeyError):
        state["response"] = "I couldn't understand the date/time. Could you please provide it in a clearer format? For example: 'January 15th at 2pm'"
        return state
    
    # Check if slot is available
    with Session(engine) as session:
        existing = session.exec(
            select(Appointment).where(
                Appointment.appointment_time == appointment_time,
                Appointment.status == "confirmed"
            )
        ).first()
        
        if existing:
            state["response"] = f"Sorry, {appointment_time.strftime('%B %d at %I:%M %p')} is already booked. Would you like to try a different time?"
        else:
            # Slot is available, proceed to booking
            state["response"] = None
    
    return state


def book_appointment(state: AgentState) -> AgentState:
    """
    Create the appointment in the database
    """
    phone_number = state["phone_number"]
    extracted = state.get("extracted_data", {})
    
    with Session(engine) as session:
        # Get or create lead
        lead = session.exec(
            select(Lead).where(Lead.phone_number == phone_number)
        ).first()
        
        if not lead:
            lead = Lead(
                phone_number=phone_number,
                name=extracted.get("name")
            )
            session.add(lead)
            session.commit()
            session.refresh(lead)
        elif extracted.get("name") and not lead.name:
            lead.name = extracted["name"]
            session.add(lead)
            session.commit()
        
        # Create appointment
        date_str = extracted["date"]
        time_str = extracted["time"]
        appointment_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        appointment = Appointment(
            lead_id=lead.id,
            service=extracted.get("service", "General Appointment"),
            appointment_time=appointment_time,
            reason=extracted.get("reason"),
            status="confirmed"
        )
        
        session.add(appointment)
        session.commit()
        session.refresh(appointment)
        
        state["appointment_id"] = appointment.id
        state["response"] = f"""
✅ Appointment Confirmed!

📅 Date: {appointment_time.strftime('%B %d, %Y')}
🕐 Time: {appointment_time.strftime('%I:%M %p')}
📋 Service: {appointment.service}

We'll send you reminders before your appointment. See you then!
        """.strip()
    
    return state


def cancel_appointment(state: AgentState) -> AgentState:
    """
    Cancel an existing appointment
    """
    phone_number = state["phone_number"]
    
    with Session(engine) as session:
        # Find the lead
        lead = session.exec(
            select(Lead).where(Lead.phone_number == phone_number)
        ).first()
        
        if not lead:
            state["response"] = "I couldn't find any appointments under this number. Could you please verify your phone number?"
            return state
        
        # Find active appointment
        appointment = session.exec(
            select(Appointment).where(
                Appointment.lead_id == lead.id,
                Appointment.status == "confirmed",
                Appointment.appointment_time > datetime.utcnow()
            ).order_by(Appointment.appointment_time)
        ).first()
        
        if not appointment:
            state["response"] = "You don't have any upcoming appointments to cancel."
            return state
        
        # Cancel the appointment
        appointment.status = "cancelled"
        appointment.updated_at = datetime.utcnow()
        session.add(appointment)
        session.commit()
        
        state["response"] = f"""
❌ Appointment Cancelled

Your appointment on {appointment.appointment_time.strftime('%B %d at %I:%M %p')} has been cancelled.

Feel free to book a new appointment anytime!
        """.strip()
    
    return state


def handle_query(state: AgentState) -> AgentState:
    """
    Answer general queries using LLM
    """
    message = state["message"]
    
    prompt = f"""
    You are a helpful assistant for {settings.business_name}.
    
    Business Hours: {settings.business_hours_start}:00 AM - {settings.business_hours_end}:00 PM
    
    Answer this customer question in a friendly, concise way:
    "{message}"
    
    Keep the response under 100 words.
    """
    
    response = llm.invoke(prompt)
    state["response"] = response.content.strip()
    
    return state


def handle_greeting(state: AgentState) -> AgentState:
    """
    Respond to greetings
    """
    state["response"] = f"""
Hello! 👋 Welcome to {settings.business_name}!

I can help you with:
• Booking appointments
• Cancelling appointments
• Answering questions about our services

How can I assist you today?
    """.strip()
    
    return state


def route_intent(state: AgentState) -> str:
    """
    Route to the appropriate handler based on intent
    """
    intent = state.get("intent", "query")
    
    if intent == "booking":
        return "extract_details"
    elif intent == "cancel":
        return "cancel"
    elif intent == "greeting":
        return "greeting"
    else:
        return "query"


def route_after_extraction(state: AgentState) -> str:
    """
    Route after extracting booking details
    """
    extracted = state.get("extracted_data", {})
    
    # Check if we have minimum required info
    if extracted.get("date") and extracted.get("time"):
        return "check_availability"
    else:
        return "end"


def route_after_availability(state: AgentState) -> str:
    """
    Route after checking availability
    """
    if state.get("response"):
        # Slot not available or error
        return "end"
    else:
        # Slot available, proceed to book
        return "book"


# Build the graph
def create_agent_graph():
    """
    Create the LangGraph workflow
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("detect_intent", detect_intent)
    workflow.add_node("extract_details", extract_booking_details)
    workflow.add_node("check_availability", check_availability)
    workflow.add_node("book", book_appointment)
    workflow.add_node("cancel", cancel_appointment)
    workflow.add_node("query", handle_query)
    workflow.add_node("greeting", handle_greeting)
    
    # Set entry point
    workflow.set_entry_point("detect_intent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "detect_intent",
        route_intent,
        {
            "extract_details": "extract_details",
            "cancel": "cancel",
            "query": "query",
            "greeting": "greeting"
        }
    )
    
    workflow.add_conditional_edges(
        "extract_details",
        route_after_extraction,
        {
            "check_availability": "check_availability",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "check_availability",
        route_after_availability,
        {
            "book": "book",
            "end": END
        }
    )
    
    # Add edges to END
    workflow.add_edge("book", END)
    workflow.add_edge("cancel", END)
    workflow.add_edge("query", END)
    workflow.add_edge("greeting", END)
    
    return workflow.compile()


# Create the compiled graph
agent_graph = create_agent_graph()
