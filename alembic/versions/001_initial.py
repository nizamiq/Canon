"""Initial Canon tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create prompts table
    op.create_table(
        'canon_prompts',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('name', sa.Text(), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('current_version', sa.Integer(), default=1, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_canon_prompts_name', 'canon_prompts', ['name'], unique=True)

    # Create prompt_versions table
    op.create_table(
        'canon_prompt_versions',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('prompt_id', sa.Text(), sa.ForeignKey('canon_prompts.id'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.Text(), nullable=False),
    )
    op.create_index('ix_canon_prompt_versions_prompt_id', 'canon_prompt_versions', ['prompt_id'])

    # Create version_tags table
    op.create_table(
        'canon_version_tags',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('prompt_id', sa.Text(), sa.ForeignKey('canon_prompts.id'), nullable=False),
        sa.Column('tag_name', sa.Text(), nullable=False),
        sa.Column('version_id', sa.Text(), sa.ForeignKey('canon_prompt_versions.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_canon_version_tags_prompt_id', 'canon_version_tags', ['prompt_id'])

    # Create audit_log table
    op.create_table(
        'canon_audit_log',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('action', sa.Text(), nullable=False),
        sa.Column('resource_type', sa.Text(), nullable=False),
        sa.Column('resource_id', sa.Text(), nullable=False),
        sa.Column('actor', sa.Text(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_canon_audit_log_resource', 'canon_audit_log', ['resource_type', 'resource_id'])


def downgrade() -> None:
    op.drop_index('ix_canon_audit_log_resource', table_name='canon_audit_log')
    op.drop_table('canon_audit_log')
    
    op.drop_index('ix_canon_version_tags_prompt_id', table_name='canon_version_tags')
    op.drop_table('canon_version_tags')
    
    op.drop_index('ix_canon_prompt_versions_prompt_id', table_name='canon_prompt_versions')
    op.drop_table('canon_prompt_versions')
    
    op.drop_index('ix_canon_prompts_name', table_name='canon_prompts')
    op.drop_table('canon_prompts')
