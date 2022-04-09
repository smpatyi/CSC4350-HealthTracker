import unittest
from unittest.mock import MagicMock, patch
from urllib import response
from app import UserLogin, login
from app import add_new_data
from app import app
from flask_login import FlaskLoginClient
from flask import template_rendered

class Tests (unittest.TestCase):
    
    app.test_client_class = FlaskLoginClient
    #TestUser password is 123
    user = UserLogin.query.filter_by(username="TestUser").first()

    def test_add_new_data(self):
        with app.test_client(user=Tests.user) as client:
            response= client.post('/add_new_data', data={'height':"6'7''", 'weight':'190'}).data
            pass

if __name__ == "__main__":
    print("Running Tests")
    #app.config['LOGIN_DISABLED'] = True
    unittest.main()