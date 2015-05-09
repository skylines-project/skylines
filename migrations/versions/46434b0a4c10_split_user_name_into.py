# revision identifiers, used by Alembic.
revision = '46434b0a4c10'
down_revision = None

from alembic import op
import sqlalchemy as sa

from skylines.database import db


users = sa.sql.table(
    'tg_user',
    sa.sql.column('id', sa.Integer),
    sa.sql.column('first_name', sa.Unicode),
    sa.sql.column('last_name', sa.Unicode),
)


def upgrade():
    op.alter_column('tg_user', 'name', new_column_name='first_name')
    op.add_column('tg_user', sa.Column('last_name', sa.Unicode(length=255), nullable=True))

    for row in op.get_bind().execute(users.select()):
        id = row[users.c.id]
        name = row[users.c.first_name]

        n = name.split(' ')
        if len(n) != 2:
            continue

        first_name = n[0]
        last_name = n[1]

        print ('Converting %s -> "%s", "%s"' % (name, first_name, last_name)).encode('unicode_escape')

        op.execute(
            users.update().where(users.c.id == id).values({
                'first_name': first_name,
                'last_name': last_name,
            })
        )


def downgrade():
    for row in op.get_bind().execute(users.select()):
        id = row[users.c.id]
        first_name = row[users.c.first_name]
        last_name = row[users.c.last_name]

        if last_name:
            name = first_name + ' ' + last_name
            print ('Converting "%s", "%s" -> %s' % (first_name, last_name, name)).encode('unicode_escape')

            op.execute(
                users.update().where(users.c.id == id).values({
                    'first_name': name,
                })
            )

    db.session.flush()

    op.alter_column('tg_user', 'first_name', new_column_name='name')
    op.drop_column('tg_user', 'last_name')
