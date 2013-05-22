from skylines import app
from .model import User

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello_world():
    return 'Hello World!'

@app.route('/users/')
def user_list():
    return ', '.join([user.name for user in User.query()])
