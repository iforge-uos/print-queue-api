import os
from dotenv import find_dotenv, load_dotenv
from print_api import create_app
load_dotenv(find_dotenv())


if __name__ == "__main__":
    app = create_app(config_env="development")
    app.run(host="127.0.0.1", port=app.config["PORT"])
