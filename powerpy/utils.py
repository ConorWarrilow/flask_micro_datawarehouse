from flask import flash
import re
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
import os
from typing import List, Union
from flask_wtf import FlaskForm
import logging
from logging.handlers import RotatingFileHandler
import os
import uuid


class Flash:
    @staticmethod
    def _escape(message):
        """Escape some characters in a message to make them HTML friendly.

        Args:
            message (str): The string to process.

        Returns:
            str: Escaped string.
        """
        translations = {
            '"': '&quot;',
            "'": '&#39;',
            '`': '&lsquo;',
            '\n': '<br>',
        }
        for k, v in translations.items():
            message = message.replace(k, v)
        return message

    @classmethod
    def default(cls, message):
        return flash(cls._escape(message), 'default')

    @classmethod
    def success(cls, message):
        return flash(cls._escape(message), 'success')

    @classmethod
    def info(cls, message):
        return flash(cls._escape(message), 'info')

    @classmethod
    def warning(cls, message):
        return flash(cls._escape(message), 'warning')

    @classmethod
    def danger(cls, message):
        return flash(cls._escape(message), 'danger')

    @classmethod
    def well(cls, message):
        return flash(cls._escape(message), 'well')

    @classmethod
    def modal(cls, message):
        return flash(cls._escape(message), 'modal')
    










class CustomValidator:
    """
    A class containing custom validators for form fields.

    This class includes methods for validating field data based on allowed character sets.
    You can use these validators to enforce rules such as allowing only letters, numbers,
    underscores, hyphens, etc., in a form field.

    Methods
    -------
    regex(form: FlaskForm, field: object, characters: List[str]) -> None
        Validates that the field data contains only the allowed characters based on the provided list.
    """

    @staticmethod
    def regex(field: object, characters: List[str]) -> None:
        """
        Custom validator to check if a field contains only allowed characters.

        Parameters
        ----------
        field : object
            The field instance being validated. Typically, this would be an instance of a specific
            field type from wtforms, such as StringField.
        characters : List[str]
            A list of strings specifying which characters are allowed. The possible values are:
            - 'letters': Allows both lowercase and uppercase letters.
            - 'numbers': Allows digits (0-9).
            - 'underscores': Allows underscores (_).
            - 'hyphens': Allows hyphens (-).
            - Any combination of these values can be passed in the list.

        Raises
        ------
        ValidationError
            If the field contains characters that are not in the allowed set.
        """

        # Define character sets based on the input list
        count=0
        allowed_chars = ''
        if 'letters' in characters:
            allowed_chars += 'a-zA-Z'
            count +=1
        if 'numbers' in characters:
            allowed_chars += '0-9'
            count +=1
        if 'underscores' in characters:
            allowed_chars += '_'
            count +=1
        if 'hyphens' in characters:
            allowed_chars += '-'
            count +=1
        
        # Build the regex pattern dynamically
        pattern = f'^[{allowed_chars}]+$'

        # Validate the field data
        if not re.match(pattern, field.data):
                if count > 1:
                    raise ValidationError(f"This field can only contain {', '.join(characters[0:-1])} and {characters[-1]}.")
                else:
                    raise ValidationError(f"This field can only contain {characters[0]}.")



def generate_uuid(length: int) -> str:
    random_string = uuid.uuid4().hex[:length]
    return random_string


def configure_loggers(app):
    """
    Sets up two separate loggers:   

    1. **Standard Logger**:
       - Captures general logs

    2. **Route Logger**:
       - Logs the route being used for each request, make with the line number and path name. Makes it easy to track down the code when errors occur.
    """

    standard_log_dir = 'logs/standard_logs'
    route_log_dir = 'logs/route_logs'

    os.makedirs(standard_log_dir, exist_ok=True)
    os.makedirs(route_log_dir, exist_ok=True)

    standard_log_file = os.path.join(standard_log_dir, 'standard_logs.log')
    standard_log_handler = RotatingFileHandler(standard_log_file, maxBytes=100000, backupCount=100)
    standard_log_handler.setLevel(logging.INFO)
    standard_log_formatter = logging.Formatter('%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s - %(message)s')
    standard_log_handler.setFormatter(standard_log_formatter)
    app.logger.addHandler(standard_log_handler)
    
    route_logger = logging.getLogger('route_logger')
    route_logger.setLevel(logging.INFO)
    route_log_file = os.path.join(route_log_dir, 'route_logs.log') 
    route_log_handler = RotatingFileHandler(route_log_file, maxBytes=100000, backupCount=100)
    route_log_formatter = logging.Formatter('%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s - %(message)s')
    route_log_handler.setFormatter(route_log_formatter)
    route_logger.addHandler(route_log_handler)



