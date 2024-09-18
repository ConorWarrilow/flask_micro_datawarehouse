from flask_wtf import FlaskForm
#For Uploading Images in forms
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from powerpy.models import User, Database, Schema
import os
import re
from powerpy.utils import CustomValidator





class CreateDatabaseForm(FlaskForm):
    database_name = StringField('Database Name',
                            validators=[DataRequired(), Length(min=2, max=30)])
    database_description = StringField('Database Description (optional)',
                            validators=[Length(max=100)])
    default_schema = StringField('Default Schema',
                            validators=[DataRequired(), Length(min=2, max=30)])
    
    schema_description = StringField('Schema Description (optional)',
                            validators=[Length(max=100)])

    submit = SubmitField('Create')

    def validate_database_name(self, database_name):
        """Checks if a database already exists for this user"""

        CustomValidator.regex(database_name, ['letters', 'numbers', 'underscores'])
        
        database = Database.query.filter_by(database_name=database_name.data).filter_by(owner_id = current_user.id).first()
        if database:
            raise ValidationError('A database with this name already exists within your account. Please choose another name.')
        

    def validate_default_schema(self, default_schema):
    
        CustomValidator.regex(default_schema, ['letters', 'numbers', 'underscores'])





class CreateSchemaForm(FlaskForm):
    schema_name = StringField('Schema Name',
                            validators=[DataRequired(), Length(min=2, max=30)])
    schema_description = StringField('Schema Description',
                            validators=[Length(max=100)])
    database = SelectField('Select Database', validators=[DataRequired()])

    submit = SubmitField('Create Schema')

    def validate_schema_name(self, schema_name):
        """Custom validator to check if a schema with the same name already exists in the selected database."""
        
        CustomValidator.regex(schema_name, ['letters', 'numbers', 'underscores'])

        # Ensure that the selected database exists
        database_id = self.database.data  # Correctly accessing the database ID from the select field
        if database_id is None:
            raise ValidationError('Please select a valid database.')

        # Query the database to check if a schema with the same name exists in the selected database
        existing_schema = Schema.query.filter_by(database_id=database_id, name=schema_name.data).first()

        if existing_schema:
            raise ValidationError(f'A schema with the name "{schema_name.data}" already exists in the selected database.')




class CreateSchemaForDbForm(FlaskForm):
    schema_name = StringField('Schema Name',
                              validators=[DataRequired(), Length(min=2, max=30)])
    schema_description = StringField('Schema Description',
                                     validators=[Length(max=100)])
    submit = SubmitField('Create Schema')

    def __init__(self, database_id, *args, **kwargs):
        """Initialize the form and pass in the database_id."""
        super(CreateSchemaForDbForm, self).__init__(*args, **kwargs)
        self.database_id = database_id

    def validate_schema_name(self, schema_name):
        """Custom validator to check if a schema with the same name already exists in the selected database."""

        CustomValidator.regex(schema_name, ['letters', 'numbers', 'underscores'])

        # Query the database to check if a schema with the same name exists in the selected database
        existing_schema = Schema.query.filter_by(database_id=self.database_id, name=schema_name.data).first()

        # If a schema with the same name exists, raise an error
        if existing_schema:
            raise ValidationError(f'A schema with the name "{schema_name.data}" already exists in the selected database.')





class UpdateDatabaseForm(FlaskForm):
    """Form for updating a database, with validation to ensure the new name isn't a duplicate."""

    database_name = StringField('Database Name',
                                validators=[DataRequired(), Length(min=2, max=30)])
    database_description = StringField('Database Description',
                                       validators=[Length(max=100)])
    submit = SubmitField('Update Database')

    def __init__(self, original_database_name, *args, **kwargs):
        """Initialize the form and pass in the original database name for comparison."""
        super(UpdateDatabaseForm, self).__init__(*args, **kwargs)
        self.original_database_name = original_database_name

    def validate_database_name(self, database_name):
        """Custom validator to check if the database name already exists."""

        CustomValidator.regex(database_name, ['letters', 'numbers', 'underscores'])

        # Check if the name has actually changed; if not, skip the duplicate check
        if database_name.data != self.original_database_name:
            # Query the database to check if a database with the same name already exists
            existing_database = Database.query.filter_by(database_name=database_name.data).first()
            if existing_database:
                raise ValidationError(f'A database with the name "{database_name.data}" already exists.')








#class UpdateSchemaForm(FlaskForm):
#
#    schema_name = StringField('Schema Name',
#                            validators=[DataRequired(), Length(min=2, max=30)])
#    schema_description = StringField('Schema Description',
#                            validators=[Length(max=100)])
#    submit = SubmitField('Update Schema')
#
#    def validate_schema_name_update(self, schema_name):
#        """Custom validator to check if a schema with the same name already exists in the selected database."""
#        
#        # Regular expression check for letters and underscores
#        if not re.match(r'^[a-zA-Z_]+$', schema_name.data):
#            raise ValidationError('This field can only contain letters and underscores.')
#
#        # Ensure that the selected database exists
#        database_id = self.database.data  # Correctly accessing the database ID from the select field
#        if database_id is None:
#            raise ValidationError('Please select a valid database.')
#
#        # Query the database to check if a schema with the same name exists in the selected database
#        existing_schema = Schema.query.filter_by(database_id=database_id, name=schema_name.data).first()
#
#        if existing_schema:
#            raise ValidationError(f'A schema with the name "{schema_name.data}" already exists in the selected database.')




class UpdateSchemaForm(FlaskForm):
    schema_name = StringField('Schema Name',
                            validators=[DataRequired(), Length(min=2, max=30)])
    schema_description = StringField('Schema Description',
                            validators=[Length(max=100)])
    submit = SubmitField('Update Schema')

    def __init__(self, original_schema_name, database_id, *args, **kwargs):
        """Initialize the form and pass in the original schema name and database_id for comparison."""
        super(UpdateSchemaForm, self).__init__(*args, **kwargs)
        self.original_schema_name = original_schema_name
        self.database_id = database_id

    def validate_schema_name(self, schema_name):
        """Custom validator to check if a schema with the same name already exists in the selected database."""
        
        # Regular expression check for letters and underscores
        CustomValidator.regex(schema_name, ['letters', 'numbers', 'underscores'])

        # Skip the validation if the schema name hasn't changed
        if schema_name.data == self.original_schema_name:
            return

        # Query the database to check if a schema with the same name exists in the selected database
        existing_schema = Schema.query.filter_by(database_id=self.database_id, name=schema_name.data).first()

        # If a schema with the same name exists and it's not the current one, raise an error
        if existing_schema:
            raise ValidationError(f'A schema with the name "{schema_name.data}" already exists in the selected database.')






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
    database = SelectField('Select Database', choices=[('', 'Select Database')], validators=[DataRequired()])
    schema = SelectField('Select Schema', choices=[('', 'Select Schema')], validators=[DataRequired()], validate_choice=False)
    submit = SubmitField('Submit')




class DatabaseConfig(FlaskForm):
    database = SelectField('Select Database', choices=[('', 'Select Database')], validators=[DataRequired()])
    schema = SelectField('Select Schema', choices=[('', 'Select Schema')], validators=[DataRequired()], validate_choice=False)












#class UploadDatasetForm(FlaskForm):
#    file = FileField('Upload CSV', validators=[
#        InputRequired(),
#        FileAllowed(['csv'], 'CSV files only!')])
#    submit = SubmitField('Upload Dataset')








#class UploadDatasetForm(FlaskForm):
#    files = MultipleFileField('Upload CSV/Image', validators=[DataRequired(), validate_file_extension])
#    database = SelectField('Select Database', validators=[DataRequired()])
#    submit = SubmitField('Submit')



#def validate_file_extension(form, field):
#    allowed_extensions = {'csv', 'parquet'}
#    for file in field.data:
#        if not file:
#            continue
#        if not file.filename:
#            continue
#        # Check the file extension
#        file_ext = os.path.splitext(file.filename)[1][1:].lower()
#        if file_ext not in allowed_extensions:
#            raise ValidationError('Only .csv and .parquet files are allowed.')

#class UploadDatasetForm(FlaskForm):
#    files = MultipleFileField('Upload CSV/Image', validators=[DataRequired(), validate_file_extension])
#    database = SelectField('Select Database', validators=[DataRequired()])
#    schema = SelectField('Select Schema', validators=[DataRequired()])
#    submit = SubmitField('Submit')




# multiple files
#    class UploadDatasetForm(FlaskForm):
#    files = MultipleFileField('Upload CSVs', validators=[
#        InputRequired(),
#        FileAllowed(['csv'], 'CSV files only!')
#    ])
#    submit = SubmitField('Upload Datasets')



#def validate_file_extension(form, field):
#    allowed_extensions = {'csv', 'parquet'}
#    for file in field.data:
#        if not file:
#            continue
#        if not file.filename:
#            continue
#        # Check the file extension
#        file_ext = os.path.splitext(file.filename)[1][1:].lower()
#        if file_ext not in allowed_extensions:
#            raise ValidationError('Only .csv and .parquet files are allowed.')
#
#class UploadDatasetForm(FlaskForm):
#    files = MultipleFileField('Upload CSV/Image', validators=[DataRequired(), validate_file_extension])
#    database = SelectField('Select Database', validators=[DataRequired()])
#    schema = SelectField('Select Schema', validators=[DataRequired()], validate_choice=False)
#    submit = SubmitField('Submit')




class CreateFolderForm(FlaskForm):
    folder_name = StringField('Folder Name',
                              validators=[DataRequired(), Length(min=2, max=30)])
    folder_description = StringField('Folder Description',
                                     validators=[Length(max=100)])
    submit = SubmitField('Create Folder')

    def validate_folder_name(self, schema_name):
        CustomValidator.regex(schema_name, ['letters', 'numbers', 'underscores'])
