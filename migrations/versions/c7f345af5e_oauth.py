# revision identifiers, used by Alembic.
revision = 'c7f345af5e'
down_revision = '36d3b413b8d9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refresh_token')
    )


def downgrade():
    op.drop_table('token')
