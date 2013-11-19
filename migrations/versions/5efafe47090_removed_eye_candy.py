# revision identifiers, used by Alembic.
revision = '5efafe47090'
down_revision = '4b3af9d93c97'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('users', u'eye_candy')


def downgrade():
    op.add_column('users', sa.Column(u'eye_candy', sa.BOOLEAN(), server_default='false', nullable=False))
