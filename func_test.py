import unittest
from unittest.mock import MagicMock, patch
from app import login

class Tests (unittest.Testcase):
    def test_login(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        
        with patch ("app.request.get") as mock_requests_get:
            mock_requests_get.return_value = mock_response
            result = login()
            self.assertEqual(result,"google.com")
if __name__ == "__main__":
    unittest.main()
