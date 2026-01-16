"""
FastAPI webhook handler for WhatsApp messages
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from agent import agent_graph, AgentState
from whatsapp_utils import whatsapp_api
from database import init_db
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="WhatsApp Appointment Agent")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "WhatsApp Appointment Agent is running"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Verify webhook for WhatsApp Cloud API
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("Webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")
    else:
        logger.warning("Webhook verification failed")
        return JSONResponse(content={"error": "Verification failed"}, status_code=403)


@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle incoming WhatsApp messages
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")
        
        # Extract message data
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return JSONResponse(content={"status": "ok"})
        
        # Process first message
        message = messages[0]
        phone_number = message.get("from")
        message_type = message.get("type")
        
        # Only handle text messages
        if message_type != "text":
            return JSONResponse(content={"status": "ok"})
        
        message_text = message.get("text", {}).get("body", "")
        
        # Run the agent
        initial_state: AgentState = {
            "phone_number": phone_number,
            "message": message_text,
            "intent": None,
            "extracted_data": None,
            "response": None,
            "appointment_id": None
        }
        
        result = agent_graph.invoke(initial_state)
        
        # Send response
        response_text = result.get("response", "I'm sorry, I didn't understand that. Could you please rephrase?")
        whatsapp_api.send_message(phone_number, response_text)
        
        logger.info(f"Sent response to {phone_number}")
        
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
