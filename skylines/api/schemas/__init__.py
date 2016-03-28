from .airport import AirportSchema
from .airspace import AirspaceSchema
from .club import ClubSchema
from .user import UserSchema, AuthenticatedUserSchema
from .wave import WaveSchema

__all__ = [
    AirportSchema,
    AirspaceSchema,
    ClubSchema,
    UserSchema,
    AuthenticatedUserSchema,
    WaveSchema,
]

airport_schema = AirportSchema()
airport_list_schema = AirportSchema(only=('id', 'name', 'elevation', 'location'))

airspace_list_schema = AirspaceSchema(only=('name', '_class', 'top', 'base', 'country'))

user_schema = UserSchema()
user_list_schema = UserSchema(only=('id', 'name', 'first_name', 'last_name'))
current_user_schema = AuthenticatedUserSchema()

wave_list_schema = WaveSchema()
