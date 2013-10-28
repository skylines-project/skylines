# revision identifiers, used by Alembic.
revision = '438d391a92b4'
down_revision = '2c560c33fab9'

from alembic import op
import sqlalchemy as sa

users = sa.sql.table(
    'users',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('admin', sa.Boolean),
)

groups = sa.sql.table(
    'groups',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('group_name', sa.Unicode),
)

user_groups = sa.sql.table(
    'user_groups',
    sa.sql.column('user_id', sa.Integer),
    sa.sql.column('group_id', sa.Integer)
)


def upgrade():
    op.add_column('users', sa.Column(
        'admin', sa.Boolean(), nullable=False, server_default='0'))

    for row in op.get_bind().execute(groups.select()):
        if row[groups.c.group_name] == 'managers':
            managers_group_id = row[groups.c.id]
            break

    query = user_groups.select().where(user_groups.c.group_id==managers_group_id)
    for row in op.get_bind().execute(query):
        op.execute(users.update() \
            .where(users.c.id==row[user_groups.c.user_id]) \
            .values({
                'admin': True,
            }))

    op.drop_table('group_permissions')
    op.drop_table('permissions')
    op.drop_table('user_groups')
    op.drop_table('groups')


def downgrade():
    pass
