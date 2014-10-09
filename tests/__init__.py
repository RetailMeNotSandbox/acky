import unittest
try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock
from acky.aws import AWS
from acky.api import AwsApiClient
import acky.s3
import botocore.session


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

    @patch('botocore.operation.Operation.call')
    @patch('botocore.service.Service.get_operation')
    def test_call(self, get_operation, call):
        self._HelpApiClient(AWS('region'))
        get_operation.assert_called()
        call.assert_called()


class TestS3(unittest.TestCase):
    """Mock tests for S3. Ensure botocore calls are correct and happening."""

    class _AWS(object):
        """AWS object for mock testing with only basic features."""
        def __init__(self):
            self.session = botocore.session.get_session()
            self.region = 'us-east-1'

        @property
        def s3(self):
            return acky.s3.S3(self)

    acky.aws.AWS = MagicMock(return_value=_AWS())
    aws = acky.aws.AWS()

    @patch('acky.s3.S3.call')
    @patch('botocore.operation.Operation.call')
    def test_get(self, boto_call, acky_call):
        self.aws.s3.get("s3://test/")
        acky_call.assert_called_with("ListObjects",
                                     response_data_key="Contents",
                                     Bucket="test", Delimiter="/")
        boto_call.assert_called()
        self.aws.s3.get("s3://")
        acky_call.assert_called_with("ListBuckets",
                                     response_data_key="Buckets")
        boto_call.assert_called()

    @patch('acky.s3.S3.call')
    @patch('botocore.operation.Operation.call')
    def test_create(self, boto_call, acky_call):
        self.aws.s3.create("s3://test/")
        acky_call.assert_called_with("CreateBucket", bucket="test")
        boto_call.assert_called()

    @patch('acky.s3.S3.call')
    @patch('botocore.operation.Operation.call')
    def test_destroy(self, boto_call, acky_call):
        self.aws.s3.destroy("s3://test/")
        acky_call.assert_called_with("DeleteBucket", bucket="test")
        boto_call.assert_called()

    @patch('acky.s3.S3.call')
    @patch('botocore.operation.Operation.call')
    def test_download(self, boto_call, acky_call):
        try:
            self.aws.s3.download("s3://test/a", "/tmp/test")
        except TypeError:
            # We can't actually write files with mocks.
            pass
        acky_call.assert_called_with("GetObject", bucket="test", key='a')
        boto_call.assert_called()

    @patch('acky.s3.S3.call')
    @patch('botocore.operation.Operation.call')
    def test_copy(self, boto_call, acky_call):
        self.aws.s3.copy("s3://test/", "s3://test2/")
        acky_call.assert_called_with("CopyObject", copy_source="test/",
                                     key="", bucket="test2")
        boto_call.assert_called()

    @patch('acky.s3.S3.copy')
    @patch('acky.s3.S3.destroy')
    def test_move(self, destroy, copy):
        self.aws.s3.move("s3://test/a", "s3://test/b")
        copy.assert_called_with("s3://test/a", "s3://test/b")
        destroy.assert_called_with("s3://test/a")


if __name__ == '__main__':
    unittest.main()
