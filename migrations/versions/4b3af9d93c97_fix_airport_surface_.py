# revision identifiers, used by Alembic.
revision = '4b3af9d93c97'
down_revision = '1f33435e1753'

from alembic import op
import sqlalchemy as sa

airports = sa.sql.table(
    'airports',
    sa.sql.column('surface', sa.String(10)),
)


def upgrade():
    op.execute(
        airports.update().where(airports.c.surface == 'gras').values({
            'surface': 'grass',
        })
    )

def downgrade():
    op.execute(
        airports.update().where(airports.c.surface == 'grass').values({
            'surface': 'gras',
        })
    )
