# revision identifiers, used by Alembic.
revision = '4e33b96ffceb'
down_revision = '596364f1391a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('upload_permission_club', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('users', 'upload_permission_club')
