# revision identifiers, used by Alembic.
revision = '8a8e921cb88'
down_revision = '54d325616135'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('flights', sa.Column('scoring_start_time', sa.DateTime(), nullable=True))
    op.add_column('flights', sa.Column('scoring_end_time', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('flights', 'scoring_start_time')
    op.drop_column('flights', 'scoring_end_time')
