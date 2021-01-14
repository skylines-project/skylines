# revision identifiers, used by Alembic.
revision = "58325345d375"
down_revision = "70a6f5e6f0e1"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


def upgrade():
    op.add_column("igc_files", sa.Column("weglide_data", JSONB(), nullable=True))
    op.add_column("igc_files", sa.Column("weglide_status", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("igc_files", "weglide_status")
    op.drop_column("igc_files", "weglide_data")
