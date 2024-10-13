from powerpy import db, login_manager
from datetime import datetime, timezone, timedelta
from flask_login import UserMixin
import random
from flask import current_app
#from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import jwt

@login_manager.user_loader
def load_user(user_id):
    """For reloading the user for the user_id stored in the session, required for loading a user by id"""
    return User.query.get(int(user_id))


def random_image():
    # Define a list of possible image filenames
    images = ['default.jpg', 'default2.jpg', 'default3.jpg']
    return random.choice(images)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default=random_image)
    password = db.Column(db.String(60), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    #compute_usage = db.Column(db.Float, nullable = True, default=0.0)
    posts = db.relationship('Post', backref='author', lazy=True)
    databases = db.relationship('Database', backref='owner', lazy=True) 
    dashboards = db.relationship('Dashboard', backref='owner', lazy=True) 
    schemas = db.relationship('Schema', backref='owner', lazy=True) 
    schema_tables = db.relationship('SchemaTable', backref='owner', lazy=True)
    worksheets = db.relationship('Worksheet', backref='owner', lazy=True)
    folders = db.relationship('Folder', backref='owner', lazy=True)

    def get_reset_token(self, expired_sec=1800):
        s = jwt.encode({"exp": datetime.now(tz=timezone.utc) + timedelta(
            seconds=expired_sec), "user_id": self.id}, current_app.config['SECRET_KEY'], algorithm="HS256")
        return s

    @staticmethod
    def verify_reset_token(token):
        try:
            s = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = s['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    

    # new 
    def get_activation_token(self, expires_sec=1800):
        s = jwt.encode(
            {"exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_sec), "user_id": self.id},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return s
    # new
    @staticmethod
    def verify_activation_token(token):
        try:
            s = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = s['user_id']
        except:
            return None
        return User.query.get(user_id)




def worksheet_message(username, creation_time):
    return f"""-- Welcome, {username}!
-- This worksheet was created on {creation_time.strftime('%Y-%m-%d %I:%M %p')}.

-- You can start writing your SQL queries below.

-- Example: SELECT * FROM your_table LIMIT 10;

-- Enjoy querying!
"""

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Lowercase u for user since we're referencing the table name and column
    

class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False)
    config = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(100), nullable=True, default= lambda: datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M %p'))
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_saved = db.Column(db.DateTime, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    #access_permissions = db.Column(db.Text, nullable=True)

class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    database_name = db.Column(db.String(100), nullable=False)
    database_description = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    #access_permissions = db.Column(db.Text, nullable=True)

class Schema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    database_id = db.Column(db.Integer, db.ForeignKey('database.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class SchemaTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'), nullable=False)
    database_id = db.Column(db.Integer, db.ForeignKey('database.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    table_columns = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class DataFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    database_id = db.Column(db.Integer, db.ForeignKey('database.id'), nullable=False)
    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_updated = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # Self-referential relationship for nested folders
    children = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]), lazy=True)
    worksheets = db.relationship('Worksheet', backref='folder', lazy=True)

class Worksheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(100), nullable=True, default= lambda: datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M %p'))
    worksheet_content = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_saved = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)  # Reference to the folder

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), nullable=False)
    date_executed = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class SavedQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), nullable=False)
    date_executed = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Secrets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_key = db.Column(db.String(60), nullable=False)
    secret_key = db.Column(db.String(60), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), nullable=False)
    date_executed = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

from sqlglot import Tokenizer





