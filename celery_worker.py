import os
from print_api.app import celery, create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'development')
app.app_context().push()