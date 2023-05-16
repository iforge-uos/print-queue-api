import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from print_api.app import create_app

if __name__ == "__main__":
    app = create_app(config_env=os.getenv("ENV"))
    app.run(host="127.0.0.1", port=app.config["PORT"])
