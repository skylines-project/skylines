# revision identifiers, used by Alembic.
revision = '3e82b37a4989'
down_revision = '5efafe47090'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('users', 'tracking_key',
               existing_type=sa.BIGINT(),
               nullable=False)


def downgrade():
    op.alter_column('users', 'tracking_key',
               existing_type=sa.BIGINT(),
               nullable=True)
