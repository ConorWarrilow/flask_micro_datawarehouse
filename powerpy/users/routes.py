from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, current_app, jsonify
from powerpy.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, UploadDatasetForm
from powerpy.posts.forms import PostForm
from powerpy.databases.forms import CreateFolderForm
from powerpy import db, bcrypt#, mail
from powerpy.models import User, Post, Database, Folder, Worksheet, Dashboard
from flask_login import login_user, current_user, logout_user, login_required
from flask_dropzone import Dropzone
from powerpy.users.utils import save_picture, send_reset_email, send_activation_email

import secrets # So we can generate a random hex
import os # So we can get the file extension
from PIL import Image # So we can resize images before saving them
import logging
from werkzeug.utils import secure_filename
from powerpy.utils import Flash
# similar to app = Flask(__name__)
users = Blueprint('users', __name__)

from datetime import datetime, timezone

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)  # Create the logs directory if it doesn't exist

logging.basicConfig(
    filename=os.path.join(log_dir, 'powerpy.log'),
    level=logging.INFO,  # Adjust the logging level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'
)


import uuid

def generate_uuid(length: int) -> str:
    random_string = uuid.uuid4().hex[:length]
    return random_string






# old
#@users.route("/register", methods=['GET', 'POST'])
#def register():
#    if current_user.is_authenticated:
#        return redirect(url_for('main.home')) # If you're already logged in, then clicking register will redirect you
#    form = RegistrationForm()
#    if form.validate_on_submit():
#        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#        user = User(username=form.username.data, email = form.email.data, password=hashed_password)
#        db.session.add(user)
#        db.session.commit()
#        #flash(f"Account created for {form.username.data}!", 'success')
#        Flash.success("Your account has been created!")
#        return redirect(url_for('users.login'))
#    return render_template('register.html', title='register', form = form)


# new
@users.route("/register", methods=['GET', 'POST'])
def register():
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


#@users.route("/register/<token>", methods=['GET', 'POST'])
#def register_token():
#    if current_user.is_authenticated:
#        return redirect(url_for('main.home'))

# new
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
    Flash.success("Your account has been activated! You can now log in.")
    return redirect(url_for('users.login'))












# old
#@users.route("/login", methods=['GET', 'POST'])
#def login():
#    if current_user.is_authenticated:
#        return redirect(url_for('main.home')) # If you're already logged in, then clicking register will redirect you
#
#    form = LoginForm()
#    if form.validate_on_submit():
#        user = User.query.filter_by(email=form.email.data).first()
#        if user and bcrypt.check_password_hash(user.password, form.password.data):
#            login_user(user, remember=form.remember.data)
#            next_page = request.args.get('next') # used to redirect to the page you were actually trying to access e.g. someone tried going to 'account' when they weren't logged in,
#            # when they log in they'll be redirected to 'account' instead of home 
#            return redirect(next_page) if next_page else redirect(url_for('main.home'))
#        else:
#            Flash.danger("Login unsuccessful. Please check email and password")
#    return render_template('login.html', title='login', form = form)


# new
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












    




# Creating a route that changes based on whether you're logged in or not (layout.html changes based on whether you're logged in or not)
@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))



# Creating a route that only logged in users can access
@users.route("/account", methods=['GET', 'POST'])
@login_required # ensures only logged in users can access the route, in __init__.py we need login_manager.login_view = 'login'
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            old_picture = current_user.image_file
            if 'default' not in old_picture:
                os.remove(os.path.join(current_app.root_path, 'static/profile_pics', old_picture))
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data # Sets the updated value
        current_user.email = form.email.data # Sets the updated value
        db.session.commit() # Commits the updated values
        flash('Your account has been updated.', 'success')
        return redirect(url_for('users.account')) # This line is used to avoid the 'POST GET redirect pattern'.
    
    # If we refresh the page, it'll set the below values as the default values within the form
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








# Version 1
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


from flask import make_response












def worksheet_message(username, creation_time):
    return f"""-- Welcome, {username}.
-- Worksheet created on {creation_time}.

-- You can start writing your SQL queries below.

-- Example: SELECT * FROM your_table LIMIT 10;

-- Enjoy!
"""




# Version 2 (part 1)


@users.route('/<string:username>/worksheets/<int:folder_id>/create-worksheet', methods=['POST', 'GET'])
@users.route('/<string:username>/home/create-worksheet', defaults={'folder_id': None}, methods=['POST', 'GET'])
@login_required
def create_worksheet(username, folder_id):
    if username != current_user.username:
        abort(403)
    code = generate_uuid(16)

    if folder_id:
        worksheet = Worksheet(
            code = code,
            parent_id=folder_id,
            worksheet_content = worksheet_message(username, datetime.now(timezone.utc)),
            owner=current_user
        )
        db.session.add(worksheet)
        db.session.commit()

        return redirect(url_for('users.query', code=code, username=username))

    worksheet = Worksheet(
        code = code,
        worksheet_content = worksheet_message(username, datetime.now(timezone.utc)),
        owner=current_user
    )
    db.session.add(worksheet)
    db.session.commit()

    # Add print statements for debugging
    print(f"Worksheet created with code: {code}")

    return redirect(url_for('users.query', code=code, username=username))






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
        logging.info(dashboards)
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







@users.route('/<string:username>/worksheets', methods=['POST', 'GET'])
@login_required
def view_worksheets(username):
    if username != current_user.username:
        abort(403)

    folders = Folder.query.filter_by(owner=current_user, parent_id=None).order_by(Folder.last_updated.desc()).all()
    worksheets = Worksheet.query.filter_by(owner=current_user, parent_id=None).order_by(Worksheet.last_saved.desc()).all()

    # Combine both folders and worksheets into a single list with a type indicator
    #items = [{'type': 'folder', 'data': folder} for folder in folders] + [{'type': 'worksheet', 'data': worksheet} for worksheet in worksheets]
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('worksheets_new.html', user=current_user, folders=folders, worksheets=worksheets, image_file = image_file)




   # elif request.method == 'DELETE':



@users.route("/<username>/worksheets/<int:worksheet_id>/delete", methods=['POST', 'GET', 'DELETE'])
@login_required
def delete_worksheet(username, worksheet_id):

    if username != current_user.username:
            abort(403)
    worksheet = Worksheet.query.get_or_404(worksheet_id)

    db.session.delete(worksheet)
    db.session.commit()

    return redirect(url_for('users.view_worksheets', username=username))

    




@users.route('/<string:username>/worksheets/<int:folder_id>/create-folder', methods=['POST', 'GET'])
@users.route('/<string:username>/worksheets/create-folder', defaults={'folder_id': None}, methods=['POST', 'GET'])
@login_required
def create_folder(username, folder_id):
    if username != current_user.username:   
        abort(403)
    form = CreateFolderForm()

    if folder_id:

        parent_folder=Folder.query.get_or_404(folder_id)
        if parent_folder.parent_id:
            abort(403)

        if form.validate_on_submit():
            logging.info(f"form validated. folder_id: {folder_id}")
            folder = Folder(name=form.folder_name.data,

                        parent_id = folder_id,
                        owner=current_user)
            db.session.add(folder)
            db.session.commit()

            return redirect(url_for('users.view_folder', username=username, folder_id=folder_id))
        
        elif request.method == 'GET':
            logging.info(f"recieved a get request. folder_id: {folder_id}")
            return render_template('create_folder.html', username=username, form=form)


    elif form.validate_on_submit():
        folder = Folder(name=form.folder_name.data,

                        owner=current_user)
        db.session.add(folder)
        db.session.commit()

        return redirect(url_for('users.view_worksheets', username=username))
    


    elif request.method == 'GET':

        return render_template('create_folder.html', username=username, form=form)












#@users.route('/<string:username>/worksheets/<int:folder_id>', methods=['POST', 'GET'])
#@login_required
#def create_child_folder(username, folder_id):
#    if username != current_user.username:
#        abort(403)
#    form = CreateFolderForm()
#    if form.validate_on_submit():
#
#        folder = Folder(name=form.folder_name.data,
#                    code=form.folder_name.data + '-' + generate_uuid(8),
#                    parent_id = folder_id,
#                    owner=current_user)
#        
#        db.session.add(folder)
#        db.session.commit()
#        redirect(url_for('users.view_folder', username=username,
#                                                    folder=folder))
#
#    # Add print statements for debugging
#    elif request.method == 'GET':
#
#        return render_template('create_root_folder.html', username=username, form=form)





@users.route('/<string:username>/worksheets/folder/<int:folder_id>', methods=['POST', 'GET'])
@login_required
def view_folder(username, folder_id):
    if username != current_user.username:
        abort(403)  # Use 403 for forbidden, not 304

    # Get the folder by id
    folder = Folder.query.get_or_404(folder_id)

    # Get children folders and worksheets
    child_folders = folder.children
    worksheets = folder.worksheets

    # Pass the folder, child folders, and worksheets to the template
    return render_template('folder.html', 
                           username=username, 
                           folder=folder, 
                           child_folders=child_folders, 
                           worksheets=worksheets)





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

    return redirect(url_for('users.view_worksheets', username=username))






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
    







@users.route('/folder')
def debug_view_folder():
    return render_template('debug_view_folder.html')

@users.route('/folders/<int:folder_id>')
def debug_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    children = folder.children
    worksheets = folder.worksheets

    # Convert the data to JSON format
    folder_data = {
        'id': folder.id,
        'name': folder.name
    }

    children_data = [{'id': child.id, 'name': child.name} for child in children]
    worksheets_data = [{'id': worksheet.id, 'name': worksheet.name} for worksheet in worksheets]

    # Return as JSON response
    return jsonify(folder=folder_data, children=children_data, worksheets=worksheets_data)


























@users.route("/dashboards")
def dashboards():
    return render_template('dashboards.html')



#
#
#
#@users.route("/<username>/database/<int:database_id>", methods=['GET', 'POST'])
#@login_required
#def post(username, database_id):
#    user = User.query.filter_by(username=username).first_or_404()
#    if user != current_user:
#        abort(403)  # HTTP response for a forbidden route
#
#
#    database = Database.query.get_or_404(database_id) # If it doesn't exist, return a 404
#
#    return render_template('database.html', title=database.title, database=database)
#
#




from powerpy import db

from flask import current_app
from sqlalchemy import text

@users.route("/explain_queries")
def explain_queries():
    # Create raw SQL statements for EXPLAIN
    explain_id_query = text("EXPLAIN SELECT * FROM worksheet WHERE id = 1")
    explain_code_query = text("EXPLAIN SELECT * FROM worksheet WHERE code = 'ABC123'")

    # Execute the raw SQL queries
    result_id = current_app.db.session.execute(explain_id_query).fetchall()
    result_code = current_app.db.session.execute(explain_code_query).fetchall()

    # Print or return the EXPLAIN output
    return {
        'explain_id': [dict(row) for row in result_id],
        'explain_code': [dict(row) for row in result_code]
    }












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