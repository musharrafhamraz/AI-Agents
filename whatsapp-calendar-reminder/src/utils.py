"""Utility functions."""

import logging
from typing import Optional
from datetime import datetime
import pytz


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level
    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log")
        ]
    )


def format_phone_number(phone: str) -> str:
    """
    Format phone number for WhatsApp.
    
    Args:
        phone: Phone number
        
    Returns:
        Formatted phone number
    """
    # Remove all non-numeric characters except +
    phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Ensure it starts with +
    if not phone.startswith('+'):
        phone = '+' + phone
    
    return phone


def convert_timezone(
    dt: datetime,
    from_tz: str,
    to_tz: str = "UTC"
) -> datetime:
    """
    Convert datetime between timezones.
    
    Args:
        dt: Datetime to convert
        from_tz: Source timezone
        to_tz: Target timezone
        
    Returns:
        Converted datetime
    """
    from_zone = pytz.timezone(from_tz)
    to_zone = pytz.timezone(to_tz)
    
    # Localize if naive
    if dt.tzinfo is None:
        dt = from_zone.localize(dt)
    
    # Convert
    return dt.astimezone(to_zone)


def is_valid_timezone(tz: str) -> bool:
    """
    Check if timezone string is valid.
    
    Args:
        tz: Timezone string
        
    Returns:
        True if valid
    """
    try:
        pytz.timezone(tz)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False
