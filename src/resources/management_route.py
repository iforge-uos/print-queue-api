from flask import Blueprint, request, render_template
from marshmallow.exceptions import ValidationError
from common.routing import custom_response
from common.auth import generate_hash_key, requires_access_level


management_view = Blueprint("management view", __name__)

@management_view.route('/', methods=['GET'])
def print_dashboard():
    """
    Gets the main print dashboard for the reps
    """
    return render_template('base_layout.html',page_title="Test")
    