"""Tools package - Email provider tools and utilities"""

from .gmail_tools import (
    GmailClient,
    get_gmail_client,
    fetch_gmail_emails,
    apply_gmail_label,
    mark_gmail_important,
    archive_gmail_message,
    move_gmail_to_spam,
)

__all__ = [
    "GmailClient",
    "get_gmail_client",
    "fetch_gmail_emails",
    "apply_gmail_label",
    "mark_gmail_important",
    "archive_gmail_message",
    "move_gmail_to_spam",
]
