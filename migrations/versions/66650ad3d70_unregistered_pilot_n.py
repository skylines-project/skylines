# revision identifiers, used by Alembic.
revision = '66650ad3d70'
down_revision = '3e82b37a4989'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('flights', sa.Column('pilot_name', sa.Unicode(length=255), nullable=True))
    op.add_column('flights', sa.Column('co_pilot_name', sa.Unicode(length=255), nullable=True))


def downgrade():
    op.drop_column('flights', 'pilot_name')
    op.drop_column('flights', 'co_pilot_name')
