from flask import Flask
app = Flask(__name__, static_folder='public')

import skylines.views
