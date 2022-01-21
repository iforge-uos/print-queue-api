import json

from tests.common import BaseCase


class test_users(BaseCase):

    def test_user_add(self):
        payload = json.dumps({
            "name": "Samuel Piper",
            "email": "test@test.com",
            "social_credit_score": 5,
            "is_rep": True,
            "score_editable": True,
            "short_name": "Sam"
        })
        response = self.app.post('/api/auth/login', headers={"Content-Type": "application/json"}, data=payload)
        print(response)
        self.assertEqual(str, type(response.json['token']))
        self.assertEqual(200, response.status_code)
