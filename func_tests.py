from doctest import FAIL_FAST
import unittest
from unittest.mock import MagicMock, patch
from urllib import response
from app import UserLogin, login
from app import add_new_data
from app import app
from display import BMI
from flask_login import FlaskLoginClient

class Tests (unittest.TestCase):
    
    app.test_client_class = FlaskLoginClient
    #TestUser password is 123
    user = UserLogin.query.filter_by(username="TestUser").first()

    def test_add_new_data(self):
        with app.test_client(user=Tests.user) as client:
            response= client.post('/add_new_data', data={'height':"6'7''", 'weight':'190'}).data
            pass

    def test_BMI(self):
        return_value = BMI(180, "6'1''")
        print(return_value)
        return_value = return_value
        expected = 23.7
        self.assertAlmostEquals(return_value, expected, 1)

if __name__ == "__main__":
    print("Running Tests")
    #app.config['LOGIN_DISABLED'] = True
    unittest.main()