import secrets
import os
from PIL import Image
from powerpy import mail
from flask import url_for, current_app

from flask_mail import Message

def save_picture(form_picture):
    """Saves a downsized version of an uploaded image with a random hex as the filename."""
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    output_size = (250,250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn




def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email.
"""
    mail.send(msg)


def send_activation_email(user):
    token = user.get_activation_token()
    msg = Message('Account Activation', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f"""To activate your account, visit the following link:
{url_for('users.activate_account', token=token, _external=True)}

If you did not create an account, simply ignore this email.
"""
    mail.send(msg)