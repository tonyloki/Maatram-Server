"""Add composite indexes for high-throughput query performance.

Revision ID: e4f5a6b7c8d9
Revises: c8e1f42a9012
Create Date: 2026-11-15 14:00:00.000000
"""

from alembic import op

revision = "e4f5a6b7c8d9"
down_revision = "c8e1f42a9012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Composite index for pending/reviewed applications ordered by submission time
    op.create_index(
        "ix_volunteer_applications_status_submitted",
        "volunteer_applications",
        ["status", "submitted_at"],
        unique=False,
    )

    # 2. Composite index for volunteer points ledger pagination
    op.create_index(
        "ix_point_transactions_volunteer_created",
        "point_transactions",
        ["volunteer_profile_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_point_transactions_volunteer_created",
        table_name="point_transactions",
    )
    op.drop_index(
        "ix_volunteer_applications_status_submitted",
        table_name="volunteer_applications",
    )

