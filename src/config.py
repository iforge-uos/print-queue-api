import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
server_name = os.getenv('DB_HOST')
server_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')


class Development(object):
    """
    Development environment configuration
    """
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{server_name}:{server_port}/{db_name}"

class Production(object):
    """
    Production environment configurations
    """
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{server_name}:{server_port}/{db_name}"

class Testing(object):
    """
    Development environment configuration
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{server_name}:{server_port}/{db_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

app_config = {
    'development': Development,
    'production': Production,
    'testing': Testing
}