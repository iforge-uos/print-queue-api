from flask import current_app
from flask_mail import Message
from print_api.models.user import user_model
from print_api.common.errors import InternalServerError
from print_api.extensions import mail
from threading import Thread
import time


COMPLETED_EMAIL_HEADER = "Your Print Has Finished"
COMPLETED_EMAIL_BODY = """
        Hi %s,

        Your 3D print job "%s" was finished at %s and is ready to collect from the iForge!

        iForge Team"""

FAILED_EMAIL_HEADER = "Sorry Your Print Has Failed"
FAILED_EMAIL_BODY = """
        Hi %s,

        Sadly your 3D print job "%s" was marked as failed at %s.
        If you pop in and talk to a rep we can help you make it work!

        iForge Team"""

REJECTED_EMAIL_HEADER = "Sorry Your Print Was Rejected"
REJECTED_EMAIL_BODY = """
        Hi %s,

        Sadly your 3D print job "%s" was rejected at %s.
        If you pop in and talk to a rep we can help you make it work!

        iForge Team"""

email_content = {
    'completed':
        {
            'header': COMPLETED_EMAIL_HEADER,
            'body': COMPLETED_EMAIL_BODY
        },
    'failed':
        {
            'header': FAILED_EMAIL_HEADER,
            'body': FAILED_EMAIL_BODY
        },
    'rejected':
        {
            'header': REJECTED_EMAIL_HEADER,
            'body': REJECTED_EMAIL_BODY
        }
    }


def email(user_id, job_name, status):
    """
    Emails the associated user with the print_job name and what type of message it is.
    :param int user_id: The id of the user
    :param str job_name: The name of the job
    :param str status: Either "completed", "failed" or "rejectd".
    :return bool success: True if successful else false.
    """
    user = user_model.get_user_by_id(user_id)
    if user is None:
        return False
    user_email = user.email

    if user.short_name is None:
        user_name = user.name
    else:
        user_name = user.short_name

    t = time.localtime()
    cur_time = time.strftime("%H:%M:%S", t)

    msg = Message(email_content[status]['header'], recipients=[user_email])
    msg.body = email_content[status]['body'] % (
        user_name, job_name, cur_time)

    app = current_app._get_current_object()
    # Send email in separate thread to make api run faster
    Thread(target=send_async_email, args=(app, msg)).start()

    return True


def send_async_email(app, msg):
    """
    Creates a new app on a thread to send the email to free up the main thread.
    :param app: a new app object created from the current_app context
    :param msg: the message object being sent
    :return: None
    """
    with app.app_context():
        try:
            mail.send(msg)
        except ConnectionRefusedError:
            raise InternalServerError("[MAIL SERVER] not working")
