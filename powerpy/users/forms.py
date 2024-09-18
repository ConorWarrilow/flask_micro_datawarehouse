from flask_wtf import FlaskForm
#For Uploading Images in forms
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from powerpy.models import User, Database
import os
import re




class CustomValidator:
    
    @staticmethod
    def letters_and_underscores(form, field):
        """Custom validator to check if a field contains only letters and underscores."""
        if not re.match(r'^[a-zA-Z_]+$', field.data):
            raise ValidationError('This field can only contain letters and underscores.')

    @staticmethod
    def validate_database_name(form, database_name):
        """Checks if a database already exists for this user."""
        database = Database.query.filter_by(database_name=database_name.data).filter_by(owner_id=current_user.id).first()
        if database:
            raise ValidationError('A database with this name already exists within your account. Please choose another name.')

    @staticmethod
    def validate_file_extension(form, field):
        """Custom validator to check if files have allowed extensions."""
        allowed_extensions = {'csv', 'parquet'}
        for file in field.data:
            if not file or not file.filename:
                continue
            # Check the file extension
            file_ext = os.path.splitext(file.filename)[1][1:].lower()
            if file_ext not in allowed_extensions:
                raise ValidationError('Only .csv and .parquet files are allowed.')






class RegistrationForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """Checks if a username already exists within the database"""

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is taken. Please choose another.')

    def validate_email(self, email):
        """Checks if a username already exists within the database"""

        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('This email is already in use.')



class LoginForm(FlaskForm):
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



class UpdateAccountForm(FlaskForm):
    """We only want to query the database if a user changes their username, else it'll alert that someone already has that username (because that's their current
    username in the database). We import user from flask_login to check if any changes were made"""
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update ')

    def validate_username(self, username):
        """Checks if a username already exists within the database"""
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is taken. Please choose another.')

    def validate_email(self, email):
        """Checks if a username already exists within the database"""
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('This email is already in use.')
            


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account found with that email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')




def validate_characters(form, field):
    """Custom validator to check if a field contains only letters and underscores."""
    if not re.match(r'^[a-zA-Z_]+$', field.data):
        raise ValidationError('This field can only contain letters and underscores.')

def validate_database_name(self, database_name):
    """Checks if a database already exists for this user"""

    database = Database.query.filter_by(database_name=database_name.data).filter_by(owner_id = current_user.id).first()
    if database:
        raise ValidationError('A database with this name already exists within your account. Please choose another name.')





#class UploadDatasetForm(FlaskForm):
#    file = FileField('Upload CSV', validators=[
#        InputRequired(),
#        FileAllowed(['csv'], 'CSV files only!')])
#    submit = SubmitField('Upload Dataset')



def validate_file_extension(form, field):
    allowed_extensions = {'csv', 'parquet'}
    for file in field.data:
        if not file:
            continue
        if not file.filename:
            continue
        # Check the file extension
        file_ext = os.path.splitext(file.filename)[1][1:].lower()
        if file_ext not in allowed_extensions:
            raise ValidationError('Only .csv and .parquet files are allowed.')




class UploadDatasetForm(FlaskForm):
    files = MultipleFileField('Upload CSV/Image', validators=[DataRequired(), validate_file_extension])
    database = SelectField('Select Database', validators=[DataRequired()])
    submit = SubmitField('Submit')








# multiple files
#    class UploadDatasetForm(FlaskForm):
#    files = MultipleFileField('Upload CSVs', validators=[
#        InputRequired(),
#        FileAllowed(['csv'], 'CSV files only!')
#    ])
#    submit = SubmitField('Upload Datasets')








