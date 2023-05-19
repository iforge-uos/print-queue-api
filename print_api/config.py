import os
from dotenv import load_dotenv, find_dotenv

# Determine the app settings based on the FLASK_ENV variable
env = os.getenv("FLASK_ENV", "development")
# If FLASK_ENV is not set, it defaults to 'development'
if env == 'development':
    load_dotenv('.env.development')
elif env == 'production':
    load_dotenv('.env.production')
elif env == 'testing':
    load_dotenv('.env.testing')
else:
    raise ValueError('Invalid environment name')

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
db_server_name = os.getenv("DB_HOST")
db_server_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")


class Config:
    ALLOWED_APP_VERSION = os.getenv("ALLOWED_APP_VERSION")
    API_PREFIX = os.getenv("API_PREFIX")
    PORT = os.getenv("PORT")
    LOG_LOCATION = os.getenv("LOG_LOCATION", "logs")
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 10240))
    LOG_TO_STDOUT = os.getenv("LOG_TO_STDOUT", True)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 3600))
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 2592000))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 200)) * 1024 * 1024
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{db_server_name}:{db_server_port}/{db_name}"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
