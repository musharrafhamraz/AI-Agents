"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create surveys table
    op.create_table(
        'surveys',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('questions', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'CLOSED', name='surveystatus'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_surveys_account_id'), 'surveys', ['account_id'], unique=False)
    
    # Create responses table
    op.create_table(
        'responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('survey_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('respondent_id', sa.String(length=255), nullable=True),
        sa.Column('answers', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('channel', sa.Enum('FORM', 'CHAT', 'API', name='channel'), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
        sa.Column('validation_status', sa.Enum('PENDING', 'VALIDATED', 'FAILED', name='validationstatus'), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_responses_survey_id'), 'responses', ['survey_id'], unique=False)
    op.create_index(op.f('ix_responses_respondent_id'), 'responses', ['respondent_id'], unique=False)
    
    # Create validations table
    op.create_table(
        'validations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('response_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('layer_results', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('final_status', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('validated_at', sa.DateTime(), nullable=False),
        sa.Column('audit_log', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['response_id'], ['responses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('response_id')
    )
    op.create_index(op.f('ix_validations_response_id'), 'validations', ['response_id'], unique=True)
    
    # Create insights table
    op.create_table(
        'insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('survey_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('insight_text', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('supporting_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('trace', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_insights_survey_id'), 'insights', ['survey_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_insights_survey_id'), table_name='insights')
    op.drop_table('insights')
    op.drop_index(op.f('ix_validations_response_id'), table_name='validations')
    op.drop_table('validations')
    op.drop_index(op.f('ix_responses_respondent_id'), table_name='responses')
    op.drop_index(op.f('ix_responses_survey_id'), table_name='responses')
    op.drop_table('responses')
    op.drop_index(op.f('ix_surveys_account_id'), table_name='surveys')
    op.drop_table('surveys')
    op.execute('DROP TYPE surveystatus')
    op.execute('DROP TYPE channel')
    op.execute('DROP TYPE validationstatus')
