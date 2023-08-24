import datetime
import logging
import time

from celery import Celery
from flask import current_app
from flask_mail import Message

from print_api.common import cache
from print_api.extensions import mail
from print_api.models import UserRole, User

logger = logging.getLogger()
celery = Celery(__name__, autofinalize=False)


@celery.task(bind=True)
def wait_task(self, sleep_time):
    """sample task that sleeps x seconds then returns the current datetime"""
    time.sleep(sleep_time)
    return datetime.datetime.now().isoformat()


@celery.task(bind=True)
def send_email(self, msg_data):
    """
    Sends the email.
    """
    app = current_app._get_current_object()
    msg = Message(
        subject=msg_data["subject"],
        recipients=msg_data["recipients"],
        html=msg_data["body"],
    )

    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(e)


@celery.task(bind=True)
def update_user_roles_in_cache(self, user_id):
    """
    Update a specific users role in the cache.
    """
    roles = UserRole.get_all_by_user(user_id)

    app = current_app._get_current_object()

    store = cache.RedisCache(
       uri=app.config["REDIS_URI"],
       ex=app.config["REDIS_EXPIRY"]
    )
    store.store_user_roles(user_id, roles)


@celery.task(bind=True)
def update_all_user_roles_in_cache(self):
    """
    Update all users roles in the cache.
    """
    users = User.query.all()

    app = current_app._get_current_object()

    store = cache.RedisCache(
       uri=app.config["REDIS_URI"],
       ex=app.config["REDIS_EXPIRY"]
    )
    for user in users:
        roles = UserRole.get_all_by_user(user.id)
        store.store_user_roles(user.id, roles)
