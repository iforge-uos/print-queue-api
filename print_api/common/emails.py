import time

from flask import render_template

from print_api.common import tasks
from print_api.models import User

COMPLETED_EMAIL_HEADER = "Your Print Has Finished"
FAILED_EMAIL_HEADER = "Sorry Your Print Has Failed"
REJECTED_EMAIL_HEADER = "Sorry Your Print Was Rejected"

EMAIL_HEADERS = {
    "completed": COMPLETED_EMAIL_HEADER,
    "failed": FAILED_EMAIL_HEADER,
    "rejected": REJECTED_EMAIL_HEADER,
}


def email(user_id, job_name, status):
    """
    Emails the associated user with the print_job name and what type of message it is.
    :param int user_id: The id of the user
    :param str job_name: The name of the job
    :param str status: Either "completed", "failed" or "rejectd".
    :return bool success: True if successful else false.
    """
    user = User.get_user_by_id(user_id)
    if user is None:
        return False
    user_email = user.email

    if user.short_name is None:
        user_name = user.name
    else:
        user_name = user.short_name

    t = time.localtime()
    cur_time = time.strftime("%H:%M:%S", t)

    template_name = f"/emails/print_{status}.html"
    email_body = render_template(
        template_name,
        header_title=EMAIL_HEADERS[status],
        recipient_name=user_name,
        print_job_name=job_name,
        timestamp=cur_time,
    )

    msg_data = {
        "subject": EMAIL_HEADERS[status],
        "recipients": [user_email],
        "body": email_body,
    }

    # Dispatch to Celery
    tasks.send_email.apply_async(kwargs={"msg_data": msg_data})

    return True
