# revision identifiers, used by Alembic.
revision = '54d325616135'
down_revision = '66650ad3d70'

from alembic import op
import sqlalchemy as sa

FLIGHTS_QUERY = """
UPDATE flights
SET
    {column}_name = subquery.{column}_name,
    {column}_id = NULL
FROM (
    SELECT
        flights.id AS flight_id,
        TRIM(FROM first_name || ' ' || last_name) AS {column}_name
    FROM flights
    JOIN users ON flights.{column}_id = users.id
    WHERE users.password IS NULL
) AS subquery
WHERE flights.id = subquery.flight_id
"""

USERS_QUERY = """
DELETE FROM users
WHERE users.password IS NULL
"""


def upgrade():
    op.execute(FLIGHTS_QUERY.format(column='pilot'))
    op.execute(FLIGHTS_QUERY.format(column='co_pilot'))
    op.execute(USERS_QUERY.format(column='co_pilot'))
    op.alter_column('users', 'password', nullable=False)

def downgrade():
    op.alter_column('users', 'password', nullable=True)
