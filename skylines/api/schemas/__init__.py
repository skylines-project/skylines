from .airport import AirportSchema
from .airspace import AirspaceSchema
from .user import UserSchema
from .wave import WaveSchema

airport_schema = AirportSchema()
airport_list_schema = AirportSchema(only=('id', 'name', 'elevation', 'location'))

airspace_list_schema = AirspaceSchema(only=('name', '_class', 'top', 'base', 'country'))

user_schema = UserSchema(exclude=('email_address', 'tracking_key'))
user_list_schema = UserSchema(only=('id', 'name', 'first_name', 'last_name'))
current_user_schema = UserSchema()

wave_list_schema = WaveSchema()
