from flask import current_app
from flask_mail import Message
from print_api.models.user import user_model
from print_api.resources.api_routes.user_route import calculate_level_from_score
from print_api.common.errors import InternalServerError
from print_api.extensions import mail
from threading import Thread
import time


FINISHED_EMAIL_HEADER = "Your Print Has Finished"
FINISHED_EMAIL_BODY = """
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

email_type_struct = [[FINISHED_EMAIL_HEADER, FINISHED_EMAIL_BODY], [
    FAILED_EMAIL_HEADER, FAILED_EMAIL_BODY], [REJECTED_EMAIL_HEADER, REJECTED_EMAIL_BODY]]


def email(user_id, job_name, email_type):
    """
    Emails the associated user with the print_job name and what type of message it is.
    :param int user_id: The id of the user
    :param str job_name: The name of the job
    :param int email_type: Either 0, 1 or 2. With 0 being completed, 1 being a failure and 2 being a rejection.
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

    msg = Message(email_type_struct[email_type][0], recipients=[user_email])
    msg.body = email_type_struct[email_type][1] % (
        user_name, job_name, cur_time)

    app = current_app._get_current_object()
    # Send email in separate thread to make api run faster
    Thread(target=send_async_email, args=(app, msg)).start()

    update_user_score(user, email_type)
    return True


def update_user_score(user, email_type):
    """
    Updates the user score for the given user depending on how the print_job went
    :param user: the user object associated with the print_job
    :param int email_type: Either 0, 1 or 2. With 0 being completed, 1 being a failure and 2 being a rejection.
    :return: None
    """
    data = {}
    cur_score = user.user_score
    if email_type == 0:  # completed
        new_score = cur_score + 1
        data['complete_count'] = user.complete_count + 1
    elif email_type == 1:  # failed
        new_score = cur_score - 1
        data['fail_count'] = user.fail_count + 1
    else:  # rejected
        new_score = cur_score - 1
        data['reject_count'] = user.reject_count + 1

    if new_score < 1:
        new_score = 1
    new_level = calculate_level_from_score(new_score)

    # Load updated data into the user_schema
    data['user_score'] = new_score
    data['user_level'] = new_level
    user.update(data)


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
