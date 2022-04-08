import unittest
from dotenv import load_dotenv

from print_api.app import create_app

load_dotenv("../.env.test")


class BaseCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.db = self.app.db

    def tearDown(self):
        # Delete Database collections after the test is complete
        for collection in self.db.list_collection_names():
            self.db.drop_collection(collection)
