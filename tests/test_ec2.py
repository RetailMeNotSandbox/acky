import botocore
import unittest
import acky
try:
    from unittest.mock import patch, call, ANY
except ImportError:
    from mock import patch, call, ANY

GENERIC_AID = "aid-123"
GENERIC_AMI = "ami-123"
GENERIC_SUBNET = "subnet-test"
GENERIC_IP = "8.8.8.8"
GENERIC_INSTANCE = "i-123"
GENERIC_VOL = "vol-123"
GENERIC_AMI_DESCRIPTION = "{0} description".format(GENERIC_AMI)

class _AWS(object):
    """AWS object for mock testing with only basic features."""
    def __init__(self):
        self.session = botocore.session.get_session()
        self.region = 'us-east-1'

    @property
    def ec2(self):
        return acky.ec2.EC2(self)


class TestRegions(unittest.TestCase):
    @patch('acky.api.AwsApiClient.call')
    def test_regions(self, _call):
        _AWS().ec2.regions()
        _call.assert_called_once_with("DescribeRegions",
                                      response_data_key=ANY)


class _TestEC2Collection():
    class_name = None
    commands = None
    get_args = [{}]
    get_expectations = None
    create_args = ['test']
    create_expectations = None
    destroy_args = ['test']
    destroy_expectations = None
    instance = None

    @patch('acky.api.AwsApiClient.call')
    def test_get(self, _call):
        """Generic testing method for get() calls. Modify get_args and
        get_expectations for better coverage.
        """
        for args, expectation in zip(self.get_args,
                                     self.get_expectations):
            try:
                self.instance.get(**args)
            except NotImplementedError:
                continue
            assert expectation in _call.mock_calls,\
                "Incorrect get call by {} (expected {} in {})".\
                format(self.class_name, expectation,
                       _call.mock_calls)

    @patch('acky.api.AwsApiClient.call')
    def test_create(self, _call):
        """Generic testing method for create() calls. Modify create_args and
        create_expectations for better coverage.
        """
        for args, expectation in zip(self.create_args,
                                     self.create_expectations):
            try:
                self.instance.create(**args)
            except NotImplementedError:
                continue
            assert expectation in _call.mock_calls,\
                "Incorrect create call by {} (expected {} in {})".\
                format(self.class_name, expectation,
                       _call.mock_calls)

    @patch('acky.api.AwsApiClient.call')
    def test_destroy(self, _call):
        """Generic testing method for destroy() calls. Modify destroy_args
        and destroy_expectations for better coverage.
        """
        for args, expectation in zip(self.destroy_args,
                                     self.destroy_expectations):
            try:
                self.instance.destroy(**args)
            except NotImplementedError:
                continue
            assert expectation in _call.mock_calls,\
                "Incorrect destroy call by {} (expected {} in {})".\
                format(self.class_name, expectation,
                       _call.mock_calls)


class TestACLCollection(_TestEC2Collection, unittest.TestCase):
    """Not implemented yet."""

    class_name = "ACLs"
    commands = {'get': 'DescribeNetworkAcls',
                'create': 'CreateNetworkAcl',
                'destroy': 'DeleteNetworkAcl'}
    get_expectations = [{}]
    create_args = [{'vpc': "test"}]
    create_expectations = [{}]
    destroy_args = [{'acl': "test"}]
    destroy_expectations = [{}]
    instance = _AWS().ec2.ACLs

'''
class TestACECollection(_TestEC2Collection, unittest.TestCase):
    """Not implemented yet."""
    class_name = "ACE"
    commands = {'get': 'DescribeNetworkAcls',
                'create': 'CreateNetworkAclEntry',
                'destroy': 'DeleteNetworkAclEntry'}
    get_expectations = [{}]
    create_args = [{}]
    create_expectations = [{}]
    destroy_args = [{}]
    destroy_expectations = [{}]
    instance = _AWS().ec2.ACEs
'''


class ElasticIPCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "EIPs"
    commands = {'get': 'DescribeAddresses',
                'create': 'AllocateAddress',
                'destroy': 'ReleaseAddress'}
    get_expectations = [call(commands['get'],
                             response_data_key="Addresses")]
    create_args = [{'vpc': True}, {'vpc': False}]
    create_expectations = [call(commands['create'],
                                Domain="vpc"),
                           call(commands['create'],
                                Domain="standard")]
    destroy_args = [{'eip_or_aid': GENERIC_IP},
                    {'eip_or_aid': GENERIC_AID, 'disassociate': False},
                    {'eip_or_aid': GENERIC_AID, 'disassociate': True}]
    destroy_expectations = [call(commands['destroy'],
                                 PublicIp='8.8.8.8',
                                 response_data_key="return"),
                            call(commands['destroy'],
                                 response_data_key="return",
                                 AllocationId=GENERIC_AID),
                            call(commands['destroy'],
                                 response_data_key="return",
                                 AllocationId=GENERIC_AID)]
    instance = _AWS().ec2.ElasticIPs

    @patch('acky.api.AwsApiClient.call')
    def test_associate(self, _call):
        associate_command = "AssociateAddress"
        associate_args = [{'eip_or_aid': GENERIC_IP, 'instance_id': "i-test"},
                          {'eip_or_aid': GENERIC_AID, 'instance_id': "i-test"},
                          {'eip_or_aid': GENERIC_AID,
                           'network_interface_id': "net-test"}]
        associate_expectations = [call(associate_command,
                                       PublicIp=GENERIC_IP,
                                       InstanceId="i-test",
                                       NetworkInterfaceId='',
                                       PrivateIpAddress=''),
                                  call(associate_command,
                                       AllocationId=GENERIC_AID,
                                       InstanceId="i-test",
                                       NetworkInterfaceId='',
                                       PrivateIpAddress=''),
                                  call(associate_command,
                                       AllocationId=GENERIC_AID,
                                       InstanceId='',
                                       NetworkInterfaceId="net-test",
                                       PrivateIpAddress='')]
        for args, expectation in zip(associate_args,
                                     associate_expectations):
            self.instance.associate(**args)
            assert expectation in _call.mock_calls,\
                "Incorrect associate call by {} (expected {} in {})".\
                format(self.class_name, expectation,
                       _call.mock_calls)

    @patch('acky.api.AwsApiClient.call')
    def test_disassociate(self, _call):
        disassociate_command = "DisassociateAddress"
        disassociate_args = [{'eip_or_aid': GENERIC_IP},
                             {'eip_or_aid': GENERIC_AID}]
        disassociate_expectations = [call(disassociate_command,
                                          response_data_key="return",
                                          PublicIp=GENERIC_IP),
                                     call(disassociate_command,
                                          response_data_key="return",
                                          AllocationId=GENERIC_AID)]
        for args, expectation in zip(disassociate_args,
                                     disassociate_expectations):
            self.instance.disassociate(**args)
            assert expectation in _call.mock_calls,\
                "Incorrect disassociate call by {} (expected {} in {})".\
                format(self.class_name, expectation,
                       _call.mock_calls)


class TestInstanceCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "Instances"
    commands = {'get': 'DescribeInstances',
                'create': 'RunInstances',
                'destroy': 'TerminateInstances'}
    get_expectations = [call(commands['get'],
                             response_data_key="Reservations")]
    create_args = [{'ami': GENERIC_AMI, 'count': 1}]
    create_expectations = [call('RunInstances', MinCount=1,
                                ImageId=GENERIC_AMI,
                                response_data_key='Instances', MaxCount=1)]
    destroy_args = [{'instance_id': GENERIC_INSTANCE}]
    destroy_expectations = [call(operation='TerminateInstances',
                                 response_data_key='TerminatingInstances',
                                 InstanceIds=[GENERIC_INSTANCE])]
    instance = _AWS().ec2.Instances

    @patch('acky.api.AwsApiClient.call')
    def test_control(self, _call):
        ctrl_data = {'start': {'operation': "StartInstances",
                               'response_data_key': "StartingInstances",
                               'InstanceIds': [GENERIC_INSTANCE]},
                     'stop': {'operation': "StopInstances",
                              'response_data_key': "StoppingInstances",
                              'InstanceIds': [GENERIC_INSTANCE]},
                     'reboot': {'operation': "RebootInstances",
                                'response_data_key': "return",
                                'InstanceIds': [GENERIC_INSTANCE]},
                     'terminate': {'operation': "TerminateInstances",
                                   'response_data_key': "TerminatingInstances",
                                   'InstanceIds': [GENERIC_INSTANCE]},
                     'protect': {'operation': "ModifyInstanceAttribute",
                                 'response_data_key': "return",
                                 'Attribute': 'disableApiTermination',
                                 'Value': 'true'},
                     'unprotect': {'operation': "ModifyInstanceAttribute",
                                   'response_data_key': "return",
                                   'Attribute': 'disableApiTermination',
                                   'Value': 'false'}}
        control_args = [{'instances': GENERIC_INSTANCE, 'action': "start"},
                        {'instances': GENERIC_INSTANCE, 'action': "stop"},
                        {'instances': GENERIC_INSTANCE, 'action': "protect"},
                        {'instances': GENERIC_INSTANCE, 'action': "unprotect"}]
        control_expectations = [call(operation=ctrl_data['start']['operation'],
                                     response_data_key=
                                     ctrl_data['start']['response_data_key'],
                                     InstanceIds=[GENERIC_INSTANCE]),
                                call(operation=ctrl_data['stop']['operation'],
                                     response_data_key='StoppingInstances',
                                     InstanceIds=['i-123']),
                                call(InstanceId='i-123',
                                     Attribute='disableApiTermination',
                                     operation=
                                     ctrl_data['protect']['operation'],
                                     response_data_key='return', Value='true'),
                                call(InstanceId='i-123',
                                     Attribute='disableApiTermination',
                                     operation=
                                     ctrl_data['protect']['operation'],
                                     response_data_key='return',
                                     Value='false')]
        for args, expectation in zip(control_args,
                                     control_expectations):
            self.instance.control(**args)
            assert expectation in _call.mock_calls,\
                "Incorrect control call by {} (expected {} in {})".\
                format(self.class_name, expectation,
                       _call.mock_calls)


class TestKeyCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "KeyPairs"
    commands = {'get': 'DescribeKeyPairs',
                'create': 'CreateKeyPair',
                'destroy': 'DeleteKeyPair'}
    get_expectations = [call('DescribeKeyPairs', response_data_key='KeyPairs')]
    create_args = [{'key_name': "test-key"}]
    create_expectations = [call('CreateKeyPair', KeyName='test-key')]
    destroy_args = [{'key_name': "test-key"}]
    destroy_expectations = [call('DeleteKeyPair', KeyName='test-key')]
    instance = _AWS().ec2.KeyPairs


class TestPlacementGroupCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "PlacementGroups"
    commands = {'get': 'DescribePlacementGroups',
                'create': 'CreatePlacementGroup',
                'destroy': 'DeletePlacementGroup'}
    get_expectations = [call('DescribePlacementGroups',
                             response_data_key='PlacementGroups')]
    create_args = [{'group_name': 'test-group'}]
    create_expectations = [call('CreatePlacementGroup',
                                group_name='test-group', strategy='cluster')]
    destroy_args = [{'pg': 'test-group'}]
    destroy_expectations = [call('DeletePlacementGroup',
                                 group_name='test-group')]
    instance = _AWS().ec2.PlacementGroups


class TestSecurityGroupCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "SecurityGroups"
    commands = {'get': 'DescribeSecurityGroups',
                'create': 'CreateSecurityGroup',
                'destroy': 'DeleteSecurityGroup'}
    get_expectations = [call(commands['get'],
                             response_data_key='SecurityGroups')]
    create_args = [{'name': "test-group", 'description': "test-description"}]
    create_expectations = [call(commands['create'], GroupName='test-group',
                                Description='test-description')]
    destroy_args = [{'sg': "test-group"}]
    destroy_expectations = [call(commands['destroy'], GroupId='test-group')]
    instance = _AWS().ec2.SecurityGroups


'''
class TestIpPermissionsCollection(_TestEC2Collection, unittest.TestCase):
    """Not full implemented yet."""
    class_name = "IpPermissions"
    commands = {'get': '',
                'create': '',
                'destroy': ''}
    get_expectations = [{}]
    create_args = [{}]
    create_expectations = [{}]
    destroy_args = [{}]
    destroy_expectations = [{}]
    instance = _AWS().ec2.IpPermissions
'''


class TestVolumeCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "Volumes"
    commands = {'get': 'DescribeVolumes',
                'create': 'CreateVolume',
                'destroy': 'DeleteVolume'}
    get_expectations = [
        call(commands['get'], VolumeIds=None, response_data_key='Volumes')
    ]
    create_args = [{'az': "us-east-1", 'size_or_snap': 8}]
    create_expectations = [call(commands['create'], encrypted=True,
                                AvailabilityZone='us-east-1', Size=8)]
    destroy_args = [{'volume_id': GENERIC_VOL}]
    destroy_expectations = [call(commands['destroy'],
                                 response_data_key='return',
                                 VolumeId='vol-123')]
    instance = _AWS().ec2.Volumes


class TestSnapshotCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "Snapshots"
    commands = {'get': "DescribeSnapshots",
                'create': "CreateSnapshot",
                'destroy': "DeleteSnapshot"}
    get_expectations = [call(commands['get'],
                             response_data_key='Snapshots')]
    create_args = [{'volume_id': GENERIC_VOL}]
    create_expectations = [call(commands['create'],
                                Description=None, VolumeId='vol-123')]
    destroy_args = [{'snapshot_id': "snap-123"}]
    destroy_expectations = [call(commands['destroy'], SnapshotId='snap-123')]
    instance = _AWS().ec2.Snapshots


class TestSubnetCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "Subnets"
    commands = {'get': "DescribeSubnets",
                'create': "CreateSubnet",
                'destroy': "DeleteSubnet"}
    get_expectations = [call('DescribeSubnets', response_data_key='Subnets')]
    create_args = [{'vpc_id': "vpc-test", 'cidr': "cidr-test",
                    'availability_zone': "us-east-4b"}]
    create_expectations = [call(commands['create'], VpcId='vpc-test',
                                CidrBlock='cidr-test',
                                response_data_key='Subnet')]
    destroy_args = [{'subnet_id': GENERIC_SUBNET}]
    destroy_expectations = [call(commands['destroy'], SubnetId='subnet-test',
                                 response_data_key='return')]
    instance = _AWS().ec2.Subnets


class TestVPCCollection(_TestEC2Collection, unittest.TestCase):
    """Not implemented."""

    class_name = "VPCs"
    commands = {'get': "DescribeVpcs",
                'create': "",
                'destroy': ""}
    get_expectations = [call(commands['get'], response_data_key='Vpcs')]
    create_args = [{'cidr': ""}]
    create_expectations = [{}]
    destroy_args = [{'vpc': ""}]
    destroy_expectations = [{}]
    instance = _AWS().ec2.VPCs


class TestTagCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "Tags"
    commands = {'get': 'DescribeTags',
                'create': 'CreateTags',
                'destroy': 'DeleteTags'}
    get_expectations = [call(commands['get'], response_data_key='Tags')]
    create_args = [{'resource_ids': ["res-test"], 'tags': ["tag-test"]}]
    create_expectations = [call(commands['create'], resources=["res-test"],
                                tags=["tag-test"])]
    destroy_args = [{'resource_ids': ["res-test"], 'tags': ["tag-test"]}]
    destroy_expectations = [call(commands['destroy'], resources=["res-test"],
                                 tags=["tag-test"])]
    instance = _AWS().ec2.Tags


class TestImageCollection(_TestEC2Collection, unittest.TestCase):
    class_name = "Images"
    commands = {'get': 'DescribeImages',
                'create': 'CreateImage',
                'destroy': 'DeregisterImage'}
    get_expectations = [call(commands['get'], response_data_key='Images')]
    create_args = [{
        'instance_id': GENERIC_INSTANCE,
        'name': GENERIC_INSTANCE,
        'no_reboot':  True,
        'description': GENERIC_AMI_DESCRIPTION
    }]
    create_expectations = [call(
        commands['create'],
        response_data_key='ImageId',
        Name=GENERIC_INSTANCE,
        Description=GENERIC_AMI_DESCRIPTION,
        InstanceId=GENERIC_INSTANCE,
        NoReboot=True
    )]
    destroy_args = [{'image_id': GENERIC_AMI}]
    destroy_expectations = [call(commands['destroy'],
                                 ImageId=GENERIC_AMI)]
    instance = _AWS().ec2.Images
