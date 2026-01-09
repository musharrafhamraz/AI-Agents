"""Automated Instagram posting scheduler."""
import asyncio
import schedule
import time
from datetime import datetime
from loguru import logger
from src.agents import ContentCreatorAgent, ImageGeneratorAgent, PostingAgent
from src.config import settings
import random

# Content themes for variety
CONTENT_THEMES = [
    "morning motivation",
    "inspirational quotes",
    "emotional reflection",
    "romantic thoughts",
    "life lessons",
    "self-love and growth",
    "mindfulness and peace",
    "gratitude and positivity",
    "overcoming challenges",
    "dreams and aspirations",
    "inner strength",
    "beautiful moments",
    "heartfelt emotions",
    "personal growth",
    "finding happiness"
]


async def create_and_post():
    """Create and post content to Instagram."""
    try:
        # Select random theme for variety
        theme = random.choice(CONTENT_THEMES)
        
        logger.info(f"Starting scheduled post creation with theme: {theme}")
        
        # Step 1: Generate content
        content_agent = ContentCreatorAgent()
        content_result = await content_agent.create_content(
            theme=theme,
            brand_voice=settings.brand_voice,
            target_audience=settings.target_audience,
            brand_name=settings.brand_name
        )
        
        if content_result.get("errors"):
            logger.error(f"Content generation failed: {content_result['errors']}")
            return
        
        caption = content_result.get("caption", "")
        hashtags = content_result.get("hashtags", [])
        image_prompt = content_result.get("image_prompt", "")
        
        logger.info(f"✓ Content generated: {len(caption)} chars, {len(hashtags)} hashtags")
        
        # Step 2: Generate image
        image_agent = ImageGeneratorAgent()
        image_result = await image_agent.generate_image(image_prompt)
        
        if image_result.get("errors"):
            logger.error(f"Image generation failed: {image_result['errors']}")
            return
        
        image_url = image_result.get("image_url", "")
        logger.info(f"✓ Image generated: {image_url}")
        
        # Step 3: Publish to Instagram
        posting_agent = PostingAgent()
        publish_result = await posting_agent.publish_post(
            image_url=image_url,
            caption=caption,
            hashtags=hashtags,
            auto_publish=True
        )
        
        if publish_result.get("errors"):
            logger.error(f"Publishing failed: {publish_result['errors']}")
            return
        
        media_id = publish_result.get("instagram_media_id", "")
        logger.info(f"✓ Successfully published post! Media ID: {media_id}")
        
        print(f"\n{'='*60}")
        print(f"✅ POST PUBLISHED SUCCESSFULLY!")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Theme: {theme}")
        print(f"Media ID: {media_id}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        logger.error(f"Error in scheduled post: {e}")
        print(f"\n❌ POST FAILED: {e}\n")


def run_scheduled_post():
    """Wrapper to run async function in sync context."""
    asyncio.run(create_and_post())


def setup_schedule():
    """Set up the posting schedule."""
    
    # MONDAY - 4 posts
    schedule.every().monday.at("09:00").do(run_scheduled_post)
    schedule.every().monday.at("13:00").do(run_scheduled_post)
    schedule.every().monday.at("17:00").do(run_scheduled_post)
    schedule.every().monday.at("20:00").do(run_scheduled_post)
    
    # TUESDAY - 3 posts
    schedule.every().tuesday.at("10:00").do(run_scheduled_post)
    schedule.every().tuesday.at("14:00").do(run_scheduled_post)
    schedule.every().tuesday.at("19:00").do(run_scheduled_post)
    
    # WEDNESDAY - 5 posts
    schedule.every().wednesday.at("08:00").do(run_scheduled_post)
    schedule.every().wednesday.at("11:00").do(run_scheduled_post)
    schedule.every().wednesday.at("14:00").do(run_scheduled_post)
    schedule.every().wednesday.at("17:00").do(run_scheduled_post)
    schedule.every().wednesday.at("21:00").do(run_scheduled_post)
    
    # THURSDAY - 4 posts
    schedule.every().thursday.at("09:30").do(run_scheduled_post)
    schedule.every().thursday.at("13:30").do(run_scheduled_post)
    schedule.every().thursday.at("16:30").do(run_scheduled_post)
    schedule.every().thursday.at("20:30").do(run_scheduled_post)
    
    # FRIDAY - 5 posts
    schedule.every().friday.at("08:30").do(run_scheduled_post)
    schedule.every().friday.at("11:30").do(run_scheduled_post)
    schedule.every().friday.at("14:30").do(run_scheduled_post)
    schedule.every().friday.at("18:00").do(run_scheduled_post)
    schedule.every().friday.at("21:30").do(run_scheduled_post)
    
    # SATURDAY - 4 posts (weekend - different times)
    schedule.every().saturday.at("10:00").do(run_scheduled_post)
    schedule.every().saturday.at("14:00").do(run_scheduled_post)
    schedule.every().saturday.at("18:00").do(run_scheduled_post)
    schedule.every().saturday.at("21:00").do(run_scheduled_post)
    
    # SUNDAY - 3 posts (relaxed day)
    schedule.every().sunday.at("11:00").do(run_scheduled_post)
    schedule.every().sunday.at("16:00").do(run_scheduled_post)
    schedule.every().sunday.at("20:00").do(run_scheduled_post)
    
    logger.info("✓ Schedule configured successfully!")
    print("\n" + "="*60)
    print("📅 INSTAGRAM POSTING SCHEDULE")
    print("="*60)
    print("Monday:    09:00, 13:00, 17:00, 20:00 (4 posts)")
    print("Tuesday:   10:00, 14:00, 19:00 (3 posts)")
    print("Wednesday: 08:00, 11:00, 14:00, 17:00, 21:00 (5 posts)")
    print("Thursday:  09:30, 13:30, 16:30, 20:30 (4 posts)")
    print("Friday:    08:30, 11:30, 14:30, 18:00, 21:30 (5 posts)")
    print("Saturday:  10:00, 14:00, 18:00, 21:00 (4 posts)")
    print("Sunday:    11:00, 16:00, 20:00 (3 posts)")
    print("="*60)
    print(f"Total: 28 posts per week")
    print(f"Timezone: {settings.timezone}")
    print(f"Brand: {settings.brand_name}")
    print("="*60 + "\n")


def main():
    """Main scheduler loop."""
    print("\n🚀 Starting Instagram Automation Scheduler...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set up schedule
    setup_schedule()
    
    print("\n✅ Scheduler is running! Press Ctrl+C to stop.\n")
    
    # Run scheduler loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n⏹️  Scheduler stopped by user.")
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()
