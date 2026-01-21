"""Property-based tests for database models and referential integrity

Feature: validata-platform, Property 9: Database Referential Integrity
"""
import pytest
from hypothesis import given, strategies as st, settings
from uuid import uuid4
from datetime import datetime

from backend.models.survey import SurveyORM, SurveyStatus
from backend.models.response import ResponseORM, Channel, ValidationStatus
from backend.models.validation import ValidationORM
from backend.database.connection import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_engine():
    """Create a test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session"""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


# Hypothesis strategies for generating test data
@st.composite
def survey_data(draw):
    """Generate random survey data"""
    return {
        "id": uuid4(),
        "account_id": draw(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_characters=['\x00']))),
        "title": draw(st.text(min_size=1, max_size=500, alphabet=st.characters(blacklist_characters=['\x00']))),
        "description": draw(st.one_of(st.none(), st.text(max_size=1000, alphabet=st.characters(blacklist_characters=['\x00'])))),
        "questions": [{"id": str(uuid4()), "type": "text", "text": "Sample question", "required": True}],
        "status": draw(st.sampled_from(list(SurveyStatus))),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@st.composite
def response_data(draw, survey_id):
    """Generate random response data for a given survey"""
    return {
        "id": uuid4(),
        "survey_id": survey_id,
        "respondent_id": draw(st.one_of(st.none(), st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_characters=['\x00'])))),
        "answers": [{"question_id": str(uuid4()), "value": "Sample answer"}],
        "channel": draw(st.sampled_from(list(Channel))),
        "submitted_at": datetime.utcnow(),
        "validation_status": draw(st.sampled_from(list(ValidationStatus))),
    }


@pytest.mark.asyncio
@pytest.mark.property
@settings(max_examples=100, deadline=None)
@given(survey=survey_data(), response_gen=st.data())
async def test_response_referential_integrity(survey, response_gen, test_session):
    """
    Property 9: Database Referential Integrity
    
    For any response stored in the database, the survey_id should reference 
    an existing survey in the surveys table.
    
    Validates: Requirements 8.7
    """
    # Create a survey first
    survey_orm = SurveyORM(**survey)
    test_session.add(survey_orm)
    await test_session.commit()
    await test_session.refresh(survey_orm)
    
    # Generate response data with valid survey_id
    response = response_gen.draw(response_data(survey_orm.id))
    
    # Create response with valid survey_id
    response_orm = ResponseORM(**response)
    test_session.add(response_orm)
    await test_session.commit()
    await test_session.refresh(response_orm)
    
    # Verify the response was created and references the correct survey
    assert response_orm.survey_id == survey_orm.id
    assert response_orm.id is not None


@pytest.mark.asyncio
@pytest.mark.property
async def test_response_invalid_survey_id_fails(test_session):
    """
    Property 9: Database Referential Integrity (negative test)
    
    For any response with an invalid survey_id (non-existent survey),
    the database should reject the insertion due to foreign key constraint.
    
    Validates: Requirements 8.7
    """
    # Try to create a response with non-existent survey_id
    invalid_response = ResponseORM(
        id=uuid4(),
        survey_id=uuid4(),  # Non-existent survey
        answers=[{"question_id": str(uuid4()), "value": "Test"}],
        channel=Channel.FORM,
        validation_status=ValidationStatus.PENDING,
    )
    
    test_session.add(invalid_response)
    
    # This should raise an IntegrityError due to foreign key constraint
    with pytest.raises(IntegrityError):
        await test_session.commit()


@pytest.mark.asyncio
@pytest.mark.property
@settings(max_examples=100, deadline=None)
@given(survey=survey_data(), response_gen=st.data())
async def test_validation_referential_integrity(survey, response_gen, test_session):
    """
    Property 9: Database Referential Integrity (validation table)
    
    For any validation stored in the database, the response_id should reference 
    an existing response in the responses table.
    
    Validates: Requirements 8.7
    """
    # Create survey
    survey_orm = SurveyORM(**survey)
    test_session.add(survey_orm)
    await test_session.commit()
    await test_session.refresh(survey_orm)
    
    # Create response
    response = response_gen.draw(response_data(survey_orm.id))
    response_orm = ResponseORM(**response)
    test_session.add(response_orm)
    await test_session.commit()
    await test_session.refresh(response_orm)
    
    # Create validation
    validation_orm = ValidationORM(
        id=uuid4(),
        response_id=response_orm.id,
        layer_results=[
            {
                "layer": i,
                "layer_name": f"Layer {i}",
                "passed": True,
                "reasoning": "Test",
                "confidence": 0.9,
                "timestamp": datetime.utcnow().isoformat()
            }
            for i in range(1, 8)
        ],
        final_status="validated",
        confidence_score=0.9,
    )
    
    test_session.add(validation_orm)
    await test_session.commit()
    await test_session.refresh(validation_orm)
    
    # Verify the validation was created and references the correct response
    assert validation_orm.response_id == response_orm.id
    assert validation_orm.id is not None


@pytest.mark.asyncio
@pytest.mark.property
@settings(max_examples=50, deadline=None)
@given(survey=survey_data(), response_gen=st.data())
async def test_cascade_delete_maintains_integrity(survey, response_gen, test_session):
    """
    Property 9: Database Referential Integrity (cascade delete)
    
    When a survey is deleted, all associated responses should also be deleted
    to maintain referential integrity.
    
    Validates: Requirements 8.7
    """
    # Create survey
    survey_orm = SurveyORM(**survey)
    test_session.add(survey_orm)
    await test_session.commit()
    await test_session.refresh(survey_orm)
    
    # Create response
    response = response_gen.draw(response_data(survey_orm.id))
    response_orm = ResponseORM(**response)
    test_session.add(response_orm)
    await test_session.commit()
    
    response_id = response_orm.id
    
    # Delete the survey
    await test_session.delete(survey_orm)
    await test_session.commit()
    
    # Verify the response was also deleted (cascade)
    from sqlalchemy import select
    result = await test_session.execute(
        select(ResponseORM).where(ResponseORM.id == response_id)
    )
    deleted_response = result.scalar_one_or_none()
    
    assert deleted_response is None, "Response should be deleted when survey is deleted"
