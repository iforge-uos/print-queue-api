import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
db_server_name = os.getenv("DB_HOST")
db_server_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")


class Config:
    ALLOWED_APP_VERSION = os.getenv("ALLOWED_APP_VERSION")
    API_PREFIX = os.getenv("API_PREFIX")
    PORT = os.getenv("PORT")
    LOG_LEVEL = os.getenv("LOG_LEVEL")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 200)) * 1024 * 1024
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{db_server_name}:{db_server_port}/{db_name}"


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{db_server_name}:{db_server_port}/{db_name}"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{db_server_name}:{db_server_port}/{db_name}"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
