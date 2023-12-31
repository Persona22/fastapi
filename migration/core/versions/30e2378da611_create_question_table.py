"""Create question table

Revision ID: 30e2378da611
Revises: ba852a5526d6
Create Date: 2023-09-17 14:59:51.257162

"""
from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy import func, text

# revision identifiers, used by Alembic.
revision: str = "30e2378da611"
down_revision: str | None = "f8ab1017d1df"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "question",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("external_id", sa.UUID, unique=True, default=uuid4, nullable=False),
        sa.Column("create_datetime", sa.DateTime, server_default=func.now(), nullable=False),
        sa.Column("delete_datetime", sa.DateTime, nullable=True),
        sa.Column("answer_count", sa.Integer, default=0, server_default=text('0'), nullable=False),
    )
    op.create_table(
        "question_translation",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("external_id", sa.UUID, unique=True, default=uuid4, nullable=False),
        sa.Column("create_datetime", sa.DateTime, server_default=func.now(), nullable=False),
        sa.Column("delete_datetime", sa.DateTime, nullable=True),
        sa.Column("text", sa.VARCHAR(length=3000), nullable=False),
        sa.Column("question_id", sa.Integer, sa.ForeignKey("question.id"), nullable=False),
        sa.Column("language_id", sa.Integer, sa.ForeignKey("language.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("question_translation")
    op.drop_table("question")
