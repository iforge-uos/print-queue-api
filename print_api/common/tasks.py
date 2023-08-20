import datetime
import time
import logging
from celery import Celery
from flask import current_app
from flask_mail import Message
from print_api.extensions import mail


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
        body=msg_data["body"]
    )

    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(e)
