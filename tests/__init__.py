import unittest
from unittest.mock import (
    patch,
)
from acky import AWS


class TestAWS(unittest.TestCase):

    @patch('botocore.session.get_session')
    def test_gets_session(self, _get_session):
        AWS('region', profile='profile')
        _get_session.assert_called()

    @patch('botocore.session.get_session')
    @patch('acky.iam.UserCollection.get_current')
    def test_gets_userinfo(self, _get_current_user, _get_session):
        aws = AWS('region')
        aws.userinfo
        _get_current_user.assert_called()

if __name__ == '__main__':
    unittest.main()
