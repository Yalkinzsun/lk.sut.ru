from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cb02820a3e676h9dgh5fd9g87e3f7a35b3f5b'

import bonch.main
