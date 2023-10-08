from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretKey'

    PASSWORD = "gcloudPassword"

    PUBLIC_IP_ADDRESS = "gcloudPublicIPAddress"

    DBNAME = "gcloudDatabaseName"

    PROJECT_ID = "gcloudProjectId"

    INSTANCE_NAME = "gcloudInstanceName"

    IS_LOCAL = True

    # For local deployment creates local database instead of connecting to gcloud database
    if IS_LOCAL:
        app_root = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(app_root, 'database.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    db.init_app(app)

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    with app.app_context():
        db.create_all()

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    return app
