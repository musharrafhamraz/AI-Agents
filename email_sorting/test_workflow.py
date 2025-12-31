"""
Simple test script to verify the email sorting workflow.
Run this to test the system without setting up Gmail.
"""

from datetime import datetime
from src.graph import create_email_sorting_workflow
from rich.console import Console

console = Console()


def test_workflow():
    """Test the workflow with sample emails"""
    
    # Sample emails
    sample_emails = [
        {
            "message_id": "test-001",
            "sender": "boss@company.com",
            "recipient": "you@company.com",
            "subject": "URGENT: Project deadline tomorrow",
            "body": "Hi, we need to finalize the project report by tomorrow. Can you send me the latest version ASAP?",
            "body_html": None,
            "received_at": datetime.now().isoformat(),
            "thread_id": None,
            "has_attachments": False,
            "attachment_count": 0,
            "processing_stage": "fetched",
            "requires_human_review": False,
            "action_items": [],
            "actions": [],
            "labels": [],
            "retry_count": 0,
            "sender_history": {
                "total_emails": 50,
                "avg_priority": 8.0,
                "common_categories": ["Work"],
                "is_vip": True
            },
            "similar_emails": [],
            "classification": None,
            "classification_confidence": None,
            "classification_reasoning": None,
            "priority_score": None,
            "urgency_level": None,
            "recommended_response_time": None,
            "priority_reasoning": None,
            "intent": None,
            "intent_confidence": None,
            "requires_response": None,
            "intent_reasoning": None,
            "overall_confidence": None,
            "error": None,
            "processed_at": None,
            "processing_time_ms": None
        },
        {
            "message_id": "test-002",
            "sender": "newsletter@deals.com",
            "recipient": "you@company.com",
            "subject": "50% OFF Everything - Limited Time!",
            "body": "Don't miss out on our biggest sale of the year! Get 50% off all items. Shop now before it's too late!",
            "body_html": None,
            "received_at": datetime.now().isoformat(),
            "thread_id": None,
            "has_attachments": False,
            "attachment_count": 0,
            "processing_stage": "fetched",
            "requires_human_review": False,
            "action_items": [],
            "actions": [],
            "labels": [],
            "retry_count": 0,
            "sender_history": {
                "total_emails": 200,
                "avg_priority": 2.0,
                "common_categories": ["Promotions"],
                "is_vip": False
            },
            "similar_emails": [],
            "classification": None,
            "classification_confidence": None,
            "classification_reasoning": None,
            "priority_score": None,
            "urgency_level": None,
            "recommended_response_time": None,
            "priority_reasoning": None,
            "intent": None,
            "intent_confidence": None,
            "requires_response": None,
            "intent_reasoning": None,
            "overall_confidence": None,
            "error": None,
            "processed_at": None,
            "processing_time_ms": None
        },
        {
            "message_id": "test-003",
            "sender": "friend@gmail.com",
            "recipient": "you@gmail.com",
            "subject": "Coffee this weekend?",
            "body": "Hey! Want to grab coffee this weekend? Let me know when you're free.",
            "body_html": None,
            "received_at": datetime.now().isoformat(),
            "thread_id": None,
            "has_attachments": False,
            "attachment_count": 0,
            "processing_stage": "fetched",
            "requires_human_review": False,
            "action_items": [],
            "actions": [],
            "labels": [],
            "retry_count": 0,
            "sender_history": {
                "total_emails": 30,
                "avg_priority": 5.0,
                "common_categories": ["Personal"],
                "is_vip": False
            },
            "similar_emails": [],
            "classification": None,
            "classification_confidence": None,
            "classification_reasoning": None,
            "priority_score": None,
            "urgency_level": None,
            "recommended_response_time": None,
            "priority_reasoning": None,
            "intent": None,
            "intent_confidence": None,
            "requires_response": None,
            "intent_reasoning": None,
            "overall_confidence": None,
            "error": None,
            "processed_at": None,
            "processing_time_ms": None
        }
    ]
    
    console.print("\n[bold cyan]Testing Email Sorting Workflow[/bold cyan]\n")
    console.print(f"Processing {len(sample_emails)} sample emails...\n")
    
    # Create workflow
    workflow = create_email_sorting_workflow()
    
    # Process each email
    for i, email in enumerate(sample_emails, 1):
        console.print(f"[bold]Email {i}/{len(sample_emails)}[/bold]")
        console.print(f"From: {email['sender']}")
        console.print(f"Subject: {email['subject']}")
        
        try:
            # Run workflow
            result = workflow.invoke(email)
            
            # Display results
            console.print(f"\n[green]Results:[/green]")
            console.print(f"  Category: [cyan]{result.get('classification', 'Unknown')}[/cyan]")
            console.print(f"  Priority: [yellow]{result.get('priority_score', 0):.1f}/10[/yellow] ({result.get('urgency_level', 'Unknown')})")
            console.print(f"  Intent: [magenta]{result.get('intent', 'Unknown')}[/magenta]")
            console.print(f"  Confidence: [green]{result.get('overall_confidence', 0):.0%}[/green]")
            console.print(f"  Actions: {', '.join(result.get('actions', []))}")
            console.print(f"  Labels: {', '.join(result.get('labels', []))}")
            console.print(f"  Stage: {result.get('processing_stage')}")
            
            if result.get('error'):
                console.print(f"  [red]Error: {result['error']}[/red]")
            
            console.print()
            
        except Exception as e:
            console.print(f"[red]Error processing email: {str(e)}[/red]\n")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
    
    console.print("[bold green]✓ Test complete![/bold green]\n")


if __name__ == "__main__":
    test_workflow()
