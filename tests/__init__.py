import unittest
from mock import MagicMock, call, ANY
import inspect
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from acky.aws import AWS
from acky.api import AwsApiClient
import acky.ec2


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


class TestAwsCollection(unittest.TestCase):
    """The tests variable contains the functions to test.
    'get|create|destroy' is mapped to its corresponding botocore command,
    'args' provides additional argument names needed for calls, and
    'call' represents the expected keys in the response call.
    """
    tests = {'ACECollection':
                {'get': 'DescribeNetworkAcls',
                 'create': 'CreateNetworkAcl',
                 'destroy': 'DeleteNetworkAcl'},
             'ACLCollection':
                {'get': 'DescribeNetworkAcls',
                 'create': 'CreateNetworkAclEntry',
                 'destroy': 'DeleteNetworkAclEntry'},
             'ElasticIPCollection':
                {'get': 'DescribeAddresses',
                 'create': 'AllocateAddress',
                 'destroy': 'ReleaseAddress',
                 'call': {'get': ['response_data_key'],
                          'create': ['Domain'],
                          'destroy': ['AllocationId', 'response_data_key']}},
             'InstanceCollection':
                {'get': 'DescribeInstances',
                 'call': {'get': ['response_data_key']}},
                #,'create': 'CreatePlacementGroup'
                #,'destroy': 'DeleteKeyPair'}
             #'IpPermissionsCollection':
             #   {'get': 'DescribeSecurityGroups'},
             'KeyPairCollection':
                {'get': 'DescribeKeyPairs',
                 'create': 'CreateKeyPair',
                 'destroy': 'DeleteKeyPair',
                 'call': {'get': ['response_data_key'],
                          'create': ['KeyName'],
                          'destroy': ['KeyName']}},
             'PlacementGroupCollection':
                {'get': 'DescribePlacementGroups',
                 'create': 'CreatePlacementGroup',
                 'destroy': 'DeletePlacementGroup',
                 'call': {'get': ['response_data_key'],
                          'create': ['group_name', 'strategy'],
                          'destroy': ['group_name']}},
             'SecurityGroupCollection':
                {'get': 'DescribeSecurityGroups',
                 'create': 'CreateSecurityGroup',
                 'destroy': 'DeleteSecurityGroup',
                 'args': {'create': ['name', 'description']},
                 'call': {'get': ['response_data_key'],
                          'create': ['Description', 'GroupName'],
                          'destroy': ['GroupId']}},
             'SnapshotCollection':
                {'get': 'DescribeSnapshots',
                 'create': 'CreateSnapshot',
                 'destroy': 'DeleteSnapshot',
                 'call': {'get': ['response_data_key'],
                          'create': ['Description', 'VolumeId',
                                     'response_data_key'],
                          'destroy': ['SnapshotId']}},
             'SubnetCollection':
                {'get': 'DescribeSubnets',
                 'create': 'CreateSubnet',
                 'destroy': 'DeleteSubnet',
                 'args': {'create': ['VpcId', 'CidrBlock',
                                     'availability_zone']},
                 'call': {'get': ['response_data_key'],
                          'create': ['VpcId', 'CidrBlock',
                                     'response_data_key'],
                          'destroy': ['SubnetId', 'response_data_key']}},
             'TagCollection':
                {'get': 'DescribeTags',
                 'create': 'CreateTags',
                 'destroy': 'DeleteTags',
                 'args': {'create': ['resource_ids', 'tags']
                         ,'destroy': ['resource_ids', 'tags']},
                 'call': {'get': ['response_data_key'],
                          'create': ['resources', 'tags'],
                          'destroy': ['resources', 'tags']}},
             'VPCCollection':
                {'get': 'DescribeVpcs',
                 'create': 'CreateVpc',
                 'destroy': 'DeleteVpc',
                 'call': {'get': ['response_data_key']}},
             'VolumeCollection':
                {'get': 'DescribeVolumes',
                 'create': 'CreateVolume',
                 'destroy': 'DeleteVolume',
                 'args': {'create': ['az', 0]},
                 'call': {'get': ['response_data_key'],
                          'create': ['encrypted',
                                     'AvailabilityZone',
                                     'Size'],
                          'destroy': ['response_data_key', 'VolumeId']}}}
    for n, c in inspect.getmembers(acky.ec2):
        if inspect.isclass(c) and n in tests:
            tests[n]['class'] = c

    @patch('botocore.operation.Operation.call')
    def test_get_create_destroy(self, _call):
        for c, info in self.tests.items():
            instance = info['class'](AWS('us-east-1'))
            instance.call = MagicMock()
            arguments = {'get': [()],
                         'create': ['test'],
                         'destroy': ['test']}
            if 'args' in info.keys():
                arguments.update(info['args'])
                print arguments
            if 'get' in info:
                kwargs = {}
                if 'call' in info and 'get' in info['call']:
                    kwargs = {k: ANY for k in info['call']['get']}
                try:
                    print c, info['get'], arguments['get']
                    instance.get(*arguments['get'])
                    assert call(info['get'], **kwargs) in\
                        instance.call.mock_calls,\
                        'Incorrect get call by ' +\
                    '{} (expected {} in {})'.format(c,
                                                    call(info['get'],
                                                         **kwargs),
                                                    instance.call.mock_calls)
                except NotImplementedError: pass
            if 'create' in info:
                kwargs = {}
                if 'call' in info and 'create' in info['call']:
                    kwargs = {k: ANY for k in info['call']['create']}
                try:
                    instance.create(*arguments['create'])
                    assert call(info['create'], **kwargs) in\
                        instance.call.mock_calls,\
                        'Incorrect create call by ' + \
                    '{} (expected {} in {})'.format(c,
                                                    call(info['create'],
                                                         **kwargs),
                                                    instance.call.mock_calls)
                except NotImplementedError: pass
            if 'destroy' in info:
                kwargs = {}
                if 'call' in info and 'destroy' in info['call']:
                    kwargs = {k: ANY for k in info['call']['destroy']}
                try:
                    instance.destroy(*arguments['destroy'])
                    assert call(info['destroy'], **kwargs) in\
                        instance.call.mock_calls,\
                        'Incorrect destroy call by ' + \
                    '{} (expected {} in {})'.format(c,
                                                    call(info['destroy'],
                                                         **kwargs),
                                                    instance.call.mock_calls)
                except NotImplementedError: pass

if __name__ == '__main__':
    unittest.main()
