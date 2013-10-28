# revision identifiers, used by Alembic.
revision = '2c560c33fab9'
down_revision = '46434b0a4c10'

from alembic import op


def upgrade():
    op.rename_table('tg_user', 'users')
    op.rename_table('tg_group', 'groups')
    op.rename_table('tg_permission', 'permissions')
    op.rename_table('tg_group_permission', 'group_permissions')
    op.rename_table('tg_user_group', 'user_groups')


def downgrade():
    op.rename_table('users', 'tg_user')
    op.rename_table('groups', 'tg_group')
    op.rename_table('permissions', 'tg_permission')
    op.rename_table('group_permissions', 'tg_group_permission')
    op.rename_table('user_groups', 'tg_user_group')
