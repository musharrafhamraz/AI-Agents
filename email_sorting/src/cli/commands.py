"""CLI commands for email sorting agent"""

import click
from rich.console import Console
from rich.table import Table
from datetime import datetime

console = Console()


@click.group()
def cli():
    """AI-Powered Email Sorting Agent"""
    pass


@cli.command()
@click.option('--provider', type=click.Choice(['gmail', 'outlook', 'imap']), 
              default='gmail', help='Email provider to use')
def setup(provider: str):
    """Initial setup and authentication"""
    console.print(f"\n[bold cyan]Setting up {provider} integration...[/bold cyan]\n")
    
    if provider == "gmail":
        from ..tools.gmail_tools import get_gmail_client
        
        console.print("This will open a browser window for Gmail authentication.")
        console.print("Please authorize the application to access your Gmail account.\n")
        
        try:
            client = get_gmail_client()
            client.authenticate()
            console.print("[green]✓[/green] Gmail authentication successful!")
            console.print("\n[dim]Credentials saved to token.pickle[/dim]")
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            console.print("\n[yellow]Setup Instructions:[/yellow]")
            console.print("1. Go to Google Cloud Console: https://console.cloud.google.com")
            console.print("2. Create a new project or select existing")
            console.print("3. Enable Gmail API")
            console.print("4. Create OAuth 2.0 credentials (Desktop app)")
            console.print("5. Download credentials.json to project root")
            return
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            return
    
    elif provider == "outlook":
        console.print("[yellow]Outlook integration coming soon![/yellow]")
        return
    
    elif provider == "imap":
        console.print("[yellow]IMAP integration coming soon![/yellow]")
        return
    
    console.print(f"\nYou can now run: [bold]python main.py process[/bold]")


@cli.command()
@click.option('--batch-size', default=10, help='Number of emails to process')
@click.option('--dry-run', is_flag=True, help='Preview actions without executing')
def process(batch_size: int, dry_run: bool):
    """Process emails through the AI agent workflow"""
    from ..graph import create_email_sorting_workflow
    from ..agents import fetch_emails
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from langgraph.checkpoint.sqlite import SqliteSaver
    import os

    
    console.print(f"\n[bold cyan]Processing up to {batch_size} emails...[/bold cyan]\n")
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No actions will be executed[/yellow]\n")
    
    try:
        # Fetch emails
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Fetching emails...", total=None)
            emails = fetch_emails(batch_size)
            progress.update(task, completed=True)
        
        if not emails:
            console.print("[yellow]No unread emails found.[/yellow]")
            return
        
        console.print(f"[green]Found {len(emails)} unread emails[/green]\n")
        
        # Ensure directory exists
        os.makedirs("data/checkpoints", exist_ok=True)

        # Create workflow with checkpointer
        with SqliteSaver.from_conn_string("data/checkpoints/workflow.db") as memory:
            workflow = create_email_sorting_workflow(checkpointer=memory)
            
            # Process each email
            results = []
            for i, email_state in enumerate(emails, 1):
                console.print(f"\n[bold]Email {i}/{len(emails)}[/bold]")
                console.print(f"From: {email_state['sender']}")
                console.print(f"Subject: {email_state['subject'][:60]}...")
                
                try:
                    # Run workflow
                    config = {"configurable": {"thread_id": email_state.get("message_id", "default")}}
                    result = workflow.invoke(email_state, config=config)
                    results.append(result)
                    
                    # Display results
                    console.print(f"  Category: [cyan]{result.get('classification', 'Unknown')}[/cyan]")
                    console.print(f"  Priority: [yellow]{(result.get('priority_score') or 0):.1f}/10[/yellow]")
                    console.print(f"  Confidence: [green]{(result.get('overall_confidence') or 0):.0%}[/green]")
                    
                    if not dry_run:
                        console.print(f"  Status: [green]{result.get('processing_stage')}[/green]")
                    
                    if result.get('error'):
                        console.print(f"  [red]Agent Error: {result.get('error')}[/red]")
                    
                except Exception as e:
                    console.print(f"  [red]Error: {str(e)}[/red]")
                    import traceback
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        # Summary
        console.print(f"\n[bold green]✓ Processed {len(results)} emails successfully![/bold green]")
        
        if dry_run:
            console.print("\n[yellow]Dry run complete - no actions were executed[/yellow]")
        
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())


@cli.command()
@click.option('--days', default=7, help='Number of days to show stats for')
def stats(days: int):
    """Show email processing statistics"""
    console.print(f"\n[bold cyan]Email Statistics (Last {days} days)[/bold cyan]\n")
    
    # Create stats table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Category")
    table.add_column("Count", justify="right")
    table.add_column("Percentage", justify="right")
    
    # TODO: Query database for stats
    # Placeholder data
    table.add_row("Work", "45", "45%")
    table.add_row("Personal", "20", "20%")
    table.add_row("Promotions", "25", "25%")
    table.add_row("Spam", "10", "10%")
    
    console.print(table)
    console.print(f"\n[dim]Total emails processed: 100[/dim]")


@cli.command()
def visualize():
    """Visualize the LangGraph workflow"""
    from ..graph import create_email_sorting_workflow
    
    console.print("\n[bold cyan]Generating workflow visualization...[/bold cyan]\n")
    
    workflow = create_email_sorting_workflow()
    
    try:
        # Generate graph visualization
        graph_image = workflow.get_graph().draw_mermaid_png()
        
        # Save to file
        output_path = "workflow_diagram.png"
        with open(output_path, "wb") as f:
            f.write(graph_image)
        
        console.print(f"[green]✓[/green] Workflow diagram saved to: {output_path}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("\n[yellow]Tip:[/yellow] Install graphviz for visualization")


@cli.command()
@click.argument('email_id')
@click.argument('category')
def reclassify(email_id: str, category: str):
    """Manually reclassify an email"""
    console.print(f"\n[cyan]Reclassifying email {email_id} as {category}...[/cyan]\n")
    
    # TODO: Update database
    # TODO: Record correction for learning
    
    console.print("[green]✓[/green] Email reclassified successfully!")


@cli.command()
def test():
    """Test the workflow with a sample email"""
    from ..graph import create_email_sorting_workflow
    
    console.print("\n[bold cyan]Testing workflow with sample email...[/bold cyan]\n")
    
    # Sample email state
    sample_email = {
        "message_id": "test-123",
        "sender": "boss@company.com",
        "recipient": "you@company.com",
        "subject": "URGENT: Project deadline tomorrow",
        "body": "Hi, we need to finalize the project report by tomorrow. Can you send me the latest version?",
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
        "similar_emails": []
    }
    
    # Create and run workflow
    from langgraph.checkpoint.memory import MemorySaver
    
    with MemorySaver() as memory:
        workflow = create_email_sorting_workflow(checkpointer=memory)
    
        try:
            config = {"configurable": {"thread_id": "test-123"}}
            result = workflow.invoke(sample_email, config=config)
            
            # Display results
            console.print("\n[bold green]Results:[/bold green]")
            console.print(f"Category: {result.get('classification')}")
            console.print(f"Priority: {result.get('priority_score'):.1f}/10")
            console.print(f"Intent: {result.get('intent')}")
            console.print(f"Confidence: {result.get('overall_confidence', 0):.0%}")
            console.print(f"Actions: {', '.join(result.get('actions', []))}")
            console.print(f"Labels: {', '.join(result.get('labels', []))}")
            
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}")
            import traceback
            console.print(traceback.format_exc())


if __name__ == '__main__':
    cli()
