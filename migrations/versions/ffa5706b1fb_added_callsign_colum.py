# revision identifiers, used by Alembic.
revision = 'ffa5706b1fb'
down_revision = '438d391a92b4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('users', sa.Column('tracking_callsign', sa.Unicode(length=5), nullable=True))


def downgrade():
    op.drop_column('users', 'tracking_callsign')
