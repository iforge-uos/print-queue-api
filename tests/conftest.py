import pytest
import psycopg2
from print_api.app import create_app


@pytest.fixture()
def app():
    app = create_app("testing")
    yield app

    # clean up / reset resources here


@pytest.fixture
def init_database():
    # Connect to the test database
    conn = psycopg2.connector.connect(
        # TODO replace with env vars
        user="user",
        password="password",
        host="localhost",
        database="testdb",
    )
    cursor = conn.cursor()

    # Read the initialization queries from a file
    # TODO fix mappings of file and write it
    with open("init.sql", "r") as f:
        queries = f.read()

    # Execute the initialization queries
    cursor.execute(queries)
    conn.commit()

    # Yield control back to the test function
    yield

    # Close the connection to the test database
    cursor.close()
    conn.close()


def delete_database():
    # TODO IMPLEMENT
    pass


@pytest.fixture()
def client(app):
    test_client = app.test_client()

    def set_x_api_key(response):
        response.headers["x-api-key"] = "test"
        return response

    test_client.application.after_request(set_x_api_key)
    return test_client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
