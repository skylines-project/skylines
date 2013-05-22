from flask import Flask
app = Flask(__name__, static_folder='public')

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello_world():
    app.logger.warning('An error occurred')
    return 'Hello World!'
