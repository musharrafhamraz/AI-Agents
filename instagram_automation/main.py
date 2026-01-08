"""Instagram Automation Agent - Main entry point."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli import cli
from loguru import logger

# Configure logging
logger.add(
    "logs/instagram_agent_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)

if __name__ == "__main__":
    cli()
