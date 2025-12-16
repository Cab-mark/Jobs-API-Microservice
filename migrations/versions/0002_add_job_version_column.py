"""Add version column to jobs table."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_job_version_column"
down_revision = "0001_create_jobs_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.alter_column("jobs", "version", server_default=None)


def downgrade() -> None:
    op.drop_column("jobs", "version")
