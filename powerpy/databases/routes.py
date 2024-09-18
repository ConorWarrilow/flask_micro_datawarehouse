from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, current_app, jsonify, Response
from powerpy.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from powerpy.posts.forms import PostForm
from powerpy.databases.forms import UpdateDatabaseForm, CreateSchemaForm, CreateSchemaForDbForm, UploadDatasetForm, CreateDatabaseForm, UpdateSchemaForm
from powerpy.utils import Flash

from powerpy import db, bcrypt#, mail
from powerpy.models import User, Post, Database, Schema, DataFile, Dashboard
from flask_login import login_user, current_user, logout_user, login_required
from flask_dropzone import Dropzone
from powerpy.users.utils import save_picture, send_reset_email
import re
import secrets # So we can generate a random hex
import os # So we can get the file extension
from PIL import Image # So we can resize images before saving them
import logging
from werkzeug.utils import secure_filename
import shutil

from redis import Redis

redis = Redis(host='localhost', port=6379, db=0)

# similar to app = Flask(__name__)
databases = Blueprint('databases', __name__)


log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)  # Create the logs directory if it doesn't exist

logging.basicConfig(
    filename=os.path.join(log_dir, 'powerpy.log'),
    level=logging.INFO,  # Adjust the logging level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'
)



### MY FUNCTIONS ###

def check_if_current_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user != current_user:
        abort(403)
    return user










@databases.route("/<string:username>/databases/create", methods=['GET', 'POST'])
@login_required
def create_database(username):
    user = check_if_current_user(username)
    form = CreateDatabaseForm()

    if form.validate_on_submit():
        try:
            # Create and add the database to the session
            database = Database(
                database_name=form.database_name.data,
                database_description=form.database_description.data,
                owner=current_user
            )
            db.session.add(database)
            logging.info(f"Database object created: {database}")
            
            # Commit to get the database ID
            db.session.commit()
            logging.info(f"Database committed with ID: {database.id}")

            # Create the schema now that we have the database ID
            schema = Schema(
                name=form.default_schema.data,
                description=form.schema_description.data,
                database_id=database.id,
                owner=current_user
            )
            db.session.add(schema)
            logging.info(f"Schema object created: {schema}")

            # Commit the schema
            db.session.commit()
            logging.info("Schema committed successfully.")
            
            Flash.success('Database and default schema created successfully')
            return redirect(url_for('databases.view_databases', username=username))
        
        except Exception as e:
            logging.error(f"Error occurred during database creation: {e}")
            db.session.rollback()  # Roll back in case of any errors
            Flash.danger('An error occurred while creating the database. Please try again.')

    # Log form errors if validation fails
    if form.errors:
        logging.warning(f"Form validation errors: {form.errors}")

    return render_template('create_database.html', title='Create Database', form=form)



@databases.route("/<string:username>/schemas/create", methods=['GET', 'POST'])
@login_required
def create_schema(username):
    user = check_if_current_user(username)
    form = CreateSchemaForm()
    
    # Fetch available databases for the current user
    form.database.choices = [(db.id, db.database_name) for db in Database.query.filter_by(owner=current_user).all()]

    if form.validate_on_submit():
        try:
            # Create and add schema to the session
            schema = Schema(name=form.schema_name.data,
                            description=form.schema_description.data,
                            database_id=form.database.data,  # database_id from the form
                            owner_id=current_user.id)  # Assign the current user's ID as the owner

            db.session.add(schema)
            db.session.commit()  # Commit the schema to the database
            Flash.success('Schema Created')
            return redirect(url_for('main.home'))

        except Exception as e:
            db.session.rollback()  # Rollback in case of any error
            Flash.danger(f'An error occurred while creating the schema. {str(e)}')

    return render_template('create_schema.html', title='Create Schema', form=form)

























@databases.route("/<string:username>/databases/<int:database_id>/create-schema", methods=['GET', 'POST'])
@login_required
def create_schema_for_db(username, database_id):
    user = check_if_current_user(username)

    # Pass the database_id to the form during initialization
    form = CreateSchemaForDbForm(database_id=database_id)

    if form.validate_on_submit():
        # Create a new schema with the form data
        schema = Schema(name=form.schema_name.data,
                        description=form.schema_description.data,
                        database_id=database_id,  # Use the database_id from the URL
                        owner_id=current_user.id)  # Assign the current user's ID as the owner

        db.session.add(schema)
        db.session.commit()
        Flash.success('Schema Created')
        page = request.args.get('page', 1, type=int)
        total_databases = request.args.get('total_databases', 'error', type=int)
        schemas = (Schema.query
        .filter_by(owner=user, database_id=database_id)
        .order_by(Schema.date_created.desc())
        ).all()
        
        return redirect(url_for('databases.view_database', database_id=database_id, username=current_user.username, schemas=schemas, page=page, total_databases=total_databases)) ############# this needs changing or just get rid of some of the multiple pages functionality shit

    return render_template('create_schema_for_db.html', title='Create Schema', form=form)


## fuck this just get rid of the dumb page functionality you honestly don't even want it anyway


# old one before I updated the base template
#
#
#@databases.route("/<string:username>/databases", methods=['GET', 'POST'])
#@login_required
#def view_databases(username):
#    user = User.query.filter_by(username=username).first_or_404()
#
#    if user != current_user:
#        abort(403)  # HTTP response for a forbidden route
#
#    page = request.args.get('page', 1, type=int)
#    total_databases = request.args.get('total_databases', 'error', type=int)
#    logging.info(f"total_databases_one:{total_databases}")
#    databases = (Database.query
#        .filter_by(owner=user)
#        .order_by(Database.date_created.desc())
#        .paginate(page=page, per_page=10)
#    )
#    form = CreateDatabaseForm()
#
#    if form.validate_on_submit():
#        try:
#            # Create and add the database to the session
#            database = Database(
#                database_name=form.database_name.data,
#                database_description=form.database_description.data,
#                owner=current_user
#            )
#            db.session.add(database)
#            logging.info(f"Database object created: {database}")
#            
#            # Commit to get the database ID
#            db.session.commit()
#            logging.info(f"Database committed with ID: {database.id}")
#
#            # Create the schema now that we have the database ID
#            schema = Schema(
#                name=form.default_schema.data,
#                description=form.schema_description.data,
#                database_id=database.id,
#                owner=current_user
#            )
#            db.session.add(schema)
#            logging.info(f"Schema object created: {schema}")
#
#            # Commit the schema
#            db.session.commit()
#            logging.info("Schema committed successfully.")
#            
#            Flash.success('Database and default schema created successfully')
#            return redirect(url_for('databases.view_databases', username=username))
#        
#        except Exception as e:
#            logging.error(f"Error occurred during database creation: {e}")
#            db.session.rollback()  # Roll back in case of any errors
#            Flash.danger('An error occurred while creating the database. Please try again.')
#
#    # Log form errors if validation fails
#    if form.errors:
#        logging.warning(f"Form validation errors: {form.errors}")
#    
#    return render_template('databases.html', title='Databases',
#                           databases=databases, user=user, page=page, form=form)
#
#



@databases.route("/<string:username>/databases/<int:database_id>", methods=['GET', 'POST'])
@login_required
def view_database(username, database_id):
    user = check_if_current_user(username)


    page = request.args.get('page', 1, type=int)
    total_databases = request.args.get('total_databases', 'error', type=int)


    logging.info(f"user:{page}")
    logging.info(f"total_databases_two:{total_databases}")
    database = Database.query.get_or_404(database_id) # If it doesn't exist, return a 404
    schemas = (Schema.query
        .filter_by(owner=user, database_id=database.id)
        .order_by(Schema.date_created.desc())
        ).all()

    logging.info(f"user:{schemas}")


    return render_template('database.html', database=database, schemas=schemas, total_databases=total_databases, page=page)






@databases.route("/<username>/databases/<int:database_id>/delete", methods=['POST'])
@login_required
def delete_database(username, database_id):
    """Deleting a database will delete all schemas and data within the database"""

    # Get the database object
    database = Database.query.get_or_404(database_id)
    if database.owner != current_user:
        abort(403)

    # Path to delete
    database_path = f"uploads/{current_user.id}/{database.database_name}"

    # Attempt to delete the directory and its contents
    if os.path.exists(database_path):
        try:
            shutil.rmtree(database_path)  # Recursively remove the directory and its contents
            logging.info(f"Successfully deleted the directory: {database_path}")
        except Exception as e:
            logging.error(f"Error deleting directory {database_path}: {e}")
            flash('An error occurred while deleting the files. Please try again.', 'danger')
            return redirect(url_for('databases.view_databases', username=username))
    else:
        flash('Directory does not exist. No files were deleted.', 'warning')
        logging.warning(f"Directory does not exist: {database_path}")

    # Delete the database and related entries
    try:
        db.session.delete(database)
        schemas = Schema.query.filter_by(database_id=database_id).all()
        for schema in schemas:
            db.session.delete(schema)
        datafiles = DataFile.query.filter_by(database_id=database_id).all()
        for datafile in datafiles:
            db.session.delete(datafile)
        db.session.commit()
        logging.info(f"Successfully deleted database {database_id} and related entries")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting database {database_id} and related entries: {e}")
        flash('An error occurred while deleting the database. Please try again.', 'danger')
        return redirect(url_for('databases.view_databases', username=username))

    # Adjust pagination and redirect
    total_databases = request.form.get('total_databases', 1, type=int)
    page = request.form.get('page', 1, type=int)
    if total_databases % 10 == 1:
        page = max(page - 1, 1)  # Ensure page number is not less than 1

    logging.info(f"Total databases before deleting a database: {total_databases}")
    logging.info(f"Page number after deletion: {page}")
    flash('Your database has been deleted!', 'info')

    return redirect(url_for('databases.view_databases', 
                            username=username, 
                            page=page,
                            total_databases=total_databases))





@databases.route("/<username>/databases/<int:database_id>/<int:schema_id>/delete", methods=['POST'])
@login_required
def delete_schema(username, database_id, schema_id):

    # Get the database object
    database = Database.query.get_or_404(database_id)
    if database.owner != current_user:
        abort(403)

    schema = Schema.query.get_or_404(schema_id)




    # Define the path to the schema's directory
    schema_path = f"uploads/{current_user.id}/{database.database_name}/{schema.name}"

    # Attempt to delete the schema's directory and its contents
    if os.path.exists(schema_path):
        try:
            shutil.rmtree(schema_path)  # Recursively remove the directory and its contents
            logging.info(f"Successfully deleted the schema directory: {schema_path}")
        except Exception as e:
            logging.error(f"Error deleting schema directory {schema_path}: {e}")
            flash('An error occurred while deleting the schema files. Please try again.', 'danger')
            return redirect(url_for('databases.view_databases', username=username))
    else:
        flash('Schema directory does not exist. No files were deleted.', 'warning')
        logging.warning(f"Schema directory does not exist: {schema_path}")

    # Delete the schema and related data files
    try:
        schema = Schema.query.get_or_404(schema_id)
        db.session.delete(schema)
        datafiles = DataFile.query.filter_by(schema_id=schema_id).all()
        for datafile in datafiles:
            db.session.delete(datafile)
        db.session.commit()
        logging.info(f"Successfully deleted schema {schema_id} and related data files")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting schema {schema_id} and related data files: {e}")
        flash('An error occurred while deleting the schema. Please try again.', 'danger')
        return redirect(url_for('databases.view_databases', username=username))

    # Redirect after successful deletion
    total_databases = request.form.get('total_databases', 1, type=int)
    page = request.form.get('page', 1, type=int)
    if total_databases % 10 == 1 and total_databases != 11:
        page = max(page - 1, 1)  # Ensure page number is not less than 1

    logging.info(f"Total databases before deleting schema: {total_databases}")
    logging.info(f"Page number after deletion: {page}")
    flash('The schema has been deleted!', 'info')

    return redirect(url_for('databases.view_database', 
                            username=username, 
                            page=page, 
                            total_databases=total_databases, 
                            database_id=database_id,
                            title = 'Delete Schema',
                            legend = 'Delete Schema'))



















@databases.route("/<username>/databases/<int:database_id>/update", methods=['GET', 'POST'])
@login_required
def update_database(username, database_id):
    database = Database.query.get_or_404(database_id)
    
    # Ensure the current user is the owner of the database
    if database.owner != current_user:
        abort(403)

    # Pass the original database name to the form for comparison
    form = UpdateDatabaseForm(original_database_name=database.database_name)

    if form.validate_on_submit():
        # Check if there are no changes made to the database
        if form.database_name.data == database.database_name and form.database_description.data == database.database_description:
            Flash.info('No Changes made.')
            return redirect(url_for('databases.view_database', database_id=database_id, username=username))

        # Update the database with new values
        database.database_name = form.database_name.data
        database.database_description = form.database_description.data
        db.session.commit()

        Flash.success('Your database has been updated.')
        return redirect(url_for('databases.view_database', database_id=database_id, username=username))
    
    # Pre-fill the form with the current database values when the request method is GET
    elif request.method == 'GET':
        form.database_name.data = database.database_name
        form.database_description.data = database.database_description

    return render_template('update_database.html', title='Update Database',
                           form=form, legend='Update Database', username=username)








#@databases.route("/<username>/databases/<int:database_id>/<int:schema_id>/update", methods=['GET', 'POST'])
#@login_required
#def update_schema(username, database_id, schema_id):
#
#
#    schema = Schema.query.get_or_404(schema_id)
#    if schema.owner != current_user:
#            abort(403)  
#
#
#    # This line obtains the data for the specific post
#    form = UpdateSchemaForm()
#    if form.validate_on_submit():
#
#        if form.schema_name.data == schema.name and form.schema_description.data == schema.description:
#            Flash.info('No Changes made.')
#            return redirect(url_for('databases.view_database', database_id=database_id, username=username))
#
#
#        schema.name = form.schema_name.data
#        schema.description = form.schema_description.data
#        db.session.commit()
#        Flash.success('Your schema has been updated.')
#        return redirect(url_for('databases.view_database', database_id=database_id, username=username))
#    
#    elif request.method == 'GET':
#        form.schema_name.data = schema.name
#        form.schema_description.data = schema.description
#
#    return render_template('update_schema.html', title='Update Schema',
#                           form=form, legend='Update Schema', username=username)








@databases.route("/<username>/databases/<int:database_id>/<int:schema_id>/update", methods=['GET', 'POST'])
@login_required
def update_schema(username, database_id, schema_id):
    schema = Schema.query.get_or_404(schema_id)

    if schema.owner != current_user:
        abort(403)

    form = UpdateSchemaForm(original_schema_name=schema.name, database_id=database_id)

    if form.validate_on_submit():
        # If the name and description are unchanged, do not proceed with the update
        if form.schema_name.data == schema.name and form.schema_description.data == schema.description:
            Flash.info('No changes made.')
            return redirect(url_for('databases.view_database', database_id=database_id, username=username))

        # Proceed with updating the schema
        schema.name = form.schema_name.data
        schema.description = form.schema_description.data
        db.session.commit()

        Flash.success('Your schema has been updated.')
        return redirect(url_for('databases.view_database', database_id=database_id, username=username))

    elif request.method == 'GET':
        form.schema_name.data = schema.name
        form.schema_description.data = schema.description

    return render_template('update_schema.html', title='Update Schema',
                           form=form, legend='Update Schema', username=username)
















#@databases.route("/add-data", methods=['GET', 'POST'])
#def add_data():
#    form = UploadDatasetForm()
#
#    if form.validate_on_submit():
#        file = form.file.data
#        # Save the file or process it as needed
#        os.makedirs(f"uploads/{current_user.username}", exist_ok=True)
#        file.save(os.path.join('uploads', current_user.username, file.filename))
#        flash('File successfully uploaded!', 'success')
#        
#        return redirect(url_for('main.home'))
#    
#    return render_template('add_data.html', title='Create Database', form = form)


# multiple files
##users.route("/add-data", methods=['GET', 'POST'])
#def add_data():
#   form = UploadDatasetForm()
#
#   if form.validate_on_submit():
#       files = form.files.data  # This will be a list of FileStorage objects
#       
#       os.makedirs(f"uploads/{current_user.username}", exist_ok=True)
#
#       for file in files:
#           # Save each file
#           file.save(os.path.join('uploads', current_user.username, file.filename))
#       
#       flash('Files successfully uploaded!', 'success')
#       return redirect(url_for('main.home'))
#   
#   return render_template('add_data.html', title='Create Database', form=form)
#<form method="POST" enctype="multipart/form-data">
#    {{ form.hidden_tag() }}
#    <div class="form-group">
#        {{ form.files.label(class="form-label") }}
#        {{ form.files(class="form-control", multiple=True) }}
#    </div>
#    <div class="form-group">
#        {{ form.submit(class="btn btn-primary") }}
#    </div>
#</form>






















#@databases.route("/schemas/<int:database_id>", methods=['GET'])
#@login_required
#def get_schemas(database_id):
#    database = Database.query.get_or_404(database_id)
#    if database.owner != current_user:
#        abort(403)
#
#    schemas = Schema.query.filter_by(database_id=database_id).all()
#    return jsonify([(schema.id, schema.name) for schema in schemas])
#
#
#
#
#@databases.route("/upload", methods=['GET', 'POST'])
#@login_required
#def upload():
#    form = UploadDatasetForm()
#    form.database.choices = [(db.id, db.database_name) for db in Database.query.filter_by(owner=current_user).all()]
#
#    if form.validate_on_submit():
#        files = form.files.data
#        logging.info(f"files: {files}")
#        database_id = form.database.data
#        logging.info(f"files: {database_id}")
#        schema_id = form.schema.data
#        logging.info(f"files: {schema_id}")
#        schema_path = f"uploads/{current_user.id}/{database_id}/{schema_id}"
#        os.makedirs(schema_path, exist_ok=True)
#
#
#        for file in files: 
#            filename = secure_filename(file.filename)
#            file_path = os.path.join(schema_path, filename)
#            file.save(file_path)
#
#
#        Flash.success('Data Successfully Uploaded.')
#        return redirect(url_for('main.home'))
#
#    return render_template('upload.html', form=form)



        #file = form.file.data
        #database_id = form.database.data

        # Save the uploaded file
        #filename = secure_filename(file.filename)
        #file_path = os.path.join(current_app.root_path, 'uploads', filename)
        #file.save(file_path)

        # Perform operations with the uploaded file and the selected database





#@databases.route("/upload", methods=['GET', 'POST'])
#@login_required
#def upload():
#    form = UploadDatasetForm()
#    
#    # Set choices for the database field
#    form.database.choices = [(db.id, db.database_name) for db in Database.query.filter_by(owner=current_user).all()]
#    
#    # Set initial choices for the schema field with a default option
#    form.schema.choices = [('', 'Select Schema')]
#
#    if form.validate_on_submit():
#        try:
#            files = form.files.data
#            database_id = form.database.data
#            schema_id = form.schema.data
#            
#            logging.info(f"Processing upload for user {current_user.id}, database {database_id}, schema {schema_id}")
#            
#            schema_path = f"uploads/{current_user.id}/{database_id}/{schema_id}"
#            os.makedirs(schema_path, exist_ok=True)
#            
#            for file in files:
#                filename = secure_filename(file.filename)
#                file_path = os.path.join(schema_path, filename)
#                file.save(file_path)
#                logging.info(f"Saved file: {file_path}")
#            
#            flash('Data Successfully Uploaded.', 'success')
#            return redirect(url_for('main.home'))
#        except Exception as e:
#            logging.error(f"Error during file upload: {str(e)}")
#            flash('An error occurred during upload. Please try again.', 'danger')
#
#    return render_template('upload.html', form=form)







## original upload incase I need to go back to it
#@databases.route("/upload", methods=['GET', 'POST'])
#@login_required
#def upload():
#    form = UploadDatasetForm()
#    form.database.choices = [(db.id, db.database_name) for db in Database.query.filter_by(owner=current_user).all()]
#
#    if form.validate_on_submit():
#        files = form.files.data
#        logging.info(f"files: {files}")
#        database_id = form.database.data
#
#        database_path = f"uploads/{current_user.id}/{database_id}"
#        os.makedirs(database_path, exist_ok=True)
#
#
#        for file in files: 
#            filename = secure_filename(file.filename)
#            file_path = os.path.join(database_path, filename)
#            file.save(file_path)
#
#
#        Flash.success('Data Successfully Uploaded.')
#        return redirect(url_for('users.upload'))
#
#    return render_template('upload.html', form=form)




#@databases.route("/upload", methods=['GET', 'POST'])
#@login_required
#def upload():
#    form = UploadDatasetForm()
#    
#    # Set choices for the database field
#    form.database.choices = [(str(db.id), db.database_name) for db in Database.query.filter_by(owner=current_user).all()]
#    
#    if form.validate_on_submit():
#        try:
#            files = form.files.data
#            database_id = form.database.data
#            schema_id = form.schema.data
#            
#            logging.info(f"Processing upload for user {current_user.id}, database {database_id}, schema {schema_id}")
#            
#            schema_path = f"uploads/{current_user.id}/{database_id}/{schema_id}"
#            os.makedirs(schema_path, exist_ok=True)
#            
#            for file in files:
#                filename = secure_filename(file.filename)
#                file_path = os.path.join(schema_path, filename)
#                file.save(file_path)
#                logging.info(f"Saved file: {file_path}")
#            
#            flash('Data Successfully Uploaded.', 'success')
#            return redirect(url_for('main.home'))
#        except Exception as e:
#            logging.error(f"Error during file upload: {str(e)}")
#            flash('An error occurred during upload. Please try again.', 'danger')
#
#    return render_template('upload.html', form=form)































#original for id probably need it back

#@databases.route("/schemas/<int:database_id>", methods=['GET'])
#@login_required
#def get_schemas(database_id):
#    database = Database.query.get_or_404(database_id)
#    if database.owner != current_user:
#        abort(403)
#    
#    schemas = Schema.query.filter_by(database_id=database_id).all()
#    return jsonify([(str(schema.id), schema.name) for schema in schemas])

import duckdb


@databases.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadDatasetForm()
    
    # Set choices for the database field, keeping the default option
    db_choices = [('', 'Select Database')]
    db_choices.extend([(str(db.id), db.database_name) for db in Database.query.filter_by(owner=current_user).all()])
    form.database.choices = db_choices
    
    if form.validate_on_submit():
        try:
            files = form.files.data
            database_id = form.database.data
            schema_id = form.schema.data

            # Fetch the database and schema names
            database = Database.query.get(database_id)
            schema = Schema.query.get(schema_id)

            if not database or not schema:
                flash('Invalid database or schema selected.', 'danger')
                return redirect(url_for('databases.upload'))

            database_name = secure_filename(database.database_name)
            schema_name = secure_filename(schema.name)

            logging.info(f"Processing upload for user {current_user.id}, database {database_name}, schema {schema_name}")

            schema_path = f"uploads/{current_user.id}/{database_name}/{schema_name}"
            os.makedirs(schema_path, exist_ok=True)

            for file in files:
                filename = secure_filename(file.filename)
                new_filename = filename.replace('-', '_')
                datafile = DataFile(filename=new_filename.rsplit('.', 1)[0],
                                    database_id=database_id,
                                    schema_id=schema_id,
                                    owner_id=current_user.id)
                db.session.add(datafile)
                db.session.commit()

                # Load file contents using DuckDB
                file_path = os.path.join(schema_path, filename)

                # Assuming it's a CSV file. You can adjust based on the file type.
                with open(file_path, 'wb') as f:
                    f.write(file.read())  # Save file temporarily

                # Use DuckDB to read the file and convert to Parquet
                parquet_file_path = os.path.join(schema_path, f"{new_filename.rsplit('.', 1)[0]}.parquet")

                # DuckDB query to read and save as Parquet

                duckdb.query(f"""
                    COPY (SELECT * FROM read_csv_auto('{file_path}'))
                    TO '{parquet_file_path}' (FORMAT PARQUET)
                """)

                # Optionally delete the temporary CSV file after conversion
                os.remove(file_path)
            
            flash('Data Successfully Uploaded.', 'success')
            return redirect(url_for('main.home'))
        except Exception as e:
            logging.error(f"Error during file upload: {str(e)}")
            flash('An error occurred during upload. Please try again.', 'danger')
    
    return render_template('upload.html', form=form)















@databases.route("/redis", methods=['GET', 'POST'])
def hello():
    redis.incr('hits')
    return f"This page has been viewed {redis.get('hits').decode('utf-8')} time(s)"



















#from flask import Flask, request, jsonify
#from redis import Redis
import json
from functools import wraps
import time
#
#app = Flask(__name__)
#redis = Redis(host='localhost', port=6379, db=0)
#
## 1. Caching
#def cache(expire_time=300):
#    def decorator(f):
#        @wraps(f)
#        def decorated_function(*args, **kwargs):
#            cache_key = f"cache:{request.path}:{request.query_string}"
#            result = redis.get(cache_key)
#            if result:
#                return json.loads(result)
#            result = f(*args, **kwargs)
#            redis.setex(cache_key, expire_time, json.dumps(result))
#            return result
#        return decorated_function
#    return decorator
#
#@app.route('/api/expensive-operation')
#@cache(expire_time=60)
#def expensive_operation():
#    time.sleep(2)  # Simulate expensive operation
#    return {"result": "This is an expensive operation"}
#
## 2. Session Storage
#from flask_session import Session
#app.config['SESSION_TYPE'] = 'redis'
#app.config['SESSION_REDIS'] = redis
#Session(app)
#
#@app.route('/api/session-example')
#def session_example():
#    if 'visits' in session:
#        session['visits'] = session.get('visits') + 1
#    else:
#        session['visits'] = 1
#    return f"You have visited this page {session['visits']} times."
#
## 3. Rate Limiting
#def rate_limit(limit=10, per=60):
#    def decorator(f):
#        @wraps(f)
#        def decorated_function(*args, **kwargs):
#            key = f"rate_limit:{request.remote_addr}:{request.path}"
#            current = redis.get(key)
#            if current is not None and int(current) > limit:
#                return jsonify({"error": "Rate limit exceeded"}), 429
#            pipe = redis.pipeline()
#            pipe.incr(key)
#            pipe.expire(key, per)
#            pipe.execute()
#            return f(*args, **kwargs)
#        return decorated_function
#    return decorator
#
#@app.route('/api/rate-limited')
#@rate_limit(limit=5, per=60)
#def rate_limited():
#    return "This is a rate-limited endpoint"
#
## 4. Job Queue
#from rq import Queue
#from rq.job import Job
#
#q = Queue(connection=redis)
#
#def background_task(x, y):
#    time.sleep(5)  # Simulate long running task
#    return x + y
#
#@app.route('/api/enqueue-job')
#def enqueue_job():
#    job = q.enqueue(background_task, 3, 4)
#    return jsonify({"job_id": job.id})
#
#@app.route('/api/job-result/<job_id>')
#def get_job_result(job_id):
#    job = Job.fetch(job_id, connection=redis)
#    if job.is_finished:
#        return jsonify({"result": job.result})
#    else:
#        return jsonify({"status": "pending"})
#
## 5. Pub/Sub for Real-time Updates
#import threading
#
#def message_handler():
#    pubsub = redis.pubsub()
#    pubsub.subscribe('updates')
#    for message in pubsub.listen():
#        if message['type'] == 'message':
#            print(f"Received: {message['data']}")
#
#@app.route('/api/publish-update')
#def publish_update():
#    redis.publish('updates', 'This is a real-time update')
#    return "Update published"
#
## Start the message handler in a separate thread
#threading.Thread(target=message_handler, daemon=True).start()
#
#if __name__ == '__main__':
#    app.run(debug=True)






















def cache(expire_time=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"cache:{request.path}:{request.query_string}"
            result = redis.get(cache_key)
            if result:
                return json.loads(result)
            result = f(*args, **kwargs)
            redis.setex(cache_key, expire_time, json.dumps(result))
            return result
        return decorated_function
    return decorator

def get_weather_data(city):
    # Simulate an API call with a delay
    time.sleep(2)
    # In a real scenario, you would make an actual API call here
    return {
        "city": city,
        "temperature": 22,
        "condition": "Sunny"
    }

@databases.route('/weather/<city>')
@cache(expire_time=60)  # Cache for 1 minute
def weather(city):
    start_time = time.time()
    weather_data = get_weather_data(city)
    end_time = time.time()
    
    response_time = round(end_time - start_time, 2)
    
    return render_template('weather.html', 
                           weather=weather_data, 
                           response_time=response_time)







from powerpy.utils import GigaDuck




#original 

#@databases.route("/databases", methods=['GET'])
#@login_required
#def get_databases():
#    databases = Database.query.filter_by(owner=current_user).all()
#    return jsonify([(str(db.id), db.database_name) for db in databases])








#@databases.route("/<string:username>/editor", methods=['GET'])
#@login_required
#def editor_query(username):
#    if username != current_user.username:
#        abort(403)
#    default_db = request.args.get('selected_database', type=str)
#    default_schema = request.args.get('selected_schema', type=str)
#    query = request.args.get('query', type=str)
#    gigaduck = GigaDuck(database=':memory:', user_id=current_user.id, default_db=default_db, default_schema=default_schema)
#    QUERY = f"""{query}"""
#    result = gigaduck.query(QUERY).fetch_df_chunk()





# original

#@databases.route("/editor", methods=['GET'])
#@login_required
#def editor_query():
#    default_db = request.args.get('selected_database', type=str)
#    default_schema = request.args.get('selected_schema', type=str)
#    query = request.args.get('query', type=str)
#    
#    current_app.logger.info(f"Received query: {query}")
#    current_app.logger.info(f"Selected database: {default_db}")
#    current_app.logger.info(f"Selected schema: {default_schema}")
#
#    database_name = Database.query.get_or_404(default_db)
#    schema_name = Database.query.get_or_404(default_schema)
#
#    current_app.logger.info(f"Received query: {query}")
#    current_app.logger.info(f"Selected databaseafterrrrrrrrrr: {database_name}")
#    current_app.logger.info(f"Selected schema afterrrrrrrrrrrrr: {schema_name}")
#
#    try:
#        gigaduck = GigaDuck(database=':memory:', user_id=current_user.id, default_db=database_name.database_name, default_schema=schema_name.name)
#        result = gigaduck.query(query).fetch_df_chunk()
#        response_data = {
#            'columns': result.columns.tolist(),
#            'data': result.values.tolist()
#        }
#        current_app.logger.info(f"Query result: {response_data}")
#        return jsonify(response_data)
#    except Exception as e:
#        current_app.logger.error(f"Error executing query: {str(e)}")
#        return jsonify({'error': str(e)}), 400










from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import simplejson as sj



#limiter = Limiter(
#    get_remote_address,
#    app=current_app,
#    storage_uri='redis://localhost:6379/0'
#)



@databases.route("/editor", methods=['GET'])
#@limiter.limit("5 per minute")
@login_required
def editor_query():
    start_time = datetime.now()
    selected_database_name = request.args.get('selected_database', type=str)
    selected_schema_name = request.args.get('selected_schema', type=str)
    query = request.args.get('query', type=str)
    
    current_app.logger.info(f"Received query: {query}")
    current_app.logger.info(f"Selected database: {selected_database_name}")
    current_app.logger.info(f"Selected schema: {selected_schema_name}")
    
    try:
        # Find the database by name
        database = Database.query.filter_by(owner=current_user, database_name=selected_database_name).first()
        if not database:
            return jsonify({'error': 'Database not found'}), 404

        # Find the schema by name
        schema = Schema.query.filter_by(database_id=database.id, name=selected_schema_name).first()
        if not schema:
            return jsonify({'error': 'Schema not found'}), 404

        gigaduck = GigaDuck(database=':memory:', user_id=current_user.id, default_db=database.database_name, default_schema=schema.name)
        result = gigaduck.query(query).fetchdf()

        for column in result.select_dtypes(include=['datetime64']):
            result[column] = result[column].astype(str)  # Convert to ISO 8601 string
        response_data = {
            'columns': result.columns.tolist(),
            'data': result.values.tolist()
        }
        #current_app.logger.info(f"Query result: {response_data}")

        return Response(sj.dumps(response_data, ignore_nan=True), mimetype='application/json')
    except Exception as e:
        error_message = str(e)

        # Check if the error message contains the specific pattern
        if 'match the pattern' in error_message:
            current_app.logger.error(f"Error executing query (real error): {error_message}")

            # Extract table name from the error message using regex
            # This regex captures the word just before '.parquet' after the last '/'
            match = re.search(r'/([^/]+)\.parquet"', error_message)
            if match:
                table = match.group(1)  # Extracted table name
            else:
                table = "unknown table"  # Default if table name couldn't be extracted

            return jsonify({'error': f"Unable to find '{table}' table in the specified location."}), 400
        
        elif str("'NoneType' object has no attribute") in error_message:
            return jsonify({'error': "Empty Query"}), 400
        else:
            current_app.logger.error(f"Error executing query: {error_message}")
            return jsonify({'error': error_message}), 400
    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() + 5.0  # Compute duration in seconds
    
        # Ensure current_user is loaded from the database
        user = User.query.get(current_user.id)
        if user:
            user.compute_usage += duration
            db.session.add(user)
            db.session.commit()





@databases.route("/databases", methods=['GET'])
@login_required
def get_databases():
    databases = Database.query.filter_by(owner=current_user).all()
    return jsonify([(str(db.id), db.database_name) for db in databases])


#@databases.route("/schemas/<int:database_id>", methods=['GET'])
#@login_required
#def get_schemas(database_id):
#    database = Database.query.get_or_404(database_id)
#    if database.owner != current_user:
#        abort(403)
#    
#    schemas = Schema.query.filter_by(database_id=database_id).all()
#    return jsonify([(str(schema.id), schema.name) for schema in schemas])
#
#
#@databases.route("/schemas/<int:schema_id>/datafiles", methods=['GET'])
#@login_required
#def get_datafiles(schema_id):
#    schema = Schema.query.get_or_404(schema_id)
#    if schema.owner != current_user:
#        abort(403)
#    
#    datafiles = DataFile.query.filter_by(schema_id=schema_id).all()
#    return jsonify([(str(datafile.id), datafile.filename) for datafile in datafiles])














@databases.route("/<string:username>/databases/<int:database_id>/schemas", methods=['GET'])
@login_required
def get_schemas(username, database_id):
    if username != current_user.username:
        abort(403)
    
    database = Database.query.get_or_404(database_id)
    if database.owner != current_user:
        abort(403)
    
    schemas = Schema.query.filter_by(database_id=database_id).all()
    return jsonify([(str(schema.id), schema.name) for schema in schemas])





@databases.route("/<string:username>/schemas/<int:schema_id>/datafiles", methods=['GET'])
@login_required
def get_datafiles(username, schema_id):
    if username != current_user.username:
        abort(403)
    
    schema = Schema.query.get_or_404(schema_id)
    if schema.owner != current_user:
        abort(403)
    
    datafiles = DataFile.query.filter_by(schema_id=schema_id).all()
    return jsonify([(str(datafile.id), datafile.filename) for datafile in datafiles])







from powerpy.models import Worksheet
from datetime import datetime, timezone


# Route to save the worksheet content periodically
@databases.route('/save-worksheet/<worksheet_code>', methods=['POST'])
@login_required
def save_worksheet():
    data = request.get_json()
    username = data.get('username')
    content = data.get('content')
    code = data.get('code')
    if not username or not content:
        return jsonify({'error': 'Username and content are required'}), 400

    # Check if there's already a saved worksheet for the user
    worksheet = Worksheet.query.filter_by(user_id=username).first()

    if worksheet:
        # Update existing worksheet content
        worksheet.worksheet_content = content
        worksheet.last_saved = datetime.now(timezone.utc)

        db.session.add(worksheet)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': 'Worksheet saved successfully'})











    #database = Database.query.get_or_404(database_id)
    #if database.owner != current_user:
    #    abort(403)
    #
    #schemas = Schema.query.filter_by(database_id=database_id).all()
    #return jsonify([(str(schema.id), schema.name) for schema in schemas])







@databases.route("/<string:username>/databases", methods=['GET', 'POST'])
@login_required
def view_databases(username):
    user = User.query.filter_by(username=username).first_or_404()

    if user != current_user:
        abort(403)  # HTTP response for a forbidden route


    total_databases = request.args.get('total_databases', 'error', type=int)
    logging.info(f"total_databases_one:{total_databases}")
    databases = (Database.query
        .filter_by(owner=user)
        .order_by(Database.date_created.desc())).all()
    
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    form = CreateDatabaseForm()

    if form.validate_on_submit():
        try:
            # Create and add the database to the session
            database = Database(
                database_name=form.database_name.data,
                database_description=form.database_description.data,
                owner=current_user
            )
            db.session.add(database)
            logging.info(f"Database object created: {database}")
            
            # Commit to get the database ID
            db.session.commit()
            logging.info(f"Database committed with ID: {database.id}")

            # Create the schema now that we have the database ID
            schema = Schema(
                name=form.default_schema.data,
                description=form.schema_description.data,
                database_id=database.id,
                owner=current_user
            )
            db.session.add(schema)
            logging.info(f"Schema object created: {schema}")

            # Commit the schema
            db.session.commit()
            logging.info("Schema committed successfully.")
            
            Flash.success('Database and default schema created successfully')
            return redirect(url_for('databases.view_databases', username=username))
        
        except Exception as e:
            if form.errors:
                logging.warning(f"Form validation errors: {form.errors}")
            logging.error(f"Error occurred during database creation: {e}")
            db.session.rollback()  # Roll back in case of any errors
            Flash.danger('An error occurred while creating the database. Please try again.')

    # Log form errors if validation fails
    if form.errors:
        Flash.danger('There are errors in your form')
        
    
    return render_template('databases.html', title='Databases',
                           databases=databases, user=user, form=form, image_file=image_file)



