import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
server_name = os.getenv('DB_HOST')
server_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
mail_server = os.getenv('MAIL_SERVER')
mail_port =  os.getenv('MAIL_PORT')
mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')


class Development(object):
    """
    Development environment configuration
    """
    MAIL_SERVER = mail_server
    MAIL_PORT = mail_port
    MAIL_USERNAME = mail_username
    MAIL_PASSWORD = mail_password
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{server_name}:{server_port}/{db_name}"

class Production(object):
    """
    Production environment configurations
    """
    MAIL_SERVER = mail_server
    MAIL_PORT = mail_port
    MAIL_USERNAME = mail_username
    MAIL_PASSWORD = mail_password
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{server_name}:{server_port}/{db_name}"

class Testing(object):
    """
    Development environment configuration
    """
    MAIL_SERVER = mail_server
    MAIL_PORT = mail_port
    MAIL_USERNAME = mail_username
    MAIL_PASSWORD = mail_password
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False   
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{server_name}:{server_port}/{db_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

app_config = {
    'development': Development,
    'production': Production,
    'testing': Testing
}