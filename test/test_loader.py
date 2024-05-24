import unittest
from unittest.mock import patch, Mock
from loader import Loader, SessionConfig


class TestLoader(unittest.TestCase):

    @patch("loader.requests.get")
    def test_loader_start(self, mock_get):
        # Set up the mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Create a session config for the test
        session_config = SessionConfig(
            url="http://example.com", headers={}, timeout=1
        )

        # Initialize the Loader
        loader = Loader(session_config, qps=30, duration=5)

        # Start the loader
        loader.start()

        # Check if the requests.get was called the expected number of times
        self.assertEqual(mock_get.call_count, 150)

        # Check that it took around 5 seconds
        duration = loader.end_time-loader.start_time
        self.assertGreater(duration, 4.9)
        self.assertLessEqual(duration, 5.1)

        # Verify that the status codes are as expected
        for task in loader.tasks:
            self.assertEqual(task.status, 200)


if __name__ == "__main__":
    unittest.main()
