# revision identifiers, used by Alembic.
revision = '36d3b413b8d9'
down_revision = '20f18f40fb62'

from alembic import op
import sqlalchemy as sa
from geoalchemy2.types import Geometry


def upgrade():
    op.create_table('contest_legs',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('flight_id', sa.Integer(), nullable=False),
                    sa.Column('contest_type', sa.String(), nullable=False),
                    sa.Column('trace_type', sa.String(), nullable=False),
                    sa.Column('distance', sa.Integer(), nullable=True),
                    sa.Column('cruise_height', sa.Integer(), nullable=True),
                    sa.Column('cruise_distance', sa.Integer(), nullable=True),
                    sa.Column('cruise_duration', sa.Interval(), nullable=True),
                    sa.Column('climb_height', sa.Integer(), nullable=True),
                    sa.Column('climb_duration', sa.Interval(), nullable=True),
                    sa.Column('start_height', sa.Integer(), nullable=True),
                    sa.Column('end_height', sa.Integer(), nullable=True),
                    sa.Column('start_time', sa.DateTime(), nullable=False),
                    sa.Column('end_time', sa.DateTime(), nullable=False),
                    sa.Column('start_location', Geometry(geometry_type='POINT', srid=4326), nullable=True),
                    sa.Column('end_location', Geometry(geometry_type='POINT', srid=4326), nullable=True),
                    sa.ForeignKeyConstraint(['flight_id'], ['flights.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_contest_legs_flight_id', 'contest_legs', ['flight_id'], unique=False)


def downgrade():
    op.drop_index('ix_contest_legs_flight_id', table_name='contest_legs')
    op.drop_table('contest_legs')
