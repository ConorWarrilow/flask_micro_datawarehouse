import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from powerpy.config import Config
from flask_dropzone import Dropzone
from datetime import datetime



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
dropzone = Dropzone()

login_manager.login_view = 'users.login' # redirects you to login if you try accessing account without being logged in
login_manager.login_message_category = 'info' #bootstrap class, this is for the message which pops up when you try accessing 'account' without being logged in (just makes the message look good)

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)


    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    dropzone.init_app(app)
    
    from powerpy.users.routes import users
    app.register_blueprint(users)

    from powerpy.posts.routes import posts
    app.register_blueprint(posts)

    from powerpy.main.routes import main
    app.register_blueprint(main)

    from powerpy.databases.routes import databases
    app.register_blueprint(databases)

    from powerpy.errors.handlers import errors
    app.register_blueprint(errors)

    from powerpy.models import Database
    @app.context_processor
    def inject_global_total_databases():
        global_total_databases = Database.query.count()  # Get the total number of databases
        return {'global_total_databases': global_total_databases}

    from powerpy.models import User
    @app.context_processor
    def inject_global_total_users():
        global_total_users = User.query.count()  # Get the total number of databases
        return {'global_total_users': global_total_users}
    
    from powerpy.models import Schema
    @app.context_processor
    def inject_global_total_schemas():
        global_total_schemas = Schema.query.count()  # Get the total number of databases
        return {'global_total_schemas': global_total_schemas}
    
    from flask_login import current_user
    @app.context_processor
    def compute_usage():
        compute_usage = current_user.compute_usage
        return {'compute_usage': int(compute_usage/60)}

    with app.app_context():
        db.create_all()

    return app

