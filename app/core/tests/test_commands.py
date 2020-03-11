from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase

class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        # need to simulate the connection to databse
        # if receives operational error then db is not ready
        # mocking the behavior 
        # whenever this is called (i.e. the __getitem__ function); it will replace it with this funcion
        # allows us to monitor how many times this shit is called
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)
    
    # need to pass in ts to 
    # replaces time.sleep function with a function that just returns true
    # when connecting to db thre is a 1 second sleep so adding this overrides the function so we don't have to wait
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # throw an operational error the first 5 times we try to connect to the db and then allow connection on the 6th try
            gi.side_effect=[OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
