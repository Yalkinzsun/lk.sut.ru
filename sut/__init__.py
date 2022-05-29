from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy



users_db = SQLAlchemy()

def create_app():
    app = Flask()
    users_db.init_app(app)

    from .data_models import User
    with app.app_context():
        users_db.create_all()

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SECRET_KEY'] = 'cb02820a3e676h9dgh5fd9g87e3f7a35b3f5b'

users_db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


from .data_models import User
from .auth import auth as auth_blueprint
from .main import main as main_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


import sut.main
