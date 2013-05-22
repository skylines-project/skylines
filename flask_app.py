from flask import Flask
app = Flask('skylines', static_folder='public')

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.debug = True
    app.run()
