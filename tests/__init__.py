import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from acky.aws import AWS
from acky.api import AwsApiClient


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


class TestAwsApiClient(unittest.TestCase):
    class _HelpApiClient(AwsApiClient):
        service_name = "support"

    @patch('botocore.service.get_service')
    def test_gets_service(self, _get_service):
        self._HelpApiClient(AWS('region'))
        _get_service.assert_called()

    @patch('botocore.service.get_endpoint')
    def test_gets_endpoint(self, _get_endpoint):
        self._HelpApiClient(AWS('region'))
        _get_endpoint.assert_called()

    @patch('botocore.operation.Operation.call')
    @patch('botocore.service.Service.get_operation')
    def test_call(self, get_operation, call):
        self._HelpApiClient(AWS('region'))
        get_operation.assert_called()
        call.assert_called()


if __name__ == '__main__':
    unittest.main()
