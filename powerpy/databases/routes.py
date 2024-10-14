from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, current_app, jsonify, Response
from powerpy.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from powerpy.posts.forms import PostForm
from powerpy.databases.forms import UpdateDatabaseForm, CreateSchemaForm, CreateSchemaForDbForm, UploadDatasetForm, CreateDatabaseForm, UpdateSchemaForm
from powerpy.utils import Flash, generate_uuid

from powerpy import db, bcrypt
from powerpy.models import User, Post, Database, Schema, DataFile, Dashboard, SchemaTable, Query, SavedQuery, Upload
from flask_login import login_user, current_user, logout_user, login_required
from flask_dropzone import Dropzone
from powerpy.users.utils import save_picture, send_reset_email
import re
import secrets
import os 
from PIL import Image 
import logging
from werkzeug.utils import secure_filename
import shutil
import json
from functools import wraps
import time
from powerpy.models import Worksheet
from datetime import datetime, timezone
from powerpy.databases.utils import get_query_object, SqlQueryBase
from redis import Redis
import duckdb
import simplejson as sj
import logging
import pandas as pd

# havent added caching yet, windows wasn't playing nice and I'll be moving to linux for the real project so I'll add it then.
#redis = Redis(host='localhost', port=6379, db=0)
databases = Blueprint('databases', __name__)




log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'flask_logs.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
route_logger = logging.getLogger('route_logger')



@databases.route("/create_database", methods=['POST'])
@login_required
def create_database():
    route_logger.info("Accessed databases.create_database")
    form_data = request.form
    errors = {}


    database_name = form_data['database_name']
    default_schema = form_data['default_schema']

    # Server-side validation
    #if not form_data.get('database_name'):
    #    errors['database_name'] = 'Database name is required.'

    # Database Validation
    if len(database_name) < 1 or len(database_name) > 30:
        errors['database_name'] = 'Database name must be between 1 and 30 characters.'
    elif not re.match(r'^[a-zA-Z0-9_]+$', database_name):
        errors['database_name'] = 'Only letters, numbers, and underscores are allowed.'

    if len(default_schema) < 1 or len(default_schema) > 30:
        errors['default_schema'] = 'Schema name must be between 1 and 30 characters.'
    elif not re.match(r'^[a-zA-Z0-9_]+$', default_schema):
        errors['default_schema'] = 'Only letters, numbers, and underscores are allowed.'
    try:

        database = Database.query.filter_by(database_name=database_name).filter_by(owner_id = current_user.id).first()
        if database: errors['database_name'] = f"Object '{database_name}' already exists for this account." 
            
    except Exception as e:
        current_app.logger.info("there was an exception bro")

    # Similar validation for other fields...

    if errors:
        return jsonify({"success": True, "errors": errors}), 400

    try:
        # Create and add the database to the session
        database = Database(
            database_name=database_name,
            database_description=form_data.get('database_description', ''),
            owner=current_user
        )
        db.session.add(database)
        db.session.commit()

        # Create the schema
        schema = Schema(
            name=default_schema,
            description=form_data.get('schema_description', ''),
            database_id=database.id,
            owner=current_user
        )
        db.session.add(schema)
        db.session.commit()
        schema_path = f"uploads/{current_user.id}/{database_name}/{default_schema}"
        os.makedirs(schema_path, exist_ok=True)


        return jsonify({
            "success": True,
            "message": "Database and schema created successfully",
            "flash_message": "Database created successfully.",
            "flash_category": "success"
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error occurred during database creation: {e}")
        return jsonify({
            "success": False,
            "message": str(e),
            "flash_message": "Error creating database.",
            "flash_category": "error"
        }), 500





@databases.route("/<string:username>/schemas/create", methods=['GET', 'POST'])
@login_required
def create_schema(username):
    if username != current_user.username: abort(403)
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


            selected_database = Database.query.get_or_404(form.database.data)
            schema_path = f"uploads/{current_user.id}/{selected_database.database_name}/{form.schema_name.data}"
            os.makedirs(schema_path, exist_ok=True)
            Flash.success('Schema Created')
            return redirect(url_for('main.home'))

        except Exception as e:
            db.session.rollback()  # Rollback in case of any error
            Flash.danger(f'An error occurred while creating the schema. {str(e)}')

    return render_template('create_schema.html', title='Create Schema', form=form)





@databases.route("/<string:username>/databases/<int:database_id>/create-schema", methods=['GET', 'POST'])
@login_required
def create_schema_for_db(username, database_id):
    if username != current_user.username: abort(403)

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

        database = Database.query.get_or_404(database_id)


        schema_path = f"uploads/{current_user.id}/{database.database_name}/{form.schema_name.data}"
        os.makedirs(schema_path, exist_ok=True)

        Flash.success('Schema Created')
        page = request.args.get('page', 1, type=int)
        total_databases = request.args.get('total_databases', 'error', type=int)
        schemas = (Schema.query
        .filter_by(owner=current_user, database_id=database_id)
        .order_by(Schema.date_created.desc())
        ).all()
        
        return redirect(url_for('databases.view_database', database_id=database_id, username=current_user.username, schemas=schemas, page=page, total_databases=total_databases)) ############# this needs changing or just get rid of some of the multiple pages functionality shit

    return render_template('create_schema_for_db.html', title='Create Schema', form=form)




@databases.route("/<string:username>/databases/<int:database_id>", methods=['GET', 'POST'])
@login_required
def view_database(username, database_id):
    if username != current_user.username: abort(403)


    page = request.args.get('page', 1, type=int)
    total_databases = request.args.get('total_databases', 'error', type=int)


    logging.info(f"user:{page}")
    logging.info(f"total_databases_two:{total_databases}")
    database = Database.query.get_or_404(database_id) # If it doesn't exist, return a 404
    schemas = (Schema.query
        .filter_by(owner=current_user, database_id=database.id)
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
        tables = SchemaTable.query.filter_by(database_id=database_id).all()
        for table in tables:
            db.session.delete(table)
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
        tables = SchemaTable.query.filter_by(schema_id=schema_id).all()
        for table in tables:
            db.session.delete(table)
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











import os
import logging
from werkzeug.utils import secure_filename
import duckdb
import shutil

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
            
            schema_path = f"uploads/{current_user.id}/{database.database_name}/{schema.name}"
            logging.info(f"schema_path: {schema_path}")
            os.makedirs(schema_path, exist_ok=True)
            
            for file in files:
                new_filename = secure_filename(file.filename).replace('-', '_')
                table_name = new_filename.rsplit('.', 1)[0]
                file_path = os.path.join(schema_path, new_filename)
                logging.info(f"file path: {file_path}")
                # Save file using a method that ensures the file is closed
                file.save(file_path)
               
                conn = None
                try:
                    with duckdb.connect(f"uploads/{current_user.id}/{database.database_name}.db") as conn:
            
                        conn.execute(f"USE {schema.name}")
                        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}', all_varchar=1)")
                        conn.close()
                    
                    table = SchemaTable(database_id=database_id,
                                        schema_id=schema_id,
                                        name=table_name,
                                        table_columns="temptemp",
                                        owner_id=current_user.id)
                    db.session.add(table)
                    db.session.commit()
                except Exception as e:
                    logging.error(f"Error processing file {new_filename}: {str(e)}")
                    flash(f'Error processing file {new_filename}. Please try again.', 'danger')
                    db.session.rollback()
                finally:
                    if conn:
                        conn.close()
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except PermissionError:
                            logging.warning(f"Unable to remove file {file_path}. It may be in use.")
            
            flash('Data Successfully Uploaded.', 'success')
            return redirect(url_for('main.home'))
        
        except Exception as e:
            logging.error(f"Error during file upload process: {str(e)}")
            flash('An error occurred during the upload process. Please try again.', 'danger')
   
    return render_template('upload.html', form=form)








@databases.route("/editor", methods=['GET'])
@login_required
def editor_query():
    route_logger.info("Accessed databases.editor_query")
    print("QUERY RECIEVED")
    print(f"current user id: {current_user.id}")
    database_id = request.args.get('db_id', type=int)
    database_name = request.args.get('db_name', type=str)
    print(database_id)
    print(database_name)

    #if database_id == None:
    #    with duckdb.connect() as conn:
            



    schema_id = request.args.get('schema_id', type=int)
    schema_name = request.args.get('schema_name', type=str)
    print(schema_id)
    print(schema_name)



    query = request.args.get('query', type=str)
    print(f"THE QUERY IS: {query}")
    available_databases = Database.query.filter_by(owner = current_user).all()
    print(available_databases)
    databases = {}
    for database in available_databases:
        databases[database.database_name] = database.id
    print(databases)
    default_database = Database.query.get_or_404(database_id)
    if default_database:
        default_schema = Schema.query.get_or_404(schema_id)
    else: 
        default_schema = None


    try:
        query_object = get_query_object(query, current_user.id, default_db = default_database, default_schema = default_schema)
        if isinstance(query_object, dict):
            print(query_object['output'])
            query_string = Query(code=generate_uuid(16), content=query, owner_id=current_user.id, status='failed')
            db.session.add(query_string)
            db.session.commit()
            results =  {
            "status": {
                "code": 200,
                "message": "instant fail",
                "type": "unsuccessful"
            },
            "data": {
                "type": "message",
                "contents": str(query_object['output'])
            }
        }
            return Response(sj.dumps(results, ignore_nan=True), mimetype='application/json')
        else:
            results = query_object.execute_query()
    except ValueError as e:
        query_string = Query(code=generate_uuid(16), content=query, owner_id=current_user.id, status='failed')
        db.session.add(query_string)
        db.session.commit()
        results =  {
            "status": {
                "code": 200,
                "message": "instant fail",
                "type": "unsuccessful"
            },
            "data": {
                "type": "message",
                "contents": f"{str(e)} - sfdjk345hj2342jhf"
            }
        }
        return Response(sj.dumps(results, ignore_nan=True), mimetype='application/json')

    if results['status']['type'] != 'success':
        query_string = Query(code=generate_uuid(16), content=query, owner_id=current_user.id, status='failed')
    else:
        query_string = Query(code=generate_uuid(16), content=query, owner_id=current_user.id, status='success')
    db.session.add(query_string)
    db.session.commit()
        
    return Response(sj.dumps(results, ignore_nan=True), mimetype='application/json')





@databases.route("/databases", methods=['GET'])
@login_required
def get_databases():
    databases = Database.query.filter_by(owner=current_user).all()
    global_database = Database.query.get(1)
    databases.append(global_database)

    return jsonify([(str(db.id), db.database_name) for db in databases])




@databases.route("/<string:username>/databases/<int:database_id>/schemas", methods=['GET'])
@login_required
def get_schemas(username, database_id):
    if username != current_user.username:
        abort(403)
    
    database = Database.query.get_or_404(database_id)
    if database.owner != current_user and database.id != 1:
        abort(403)
    
    schemas = Schema.query.filter_by(database_id=database_id).all()
    return jsonify([(str(schema.id), schema.name) for schema in schemas])



@databases.route("/<string:username>/schemas/<int:schema_id>/tables", methods=['GET'])
@login_required
def get_tables(username, schema_id):
    if username != current_user.username:
        abort(403)
    
    schema = Schema.query.get_or_404(schema_id)
    if schema.owner != current_user and schema.database_id != 1:
        abort(403)
    
    tables = SchemaTable.query.filter_by(schema_id=schema_id).all()
    return jsonify([(str(table.id), table.name) for table in tables])







@databases.route("/<string:username>/databases", methods=['GET', 'POST'])
@login_required
def view_databases(username):
    route_logger.info('Accessed databases.view_databases')

    if username != current_user.username: abort(403)

    total_databases = request.args.get('total_databases', 'error', type=int)
    databases = (Database.query
        .filter_by(owner=current_user)
        .order_by(Database.date_created.desc())).all()
    
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    #global_database = Database.query.get_or_404(1)
    #databases.append(global_database)


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
                           databases=databases, user=current_user, form=form, image_file=image_file)



