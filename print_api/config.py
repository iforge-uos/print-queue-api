import os
from dataclasses import dataclass

from dotenv import load_dotenv, find_dotenv


@dataclass
class Config:
    username: str
    password: str
    db_server_name: str
    db_server_port: int
    db_name: str
    ALLOWED_APP_VERSION: str
    API_PREFIX: str
    PORT: int
    LOG_LOCATION: str
    LOG_MAX_SIZE: int
    LOG_TO_STDOUT: bool
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_DEFAULT_SENDER: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_TOKEN_EXPIRES: int
    JWT_ACCESS_TOKEN_EXPIRES: int
    MAX_CONTENT_LENGTH: int
    MAIL_USE_TLS: bool
    MAIL_USE_SSL: bool
    DEBUG: bool
    TESTING: bool
    SQLALCHEMY_TRACK_MODIFICATIONS: bool
    REDIS_URI: str
    REDIS_EXPIRY: int
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    RATELIMIT_STORAGE_URI: str
    RATELIMIT_DEFAULT: str
    RATELIMIT_STRATEGY: str
    SQLALCHEMY_DATABASE_URI: str
    ADVANCED_LEVEL: int
    EXPERT_LEVEL: int
    INSANE_LEVEL: int
    AUTOREVIEW_FAIL_THRESHOLD: float
    AUTOREVIEW_START_THRESHOLD: int
    AUTOREVIEW_TIME_THRESHOLD: int
    SENTRY_SAMPLES_RATE: float
    SENTRY_DSN: str


def load_env_vars(env_file):
    load_dotenv(find_dotenv(env_file), override=True)
    return Config(
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        db_server_name=os.getenv("POSTGRES_HOST"),
        db_server_port=int(os.getenv("POSTGRES_PORT")),
        db_name=os.getenv("POSTGRES_DB"),
        ALLOWED_APP_VERSION=os.getenv("ALLOWED_APP_VERSION"),
        API_PREFIX=os.getenv("API_PREFIX"),
        PORT=int(os.getenv("PORT")),
        LOG_LOCATION=os.getenv("LOG_LOCATION", "logs"),
        LOG_MAX_SIZE=int(os.getenv("LOG_MAX_SIZE", 10240)),
        LOG_TO_STDOUT=bool(os.getenv("LOG_TO_STDOUT", True)),
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PORT=int(os.getenv("MAIL_PORT")),
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
        JWT_REFRESH_TOKEN_EXPIRES=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 3600)),
        JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 2592000)),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", 200)) * 1024 * 1024,
        MAIL_USE_TLS=bool(os.getenv("MAIL_USE_TLS", True)),
        MAIL_USE_SSL=bool(os.getenv("MAIL_USE_SSL", False)),
        DEBUG=bool(os.getenv("DEBUG", False)),
        TESTING=bool(os.getenv("TESTING", False)),
        SQLALCHEMY_TRACK_MODIFICATIONS=bool(
            os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)
        ),
        REDIS_URI=os.getenv("REDIS_URI"),
        REDIS_EXPIRY=int(os.getenv("REDIS_EXPIRY", 3600)),
        CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL"),
        CELERY_RESULT_BACKEND=os.getenv("CELERY_RESULT_BACKEND"),
        RATELIMIT_STORAGE_URI=os.getenv("RATELIMIT_STORAGE_URI"),
        RATELIMIT_DEFAULT=os.getenv("RATELIMIT_DEFAULT"),
        RATELIMIT_STRATEGY=os.getenv("RATELIMIT_STRATEGY"),
        SQLALCHEMY_DATABASE_URI=f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}",
        ADVANCED_LEVEL=int(os.getenv("ADVANCED_LEVEL", 5)),
        EXPERT_LEVEL=int(os.getenv("EXPERT_LEVEL", 10)),
        INSANE_LEVEL=int(os.getenv("INSANE_LEVEL", 15)),
        AUTOREVIEW_FAIL_THRESHOLD=float(os.getenv("AUTOREVIEW_FAIL_THRESHOLD", 0.1)),
        AUTOREVIEW_START_THRESHOLD=int(os.getenv("AUTOREVIEW_START_THRESHOLD", 5)),
        AUTOREVIEW_TIME_THRESHOLD=int(os.getenv("AUTOREVIEW_TIME_THRESHOLD", 36000)),
        SENTRY_SAMPLES_RATE=float(os.getenv("SENTRY_SAMPLES_RATE", 0.0)),
        SENTRY_DSN=os.getenv("SENTRY_DSN", ""),
    )


def load_config(env):
    env_files = {
        "development": ".env.development",
        "production": ".env.production",
        "testing": ".env.testing",
    }
    if env not in env_files:
        raise ValueError("Invalid environment name")

    # Test if running inside Docker (e.g. env vars are already set)
    if os.getenv("POSTGRES_USER") is not None:
        print("Inside Docker we good :)")
        config = load_env_vars(".env.docker")
        return config
    print("Not inside Docker, loading env vars from file...")

    config = load_env_vars(env_files[env])

    if env == "development":
        config.DEBUG = True
        config.TESTING = False
    elif env == "production":
        config.DEBUG = False
        config.TESTING = False
    elif env == "testing":
        config.DEBUG = False
        config.TESTING = True

    return config
