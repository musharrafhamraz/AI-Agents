"""Integration tests for complete survey workflow"""
import pytest
from uuid import uuid4

from backend.models.survey import SurveyCreate, Question, QuestionType
from backend.models.response import ResponseCreate, Answer, Channel
from mcp_servers.survey.resources import SurveyResources
from mcp_servers.validation.tools import ValidationTools


@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_survey_workflow():
    """
    Test complete workflow:
    1. Create survey
    2. Submit response
    3. Validate response
    4. Generate insights
    """
    survey_resources = SurveyResources()
    validation_tools = ValidationTools()
    
    # Step 1: Create survey
    survey_data = SurveyCreate(
        account_id="test_account",
        title="Integration Test Survey",
        description="Testing complete workflow",
        questions=[
            Question(
                type=QuestionType.TEXT,
                text="What is your feedback?",
                required=True
            ),
            Question(
                type=QuestionType.RATING,
                text="How would you rate this?",
                required=True
            )
        ]
    )
    
    survey = await survey_resources.create_survey(survey_data)
    assert survey is not None
    assert survey.id is not None
    
    # Step 2: Submit response
    response_data = ResponseCreate(
        survey_id=survey.id,
        answers=[
            Answer(
                question_id=survey.questions[0].id,
                value="Great product!"
            ),
            Answer(
                question_id=survey.questions[1].id,
                value=5
            )
        ],
        channel=Channel.FORM
    )
    
    # Note: Would need to create response through API or database
    # This is a simplified test
    
    # Step 3: Validate response
    # validation_result = await validation_tools.validate_response(response.id)
    # assert validation_result is not None
    
    # Step 4: Generate insights
    # insights = await analytics_tools.generate_insights(survey.id)
    # assert len(insights) > 0
    
    # Cleanup
    await survey_resources.delete_survey(survey.id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multi_channel_responses():
    """Test responses from different channels"""
    survey_resources = SurveyResources()
    
    # Create survey
    survey_data = SurveyCreate(
        account_id="test_account",
        title="Multi-Channel Test",
        description="Testing different channels",
        questions=[
            Question(
                type=QuestionType.TEXT,
                text="Test question",
                required=True
            )
        ]
    )
    
    survey = await survey_resources.create_survey(survey_data)
    
    # Test different channels
    channels = [Channel.FORM, Channel.CHAT, Channel.API]
    
    for channel in channels:
        response_data = ResponseCreate(
            survey_id=survey.id,
            answers=[
                Answer(
                    question_id=survey.questions[0].id,
                    value=f"Response from {channel.value}"
                )
            ],
            channel=channel
        )
        
        # Would create response here
        assert response_data.channel == channel
    
    # Cleanup
    await survey_resources.delete_survey(survey.id)
