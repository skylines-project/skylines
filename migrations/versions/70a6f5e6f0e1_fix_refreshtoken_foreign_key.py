# revision identifiers, used by Alembic.
revision = "70a6f5e6f0e1"
down_revision = "596364f1391a"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("token", "user_id", existing_type=sa.INTEGER(), nullable=False)
    op.drop_constraint(u"token_user_id_fkey", "token", type_="foreignkey")
    op.create_foreign_key(
        None, "token", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )


def downgrade():
    op.drop_constraint(None, "token", type_="foreignkey")
    op.create_foreign_key(u"token_user_id_fkey", "token", "users", ["user_id"], ["id"])
    op.alter_column("token", "user_id", existing_type=sa.INTEGER(), nullable=True)
