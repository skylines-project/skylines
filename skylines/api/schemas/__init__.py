from .airspace import AirspaceSchema
from .user import UserSchema, AuthenticatedUserSchema
from .wave import WaveSchema

__all__ = [
    AirspaceSchema,
    UserSchema,
    AuthenticatedUserSchema,
    WaveSchema,
]

airspace_list_schema = AirspaceSchema(only=('name', '_class', 'top', 'base', 'country'))

user_schema = UserSchema()
user_list_schema = UserSchema(only=('id', 'name', 'first_name', 'last_name'))
current_user_schema = AuthenticatedUserSchema()

wave_list_schema = WaveSchema()
