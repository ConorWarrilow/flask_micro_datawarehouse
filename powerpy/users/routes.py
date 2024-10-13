from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, current_app, jsonify, make_response
from powerpy.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, UploadDatasetForm
from powerpy.posts.forms import PostForm
from powerpy.databases.forms import CreateFolderForm
from powerpy import db, bcrypt#, mail
from powerpy.models import User, Post, Database, Folder, Worksheet, Dashboard, Schema, Secrets, DataFile
from flask_login import login_user, current_user, logout_user, login_required
from flask_dropzone import Dropzone
from powerpy.users.utils import save_picture, send_reset_email, send_activation_email, prepare_activated_account

import secrets # So we can generate a random hex
import os # So we can get the file extension
from PIL import Image # So we can resize images before saving them
import logging
from werkzeug.utils import secure_filename
from powerpy.utils import Flash, generate_uuid
from sqlalchemy import text
import duckdb
import uuid
# similar to app = Flask(__name__)
users = Blueprint('users', __name__)

from datetime import datetime, timezone


log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'flask_logs.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
route_logger = logging.getLogger('route_logger')








@users.route("/register", methods=['GET', 'POST'])
def register():
    route_logger.info('Accessed users.register')
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_active=False)
        db.session.add(user)
        db.session.commit()
        send_activation_email(user)
        Flash.info("An activation email has been sent. Please check your email to activate your account.")
        return redirect(url_for('users.login'))
    return render_template('register.html', title='register', form=form)

@users.route("/activate_account/<token>", methods=['GET'])
def activate_account(token):
    user = User.verify_activation_token(token)
    if user is None:
        Flash.warning("Invalid or expired activation token.")
        return redirect(url_for('users.register'))
    if user.is_active:
        Flash.info("Account is already activated.")
        return redirect(url_for('users.login'))
    user.is_active = True
    db.session.commit()
    prepare_activated_account(user)

    Flash.success("Your account has been activated! You can now log in.")
    return redirect(url_for('users.login'))


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.is_active:
                Flash.warning("Please activate your account. Check your email for the activation link.")
                return redirect(url_for('users.login'))
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            Flash.error("Login unsuccessful. Please check email and password")
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            old_picture = current_user.image_file
            if 'default' not in old_picture:
                try:
                    os.remove(os.path.join(current_app.root_path, 'static/profile_pics', old_picture))
                except:
                    pass
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data 
        db.session.commit()
        flash('Your account has been updated.', 'success')
        return redirect(url_for('users.account'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email 
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = (Post.query
             .filter_by(author=user)
             .order_by(Post.date_posted.desc())
             .paginate(page=page, per_page=10)
    )
    return render_template('user_posts.html', posts=posts, user=user)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title= 'Reset Password', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token Invalid or Expired.', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        #flash(f"Account created for {form.username.data}!", 'success')
        flash(f"Your password has been updated.", 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form = form)

#@users.route("<username>/secrets", methods=['GET', 'POST'])
#@login_required
#def view_secrets(username):
#    route_logger.info('Accessed databases.view_databases')
#    if username != current_user.username: abort(403)
#    secrets = (Secrets.query
#        .filter_by(owner=current_user)
#        .order_by(Database.date_created.desc())).all()













































@users.route("/<string:username>/query", methods=['GET', 'POST'])
def query_interface(username):
    user = User.query.filter_by(username=username).first_or_404()
    if username != current_user.username:
        abort(403)  # HTTP response for a forbidden route

    databases = (Database.query
        .filter_by(owner=current_user)
        .order_by(Database.date_created.desc())
    ).all()
    
    worksheet = (Worksheet.query
        .filter_by(owner=current_user)
        .order_by(Worksheet.last_saved.desc())
        ).first()
    

    return render_template('query_interface.html', 
                           databases=databases, 
                           user=current_user, 
                           worksheet=worksheet,
                           legend='query',
                           title='query')





@users.route("/<string:username>/query/<code>", methods=['GET', 'POST'])
@login_required
def query(username, code):
    if username != current_user.username:
        abort(403)

    if request.method =='GET':


        root_folders = Folder.query.filter_by(owner=current_user, parent_id=None).order_by(Folder.last_updated.desc()).all()

        # Finding all the worksheets for that person
        all_worksheets = Worksheet.query.filter_by(owner=current_user).all()

        root_worksheets = [ws for ws in all_worksheets if ws.parent_id is None]

        worksheet = next((ws for ws in all_worksheets if ws.code == code), None)

        databases = Database.query.filter_by(owner=current_user).order_by(Database.date_created.desc()).all()
        dashboards = Dashboard.query.filter_by(owner=current_user).order_by(Dashboard.date_created.desc()).all()
        global_database = Database.query.get(1)
        databases.append(global_database)

        response = make_response(render_template('query_interface.html', 
                                                databases=databases,
                                                dashboards = dashboards,
                                                user=current_user, 
                                                worksheet=worksheet,
                                                root_folders=root_folders,
                                                root_worksheets=root_worksheets,
                                                title='query',
                                                legend='query'
                                                 ))
        response.headers['Content-Type'] = 'text/html'
        return response
    
    if request.method == 'POST':
        worksheet = Worksheet.query.filter_by(code=code).first()
        logging.info(f"worksheet code to be saved: {code}")
        worksheet_content = request.json.get('content')
        logging.info(f"worksheet content to be saved: {worksheet_content}")
        worksheet.worksheet_content = worksheet_content
        worksheet.last_saved = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"status": "success", "message": "Worksheet saved successfully"})











@users.route("/<username>/worksheets/<int:worksheet_id>/delete", methods=['POST', 'GET', 'DELETE'])
@login_required
def delete_worksheet(username, worksheet_id):
    route_logger.info("Accessed users.delete_worksheet")
    if username != current_user.username:
            abort(403)
    worksheet = Worksheet.query.get_or_404(worksheet_id)

    db.session.delete(worksheet)
    db.session.commit()

    return redirect(url_for('worksheets.view_worksheets', username=username))






@users.route("/<username>/worksheets/folder/<int:folder_id>/delete", methods=['POST'])
@login_required
def delete_folder(username, folder_id):

    if username != current_user.username:
        abort(403)
    # Get the folder to be deleted
    folder = Folder.query.get_or_404(folder_id)
    
    # Ensure that only the owner can delete the folder
    if folder.owner != current_user:
        abort(403)
    logging.info("deleting a folderrrrr")
    # Get all child folders and worksheets
    children_folders = Folder.query.filter_by(parent_id=folder_id).all()
    children_worksheets = Worksheet.query.filter_by(parent_id=folder_id).all()
    
    # Delete the child folders and worksheets
    for child_folder in children_folders:
        db.session.delete(child_folder)
    
    for child_worksheet in children_worksheets:
        db.session.delete(child_worksheet)
    
    # Delete the main folder
    db.session.delete(folder)
    
    # Commit all changes at once
    db.session.commit()

    return redirect(url_for('worksheets.view_worksheets', username=username))


@users.route("/<username>/worksheets/<int:folder_id>/worksheets", methods=['GET'])
@login_required
def get_folder_worksheets(username, folder_id):
    if username != current_user.username:
            abort(403)

    folder = Folder.query.get_or_404(folder_id)

    folders=folder.children
    worksheets=folder.worksheets

    return jsonify([(str(folder.id), folder.name) for folder in folders], 
                   [(str(worksheet.code), worksheet.name) for worksheet in worksheets])
    





@users.route("/dashboards")
def dashboards():
    return render_template('dashboards.html')







@users.route('/<string:username>/home/create-dashboard', methods=['POST', 'GET'])
@login_required
def create_dashboard(username):
    if username != current_user.username:
        abort(403)
    code = generate_uuid(16)
    dashboard = Dashboard(code = code, owner=current_user)
    db.session.add(dashboard)
    db.session.commit()

    return redirect(url_for('users.dashboard_interface', code=code, username=username))




@users.route('/<string:username>/dashboard/<code>', methods=['POST', 'GET'])
@login_required
def dashboard_interface(username, code):
    if username != current_user.username:
        abort(403)

    if request.method =='GET':

        dashboards = Dashboard.query.filter_by(owner=current_user).order_by(Dashboard.date_created.desc()).all()
        dashboard = next((dashboard for dashboard in dashboards if dashboard.code == code), None)


        dashboard = Dashboard.query.filter_by(owner=current_user, code=code)


        root_folders = Folder.query.filter_by(owner=current_user, parent_id=None).order_by(Folder.last_updated.desc()).all()

        # Finding all the worksheets for that person
        root_worksheets = Worksheet.query.filter_by(owner=current_user, parent_id = None).all()

        #root_worksheets = [ws for ws in all_worksheets if ws.parent_id is None]

        databases = Database.query.filter_by(owner=current_user).order_by(Database.date_created.desc()).all()

        response = make_response(render_template('dashboard_interface.html', 
                                                databases=databases, 
                                                user=current_user, 
                                                dashboards=dashboards,
                                                dashboard=dashboard,
                                                root_folders=root_folders,
                                                root_worksheets=root_worksheets,
                                                title='dashboard',
                                                legend='dashboard'
                                                 ))
        response.headers['Content-Type'] = 'text/html'
        return response
    
    # include later
    #if request.method == 'POST':
    #    dashboard = Worksheet.query.filter_by(code=code).first()
    #    logging.info(f"worksheet code to be saved: {code}")
    #    worksheet_content = request.json.get('content')
    #    logging.info(f"worksheet content to be saved: {worksheet_content}")
    #    worksheet.worksheet_content = worksheet_content
    #    worksheet.last_saved = datetime.now(timezone.utc)
    #    db.session.commit()
    #    return jsonify({"status": "success", "message": "Worksheet saved successfully"})