import os

class Config:
    SECRET_KEY = 'ee70bd9301abb031758830dce49fe3c8'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    #MAIL_USERNAME = 'conorwarrilow@gmail.com'
    #MAIL_PASSWORD = 'clbp riov tvyr ayqv'
    MAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    #DROPZONE_UPLOAD_MULTIPLE = True
    #DROPZONE_ALLOWED_FILE_CUSTOM = True
    #DROPZONE_ALLOWED_FILE_TYPE = 'image/*, .pdf, .txt, .csv',
    #DROPZONE_MAX_FILE_SIZE = 0.5
    ##DROPZONE_UPLOAD_FOLDER = 'uploads'
    #DROPZONE_ENABLE_CSRF = False
    #DROPZONE_MAX_FILES = 3
    #DROPZONE_UPLOAD_ON_CLICK = True
    #DROPZONE_PARALLEL_UPLOADS = 3
    #DROPZONE_UPLOAD_ACTION = 'upload'
    #DROPZONE_REDIRECT_VIEW = 'home'

    DROPZONE_ALLOWED_FILE_TYPE = 'image, .csv'
    DROPZONE_MAX_FILE_SIZE = 5  # Set a size limit (in MB)
    DROPZONE_MAX_FILES = 1
    DROPZONE_UPLOAD_MULTIPLE = False
    DROPZONE_PARALLEL_UPLOADS = 1
    DROPZONE_REDIRECT_VIEW = 'users.upload'