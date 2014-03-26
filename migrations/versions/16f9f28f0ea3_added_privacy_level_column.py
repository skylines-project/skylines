# revision identifiers, used by Alembic.
revision = '16f9f28f0ea3'
down_revision = '8a8e921cb88'

from alembic import op
import sqlalchemy as sa


flights = sa.sql.table(
    'flights',
    sa.sql.column('privacy_level', sa.SmallInteger),
)


def upgrade():
    op.add_column('flights', sa.Column('privacy_level', sa.SmallInteger()))

    op.execute(flights.update().values({
        'privacy_level': 0,
    }))

    op.alter_column('flights', 'privacy_level', nullable=False)


def downgrade():
    op.drop_column('flights', 'privacy_level')
