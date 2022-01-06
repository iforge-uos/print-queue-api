from flask import current_app
from flask_mail import Message
from models.user import user_model
from resources.user_route import calculate_level_from_score
from common.errors import InternalServerError
from extensions import mail
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

email_type_struct = [[FINISHED_EMAIL_HEADER, FINISHED_EMAIL_BODY], [FAILED_EMAIL_HEADER, FAILED_EMAIL_BODY], [REJECTED_EMAIL_HEADER, REJECTED_EMAIL_BODY]]

def email(user_id, job_name, email_type):
    """
    Emails the associated user with the print_job name and what type of message it is.
    Arguments:
        user_id: The id of the user
        job_name: The name of the job
        email_type: Either 0, 1 or 2. With 0 being completed, 1 being a failure and 2 being a rejection.
    Returns:
        True if successful else false.
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

    msg = Message(email_type_struct[email_type][0],recipients=[user_email])
    msg.body = email_type_struct[email_type][1]%(user_name, job_name, cur_time)

    app = current_app._get_current_object()
    # Send email in separate thread to make api run faster
    Thread(target=send_async_email, args=(app,msg)).start()
    
    update_user_score(user, type)
    return True

def update_user_score(user, email_type):
    cur_score = user.social_credit_score
    if email_type == 0:
        new_score = cur_score + 1
    else:
        new_score = cur_score - 1
    if new_score < 1:
        new_score = 1
    new_level = calculate_level_from_score(new_score)
    
    # Load updated data into the user_schema
    data = {"social_credit_score" : new_score, "user_level" : new_level}
    user.update(data)


def send_async_email(app,msg):
    with app.app_context():
        try:
            mail.send(msg)
        except ConnectionRefusedError:
            raise InternalServerError("[MAIL SERVER] not working")