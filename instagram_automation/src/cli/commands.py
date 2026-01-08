"""CLI commands for Instagram Agent."""
import asyncio
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from datetime import datetime

from src.agents import ContentCreatorAgent, ImageGeneratorAgent, PostingAgent, EngagementAgent
from src.graph.workflow import content_workflow
from src.config import settings
from src.models import Post, PostStatus
from loguru import logger

console = Console()


@click.group()
def cli():
    """Instagram Automation Agent CLI."""
    pass


@cli.command()
@click.option("--theme", "-t", required=True, help="Content theme or topic")
@click.option("--brand-voice", "-v", default=None, help="Brand voice (default from config)")
@click.option("--audience", "-a", default=None, help="Target audience (default from config)")
@click.option("--auto-publish", is_flag=True, help="Auto-publish without review")
def create_post(theme: str, brand_voice: str, audience: str, auto_publish: bool):
    """Create and optionally publish an Instagram post."""
    asyncio.run(_create_post(theme, brand_voice, audience, auto_publish))


async def _create_post(theme: str, brand_voice: str, audience: str, auto_publish: bool):
    """Async implementation of create_post."""
    console.print(Panel(f"[bold blue]Creating Instagram Post[/bold blue]\nTheme: {theme}", expand=False))
    
    try:
        # Use config defaults if not provided
        brand_voice = brand_voice or settings.brand_voice
        audience = audience or settings.target_audience
        
        # Create content creator agent
        content_agent = ContentCreatorAgent()
        
        # Generate content
        console.print("[yellow]Generating caption and hashtags...[/yellow]")
        content_result = await content_agent.create_content(
            theme=theme,
            brand_voice=brand_voice,
            target_audience=audience,
            brand_name=settings.brand_name
        )
        
        if content_result.get("errors"):
            console.print(f"[red]Error: {content_result['errors'][0]}[/red]")
            return
        
        caption = content_result.get("caption", "")
        hashtags = content_result.get("hashtags", [])
        image_prompt = content_result.get("image_prompt", "")
        
        # Display generated content
        console.print("\n[green]✓ Caption generated:[/green]")
        console.print(Panel(caption, title="Caption", border_style="green"))
        
        console.print(f"\n[green]✓ Hashtags ({len(hashtags)}):[/green]")
        console.print(" ".join([f"#{tag}" for tag in hashtags]))
        
        # Generate image
        console.print("\n[yellow]Generating image...[/yellow]")
        image_agent = ImageGeneratorAgent()
        image_result = await image_agent.generate_image(image_prompt)
        
        if image_result.get("errors"):
            console.print(f"[red]Error: {image_result['errors'][0]}[/red]")
            return
        
        image_url = image_result.get("image_url", "")
        console.print(f"[green]✓ Image generated:[/green] {image_url}")
        
        # Publish or queue for review
        if auto_publish or not settings.enable_human_review:
            console.print("\n[yellow]Publishing to Instagram...[/yellow]")
            posting_agent = PostingAgent()
            publish_result = await posting_agent.publish_post(
                image_url=image_url,
                caption=caption,
                hashtags=hashtags,
                auto_publish=True
            )
            
            if publish_result.get("errors"):
                console.print(f"[red]Error: {publish_result['errors'][0]}[/red]")
                return
            
            media_id = publish_result.get("instagram_media_id", "")
            console.print(f"\n[bold green]✓ Post published successfully![/bold green]")
            console.print(f"Media ID: {media_id}")
        else:
            console.print("\n[yellow]Post queued for human review[/yellow]")
            console.print("Set AUTO_PUBLISH=true in .env to enable auto-publishing")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        logger.error(f"Error creating post: {e}")


@cli.command()
@click.option("--media-id", "-m", required=True, help="Instagram media ID")
@click.option("--auto-reply", is_flag=True, help="Auto-reply to comments")
def process_comments(media_id: str, auto_reply: bool):
    """Process comments on a post."""
    asyncio.run(_process_comments(media_id, auto_reply))


async def _process_comments(media_id: str, auto_reply: bool):
    """Async implementation of process_comments."""
    console.print(Panel(f"[bold blue]Processing Comments[/bold blue]\nMedia ID: {media_id}", expand=False))
    
    try:
        engagement_agent = EngagementAgent()
        
        console.print("[yellow]Fetching and processing comments...[/yellow]")
        result = await engagement_agent.process_comments(
            media_id=media_id,
            brand_voice=settings.brand_voice,
            post_caption="",  # Could fetch from API
            auto_reply=auto_reply
        )
        
        if result.get("errors"):
            console.print(f"[red]Error: {result['errors'][0]}[/red]")
            return
        
        processed = result.get("processed_comments", [])
        flagged = result.get("flagged_for_review", [])
        
        console.print(f"\n[green]✓ Processed {len(processed)} comments[/green]")
        console.print(f"[yellow]⚠ Flagged {len(flagged)} comments for review[/yellow]")
        
        # Display flagged comments
        if flagged:
            console.print("\n[bold]Flagged Comments:[/bold]")
            for comment in flagged:
                console.print(Panel(
                    f"Comment: {comment.get('text', '')}\n"
                    f"Reason: {comment.get('flag_reason', 'Unknown')}\n"
                    f"Suggested Reply: {comment.get('suggested_reply', '')}",
                    title=f"@{comment.get('username', 'unknown')}",
                    border_style="yellow"
                ))
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        logger.error(f"Error processing comments: {e}")


@cli.command()
def test_connection():
    """Test API connections."""
    asyncio.run(_test_connection())


async def _test_connection():
    """Async implementation of test_connection."""
    console.print(Panel("[bold blue]Testing API Connections[/bold blue]", expand=False))
    
    # Test Google Gemini
    try:
        from src.tools import gemini_llm
        console.print("[yellow]Testing Google Gemini...[/yellow]")
        result = await gemini_llm.generate_caption(
            theme="test",
            brand_voice="friendly",
            target_audience="everyone"
        )
        console.print("[green]✓ Google Gemini: Connected[/green]")
    except Exception as e:
        console.print(f"[red]✗ Google Gemini: {str(e)}[/red]")
    
    # Test Instagram API
    try:
        from src.tools import instagram_api
        console.print("[yellow]Testing Instagram API...[/yellow]")
        account_info = await instagram_api.get_account_info()
        console.print(f"[green]✓ Instagram API: Connected (@{account_info.get('username')})[/green]")
    except Exception as e:
        console.print(f"[red]✗ Instagram API: {str(e)}[/red]")
    
    # Test Nano Banana (Image Generation)
    try:
        from src.tools import image_generator
        console.print("[yellow]Testing Nano Banana (Gemini Image)...[/yellow]")
        console.print(f"[green]✓ Nano Banana: Configured (model: {settings.image_model})[/green]")
    except Exception as e:
        console.print(f"[red]✗ Nano Banana: {str(e)}[/red]")


if __name__ == "__main__":
    cli()
