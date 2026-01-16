"""
Scheduler for sending appointment reminders
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlmodel import Session, select
from models import Appointment, Lead
from database import engine
from whatsapp_utils import whatsapp_api
import logging

logger = logging.getLogger(__name__)


def send_reminders():
    """
    Check for upcoming appointments and send reminders
    """
    now = datetime.utcnow()
    
    with Session(engine) as session:
        # Get appointments in the next 2 hours
        two_hours_later = now + timedelta(hours=2)
        one_hour_later = now + timedelta(hours=1)
        
        # Find appointments needing 2-hour reminder
        appointments_2h = session.exec(
            select(Appointment).where(
                Appointment.status == "confirmed",
                Appointment.appointment_time <= two_hours_later,
                Appointment.appointment_time > now,
                Appointment.reminder_2h_sent == False
            )
        ).all()
        
        for appointment in appointments_2h:
            lead = session.get(Lead, appointment.lead_id)
            if lead:
                time_str = appointment.appointment_time.strftime('%I:%M %p')
                date_str = appointment.appointment_time.strftime('%B %d')
                
                message = f"""
🔔 Reminder: You have an appointment coming up!

📅 Date: {date_str}
🕐 Time: {time_str}
📋 Service: {appointment.service}

See you soon!
                """.strip()
                
                try:
                    whatsapp_api.send_message(lead.phone_number, message)
                    appointment.reminder_2h_sent = True
                    session.add(appointment)
                    logger.info(f"Sent 2-hour reminder for appointment {appointment.id}")
                except Exception as e:
                    logger.error(f"Failed to send 2-hour reminder: {str(e)}")
        
        # Find appointments needing 1-hour reminder
        appointments_1h = session.exec(
            select(Appointment).where(
                Appointment.status == "confirmed",
                Appointment.appointment_time <= one_hour_later,
                Appointment.appointment_time > now,
                Appointment.reminder_1h_sent == False
            )
        ).all()
        
        for appointment in appointments_1h:
            lead = session.get(Lead, appointment.lead_id)
            if lead:
                time_str = appointment.appointment_time.strftime('%I:%M %p')
                
                message = f"""
⏰ Final Reminder!

Your appointment is in 1 hour at {time_str}.

Please let us know if you need to reschedule.
                """.strip()
                
                try:
                    whatsapp_api.send_message(lead.phone_number, message)
                    appointment.reminder_1h_sent = True
                    session.add(appointment)
                    logger.info(f"Sent 1-hour reminder for appointment {appointment.id}")
                except Exception as e:
                    logger.error(f"Failed to send 1-hour reminder: {str(e)}")
        
        session.commit()


def start_scheduler():
    """
    Start the background scheduler
    """
    scheduler = BackgroundScheduler()
    
    # Run every 5 minutes
    scheduler.add_job(send_reminders, 'interval', minutes=5)
    
    scheduler.start()
    logger.info("Scheduler started - checking for reminders every 5 minutes")
    
    return scheduler


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = start_scheduler()
    
    try:
        # Keep the script running
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
