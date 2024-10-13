from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, current_app, jsonify, Response
from powerpy.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from powerpy.posts.forms import PostForm
from powerpy.databases.forms import UpdateDatabaseForm, CreateSchemaForm, CreateSchemaForDbForm, UploadDatasetForm, CreateDatabaseForm, UpdateSchemaForm, CreateFolderForm
from powerpy.utils import Flash, generate_uuid

from powerpy import db, bcrypt
from powerpy.models import User, Post, Database, Schema, DataFile, Dashboard
from flask_login import login_user, current_user, logout_user, login_required
from flask_dropzone import Dropzone
from powerpy.users.utils import save_picture, send_reset_email
from powerpy.worksheets.utils import worksheet_message
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
from powerpy.models import Worksheet, Folder
from datetime import datetime, timezone

from redis import Redis
import duckdb
import simplejson as sj
import logging
import uuid

worksheets = Blueprint('worksheets', __name__)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'flask_logs.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
route_logger = logging.getLogger('route_logger')



@worksheets.route('/<string:username>/worksheets', methods=['POST', 'GET'])
@login_required
def view_worksheets(username):
    route_logger.info('Accessed worksheets.view_worksheets')
    current_app.logger.info("THIS IS THE CURRENT APP LOGGER BRO")
    
    if username != current_user.username:
        abort(403)

    folders = Folder.query.filter_by(owner=current_user, parent_id=None).order_by(Folder.last_updated.desc()).all()
    worksheets = Worksheet.query.filter_by(owner=current_user, parent_id=None).order_by(Worksheet.last_saved.desc()).all()

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('worksheets/worksheets_new.html', folders=folders, worksheets=worksheets, image_file = image_file)



@worksheets.route('/<string:username>/worksheets/folder/<int:folder_id>', methods=['POST', 'GET'])
@login_required
def view_folder(username, folder_id):
    route_logger.info('Accessed worksheets.view_folder')
    if username != current_user.username:
        abort(403)  # Use 403 for forbidden, not 304

    folder = Folder.query.get_or_404(folder_id)
    folders = folder.children
    worksheets = folder.worksheets
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('worksheets/folder_new.html', 
                           username=username, 
                           folder=folder, 
                           folders=folders, 
                           worksheets=worksheets,
                           image_file=image_file)




@worksheets.route('/<string:username>/worksheets/<int:folder_id>/create-folder', methods=['POST', 'GET'])
@worksheets.route('/<string:username>/worksheets/create-folder', defaults={'folder_id': None}, methods=['POST', 'GET'])
@login_required
def create_folder(username, folder_id):
    route_logger.info("Accessed worksheets.create_folder")
    if username != current_user.username:
        abort(403)
    form = CreateFolderForm()

    if folder_id:
        parent_folder = Folder.query.get_or_404(folder_id)
        if parent_folder.parent_id:
            abort(403)

        if form.validate_on_submit():
            try:
                logging.info(f"Form validated. folder_id: {folder_id}")
                folder = Folder(name=form.folder_name.data, parent_id=folder_id, owner=current_user)
                db.session.add(folder)
                db.session.commit()

                return redirect(url_for('worksheets.view_folder', username=username, folder_id=folder_id))
            except Exception as e:
                logging.error(f"Error occurred during folder creation: {e}")
                db.session.rollback()
                Flash.danger('An error occurred while creating the folder. Please try again.')
        
        # Add return statement for GET request
        elif request.method == 'GET':
            logging.info(f"Received a GET request. folder_id: {folder_id}")
            return render_template('create_folder.html', username=username, form=form)

    # Handle case where folder_id is None (creating a root folder)
    if form.validate_on_submit():
        try:
            folder = Folder(name=form.folder_name.data, owner=current_user)
            db.session.add(folder)
            db.session.commit()

            return redirect(url_for('worksheets.view_worksheets', username=username))
        
        except Exception as e:
            logging.error(f"Error occurred during folder creation: {e}")
            db.session.rollback()
            Flash.danger('An error occurred while creating the folder. Please try again.')
    
    # Ensure errors are handled and return the form
    if form.errors:
        Flash.danger('There was a problem with your submission.')
        logging.warning(f"Form validation errors: {form.errors}")

    # Handle GET request when creating root folder or validation failure
    elif request.method == 'GET' or not form.validate_on_submit():
        return render_template('create_folder.html', username=username, form=form)

    # Catch-all return to avoid falling through
    return render_template('create_folder.html', username=username, form=form)
    




@worksheets.route('/<string:username>/worksheets/<int:folder_id>/create-worksheet', methods=['POST', 'GET'])
@worksheets.route('/<string:username>/home/create-worksheet', defaults={'folder_id': None}, methods=['POST', 'GET'])
@login_required
def create_worksheet(username, folder_id):
    route_logger.info('Accessed worksheets.create_worksheet')
    if username != current_user.username:
        abort(403)
    code = generate_uuid(16)

    if folder_id:
        worksheet = Worksheet(
            code = code,
            parent_id=folder_id,
            worksheet_content = "",
            owner=current_user
        )
        db.session.add(worksheet)
        db.session.commit()

        return redirect(url_for('users.query', code=code, username=username))

    worksheet = Worksheet(
        code = code,
        worksheet_content = "",
        owner=current_user
    )
    db.session.add(worksheet)
    db.session.commit()

    # Add print statements for debugging
    print(f"Worksheet created with code: {code}")

    return redirect(url_for('users.query', code=code, username=username))





#
#
#@worksheets.route("/<username>/worksheets/<string:worksheet_code>/delete", methods=['POST'])
#@login_required
#def delete_worksheet(username, worksheet_code):
#    route_logger.info(f"Accessed worksheets.delete_worksheet for user {username} and worksheet {worksheet_code}")
#    if username != current_user.username:
#        current_app.logger.warning(f"Unauthorized deletion attempt by {current_user.username} for {username}'s worksheet")
#        return jsonify({"success": False, "message": "Unauthorized"}), 403
#    
#    worksheet = Worksheet.query.filter_by(code=worksheet_code).first()
#    if not worksheet:
#        current_app.logger.warning(f"Worksheet {worksheet_code} not found for user {username}")
#        return jsonify({"success": False, "message": "Worksheet not found"}), 404
#
#    try:
#        db.session.delete(worksheet)
#        db.session.commit()
#        current_app.logger.info(f"Worksheet {worksheet_code} deleted successfully for user {username}")
#        return jsonify({"success": True, "message": "Worksheet deleted successfully"}), 200
#    except Exception as e:
#        db.session.rollback()
#        current_app.logger.error(f"Error deleting worksheet {worksheet_code} for user {username}: {str(e)}")
#        return jsonify({"success": False, "message": "Error deleting worksheet"}), 500
#
#

########### to do

# finish cleaning shit up
# make it so that you can flash messages without reloading the page
# get started on the dashboard, it's the next big part of the project and it doesn't rely on having perfect forms etc, who gives a fuck if someone has duplicate names for things, thats their fault.





@worksheets.route("/<username>/worksheets/<string:worksheet_code>/delete", methods=['POST'])
@login_required
def delete_worksheet(username, worksheet_code):
    route_logger.info(f"Accessed worksheets.delete_worksheet for user {username} and worksheet {worksheet_code}")
    current_app.logger.info("current app logger")
    if username != current_user.username:
        route_logger.warning(f"Unauthorized deletion attempt by {current_user.username} for {username}'s worksheet")
        return jsonify({"success": False, "message": "Unauthorized", "flash_message": "Unauthorized action.", "flash_category": "error"}), 403
    
    worksheet = Worksheet.query.filter_by(code=worksheet_code).first()
    if not worksheet:
        route_logger.warning(f"Worksheet {worksheet_code} not found for user {username}")
        return jsonify({"success": False, "message": "Worksheet not found", "flash_message": "Worksheet not found.", "flash_category": "error"}), 404

    try:
        db.session.delete(worksheet)
        db.session.commit()
        route_logger.info(f"Worksheet {worksheet_code} deleted successfully for user {username}")
        return jsonify({
            "success": True, 
            "message": "Worksheet deleted successfully",
            "flash_message": "Successfully Deleted.",
            "flash_category": "success"
        }), 200
    except Exception as e:
        db.session.rollback()
        route_logger.error(f"Error deleting worksheet {worksheet_code} for user {username}: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Error deleting worksheet",
            "flash_message": "Error deleting worksheet.",
            "flash_category": "error"
        }), 500
