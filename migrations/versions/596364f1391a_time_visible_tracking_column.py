# revision identifiers, used by Alembic.
revision = "596364f1391a"
down_revision = "c7f345af5e"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


fixes = table(
    "tracking_fixes", column("time", sa.DateTime), column("time_visible", sa.DateTime)
)


def upgrade():
    op.add_column(
        "tracking_fixes",
        sa.Column(
            "time_visible",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    op.execute(fixes.update().values(time_visible=fixes.c.time))


def downgrade():
    op.drop_column("tracking_fixes", "time_visible")
