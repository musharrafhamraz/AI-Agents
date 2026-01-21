"""Seed database with sample data for development and testing"""
import asyncio
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.connection import db_manager
from backend.models.survey import SurveyORM, SurveyStatus, QuestionType
from backend.models.response import ResponseORM, Channel, ValidationStatus
from backend.core.config import settings


async def seed_surveys():
    """Seed sample surveys"""
    print("Seeding surveys...")
    
    surveys = [
        {
            "id": uuid4(),
            "account_id": "demo_account",
            "title": "Customer Satisfaction Survey",
            "description": "Help us improve our products and services",
            "questions": [
                {
                    "id": str(uuid4()),
                    "type": "rating",
                    "text": "How satisfied are you with our product?",
                    "required": True
                },
                {
                    "id": str(uuid4()),
                    "type": "text",
                    "text": "What do you like most about our product?",
                    "required": False
                },
                {
                    "id": str(uuid4()),
                    "type": "multiple_choice",
                    "text": "Would you recommend us to others?",
                    "options": ["Definitely", "Probably", "Not sure", "Probably not", "Definitely not"],
                    "required": True
                }
            ],
            "status": SurveyStatus.ACTIVE
        },
        {
            "id": uuid4(),
            "account_id": "demo_account",
            "title": "Employee Engagement Survey",
            "description": "Share your thoughts about working here",
            "questions": [
                {
                    "id": str(uuid4()),
                    "type": "rating",
                    "text": "How satisfied are you with your current role?",
                    "required": True
                },
                {
                    "id": str(uuid4()),
                    "type": "text",
                    "text": "What motivates you most at work?",
                    "required": False
                }
            ],
            "status": SurveyStatus.ACTIVE
        },
        {
            "id": uuid4(),
            "account_id": "demo_account",
            "title": "Product Feedback Survey",
            "description": "Tell us about your experience with our new features",
            "questions": [
                {
                    "id": str(uuid4()),
                    "type": "rating",
                    "text": "How easy is the product to use?",
                    "required": True
                },
                {
                    "id": str(uuid4()),
                    "type": "multiple_choice",
                    "text": "Which features do you use most?",
                    "options": ["Dashboard", "Reports", "Analytics", "Integrations"],
                    "required": False
                }
            ],
            "status": SurveyStatus.DRAFT
        }
    ]
    
    async with db_manager.session() as session:
        for survey_data in surveys:
            survey = SurveyORM(**survey_data)
            session.add(survey)
        
        await session.commit()
    
    print(f"✓ Seeded {len(surveys)} surveys")
    return surveys


async def seed_responses(surveys):
    """Seed sample responses"""
    print("Seeding responses...")
    
    responses = []
    
    # Add responses for first survey
    survey_id = surveys[0]["id"]
    question_ids = [q["id"] for q in surveys[0]["questions"]]
    
    sample_responses = [
        {
            "id": uuid4(),
            "survey_id": survey_id,
            "respondent_id": "user_001",
            "answers": [
                {"question_id": question_ids[0], "value": 5},
                {"question_id": question_ids[1], "value": "The ease of use and great features"},
                {"question_id": question_ids[2], "value": "Definitely"}
            ],
            "channel": Channel.FORM,
            "validation_status": ValidationStatus.VALIDATED
        },
        {
            "id": uuid4(),
            "survey_id": survey_id,
            "respondent_id": "user_002",
            "answers": [
                {"question_id": question_ids[0], "value": 4},
                {"question_id": question_ids[1], "value": "Good customer support"},
                {"question_id": question_ids[2], "value": "Probably"}
            ],
            "channel": Channel.FORM,
            "validation_status": ValidationStatus.PENDING
        },
        {
            "id": uuid4(),
            "survey_id": survey_id,
            "respondent_id": "user_003",
            "answers": [
                {"question_id": question_ids[0], "value": 5},
                {"question_id": question_ids[1], "value": "Fast performance and reliability"},
                {"question_id": question_ids[2], "value": "Definitely"}
            ],
            "channel": Channel.API,
            "validation_status": ValidationStatus.VALIDATED
        }
    ]
    
    async with db_manager.session() as session:
        for response_data in sample_responses:
            response = ResponseORM(**response_data)
            session.add(response)
            responses.append(response_data)
        
        await session.commit()
    
    print(f"✓ Seeded {len(responses)} responses")
    return responses


async def main():
    """Main seeding function"""
    print("=" * 50)
    print("Validata Database Seeding")
    print("=" * 50)
    print()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✓ Connected to database")
        print()
        
        # Seed data
        surveys = await seed_surveys()
        responses = await seed_responses(surveys)
        
        print()
        print("=" * 50)
        print("✓ Database seeding completed successfully!")
        print("=" * 50)
        print()
        print("Summary:")
        print(f"  - Surveys: {len(surveys)}")
        print(f"  - Responses: {len(responses)}")
        print()
        print("You can now:")
        print("  1. Start the FastAPI backend")
        print("  2. Access the API at http://localhost:8000")
        print("  3. View API docs at http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"\n✗ Seeding failed: {e}")
        sys.exit(1)
    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
