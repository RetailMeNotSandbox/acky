from acky.api import (
    AwsCollection,
    AwsApiClient,
    make_filters,
)
from itertools import chain


class EC2ApiClient(AwsApiClient):
    service_name = "ec2"


class EC2(EC2ApiClient):

    def regions(self, continent='us', include_gov=False):
        # returns (string, ...)
        # DescribeRegions
        regions = self.call("DescribeRegions", response_data_key="Regions")
        if continent and continent != "all":
            regions = [r for r in regions
                       if r['RegionName'].startswith("{}-".format(continent))]
        return regions

    def zones(self, region):
        # returns (string, ...)
        # DescribeAvailabilityZones
        raise NotImplementedError("aws.ec2.zones")

    @property
    def environment(self):
        env = super(EC2, self).environment
        env['hoster'] = 'ec2'
        return env

    @property
    def ACLs(self):
        return ACLCollection(self._aws)

    @property
    def ACEs(self):
        return ACECollection(self._aws)

    @property
    def ElasticIPs(self):
        return ElasticIPCollection(self._aws)

    @property
    def Instances(self):
        return InstanceCollection(self._aws)

    @property
    def SecurityGroups(self):
        return SecurityGroupCollection(self._aws)

    @property
    def IpPermissions(self):
        return IpPermissionsCollection(self._aws)

    @property
    def Volumes(self):
        return VolumeCollection(self._aws)

    @property
    def Snapshots(self):
        return SnapshotCollection(self._aws)

    @property
    def Subnets(self):
        return SubnetCollection(self._aws)

    @property
    def VPCs(self):
        return VPCCollection(self._aws)

    @property
    def PlacementGroups(self):
        return PlacementGroupCollection(self._aws)

    @property
    def KeyPairs(self):
        return KeyPairCollection(self._aws)

    @property
    def Tags(self):
        return TagCollection(self._aws)

    @property
    def Images(self):
        return ImageCollection(self._aws)


class ACLCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (acl_info, ...)
        # DescribeNetworkAcls
        raise NotImplementedError()

    def create(self, vpc):
        # returns acl_info
        # CreateNetworkAcl
        raise NotImplementedError()

    def destroy(self, acl):
        # returns bool
        # DeleteNetworkAcl
        raise NotImplementedError()


class ACECollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (ace_info, ...)
        # DescribeNetworkAcls
        raise NotImplementedError()

    def add(self, acl, ace_list):
        # returns ace_info
        # CreateNetworkAclEntry
        raise NotImplementedError()

    def remove(self, acl, ace_list):
        # returns bool
        # DeleteNetworkAclEntry
        raise NotImplementedError()

    def replace(self, acl, old, new):
        # returns ace_info
        # CreateNetworkAclEntry, DeleteNetworkAclEntry
        raise NotImplementedError()


class ElasticIPCollection(AwsCollection, EC2ApiClient):
    """Interface to get, create, destroy, associate, and disassociate EIPs for
    classic EC2 domains and VPCs. (Amazon EC2 API Version 2014-06-15)
    """
    def get(self, filters=None):
        """List EIPs and associated information."""
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        return self.call("DescribeAddresses",
                         response_data_key="Addresses",
                         **params)

    def create(self, vpc=False):
        """Set vpc=True to allocate an EIP for a EC2-Classic instance.
        Set vpc=False to allocate an EIP for a VPC instance.
        """
        return self.call("AllocateAddress",
                         Domain="vpc" if vpc else "standard")

    def destroy(self, eip_or_aid, disassociate=False):
        """Release an EIP. If the EIP was allocated for a VPC instance, an
        AllocationId(aid) must be provided instead of a PublicIp. Setting
        disassociate to True will attempt to disassociate the IP before
        releasing it (required for associated nondefault VPC instances).
        """
        if "." in eip_or_aid:               # If an IP is given (Classic)
            # NOTE: EIPs are automatically disassociated for Classic instances.
            return "true" == self.call("ReleaseAddress",
                                       response_data_key="return",
                                       PublicIp=eip_or_aid)
        else:                               # If an AID is given (VPC)
            if disassociate:
                self.disassociate(eip_or_aid)
            return "true" == self.call("ReleaseAddress",
                                       response_data_key="return",
                                       AllocationId=eip_or_aid)

    def associate(self, eip_or_aid,
                  instance_id='', network_interface_id='', private_ip=''):
        """Associate an EIP with a given instance or network interface. If
        the EIP was allocated for a VPC instance, an AllocationId(aid) must
        be provided instead of a PublicIp.
        """
        if "." in eip_or_aid:               # If an IP is given (Classic)
            return self.call("AssociateAddress",
                             PublicIp=eip_or_aid,
                             InstanceId=instance_id,
                             NetworkInterfaceId=network_interface_id,
                             PrivateIpAddress=private_ip)
        else:                               # If an AID is given (VPC)
            return self.call("AssociateAddress",
                             AllocationId=eip_or_aid,
                             InstanceId=instance_id,
                             NetworkInterfaceId=network_interface_id,
                             PrivateIpAddress=private_ip)

    def disassociate(self, eip_or_aid):
        """Disassociates an EIP. If the EIP was allocated for a VPC instance,
        an AllocationId(aid) must be provided instead of a PublicIp.
        """
        if "." in eip_or_aid:               # If an IP is given (Classic)
            return "true" == self.call("DisassociateAddress",
                                       response_data_key="return",
                                       PublicIp=eip_or_aid)
        else:                               # If an AID is given (VPC)
            return "true" == self.call("DisassociateAddress",
                                       response_data_key="return",
                                       AllocationId=eip_or_aid)


class InstanceCollection(AwsCollection, EC2ApiClient):

    def get(self, instance_ids=None, filters=None):
        """List instance info."""
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        if instance_ids:
            params['InstanceIds'] = instance_ids
        reservations = self.call("DescribeInstances",
                                 response_data_key="Reservations",
                                 **params)
        return list(chain(*(r["Instances"] for r in reservations)))

    def create(self, ami, count, config=None):
        """Create an instance using the launcher."""
        return self.Launcher(config=config).launch(ami, count)

    def destroy(self, instance_id):
        """Terminate a single given instance."""
        return self.control(instance_id, "terminate")

    def control(self, instances, action):
        """Valid actions: start, stop, reboot, terminate, protect, and
        unprotect.
        """
        if not isinstance(instances, list) and\
           not isinstance(instances, tuple):
            instances = [instances]
        actions = {'start': {'operation': "StartInstances",
                             'response_data_key': "StartingInstances",
                             'InstanceIds': instances},
                   'stop': {'operation': "StopInstances",
                            'response_data_key': "StoppingInstances",
                            'InstanceIds': instances},
                   'reboot': {'operation': "RebootInstances",
                              'response_data_key': "return",
                              'InstanceIds': instances},
                   'terminate': {'operation': "TerminateInstances",
                                 'response_data_key': "TerminatingInstances",
                                 'InstanceIds': instances},
                   'protect': {'operation': "ModifyInstanceAttribute",
                               'response_data_key': "return",
                               'Attribute': 'disableApiTermination',
                               'Value': 'true'},
                   'unprotect': {'operation': "ModifyInstanceAttribute",
                                 'response_data_key': "return",
                                 'Attribute': 'disableApiTermination',
                                 'Value': 'false'}}
        if (action in ('protect', 'unprotect')):
            for instance in instances:
                self.call(InstanceId=instance, **actions[action])
        else:
            return self.call(**actions[action])

    def Launcher(self, config=None):
        """Provides a configurable launcher for EC2 instances."""
        class _launcher(EC2ApiClient):
            """Configurable launcher for EC2 instances. Create the Launcher
            (passing an optional dict of its attributes), set its attributes
            (as described in the RunInstances API docs), then launch().
            """
            def __init__(self, aws, config):
                super(_launcher, self).__init__(aws)
                self.config = config
                self._attr = list(self.__dict__.keys()) + ['_attr']

            def launch(self, ami, min_count, max_count=0):
                """Use given AMI to launch min_count instances with the
                current configuration. Returns instance info list.
                """
                params = config.copy()
                params.update(dict([i for i in self.__dict__.items()
                                    if i[0] not in self._attr]))
                return self.call("RunInstances",
                                 ImageId=ami,
                                 MinCount=min_count,
                                 MaxCount=max_count or min_count,
                                 response_data_key="Instances",
                                 **params)

        if not config:
            config = {}
        return _launcher(self._aws, config)

    def status(self, all_instances=None, instance_ids=None, filters=None):
        """List instance info."""
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        if instance_ids:
            params['InstanceIds'] = instance_ids
        if all_instances is not None:
            params['IncludeAllInstances'] = all_instances
        statuses = self.call("DescribeInstanceStatus",
                             response_data_key="InstanceStatuses",
                             **params)
        return statuses

    def events(self, all_instances=None, instance_ids=None, filters=None):
        """a list of tuples containing instance Id's and event information"""
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        if instance_ids:
            params['InstanceIds'] = instance_ids
        statuses = self.status(all_instances, **params)
        event_list = []
        for status in statuses:
            if status.get("Events"):
                for event in status.get("Events"):
                    event[u"InstanceId"] = status.get('InstanceId')
                    event_list.append(event)
        return event_list


class KeyPairCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        """List key info."""
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        return self.call("DescribeKeyPairs",
                         response_data_key="KeyPairs",
                         **params)

    def create(self, key_name):
        """Create a new key with a given name."""
        return self.call("CreateKeyPair", KeyName=key_name)

    def destroy(self, key_name):
        """Delete a key."""
        return self.call("DeleteKeyPair", KeyName=key_name)


class PlacementGroupCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (sg_info, ...)
        # DescribePlacementGroups
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        return self.call("DescribePlacementGroups",
                         response_data_key="PlacementGroups",
                         **params)

    def create(self, group_name, strategy="cluster"):
        # returns sg_info
        params = {
            "strategy": strategy
        }
        # CreatePlacementGroup
        if callable(group_name):
            params['group_name'] = group_name(self.environment)
        else:
            params['group_name'] = group_name
        return self.call("CreatePlacementGroup", **params)

    def destroy(self, pg):
        # returns bool
        # DeletePlacementGroup
        return self.call("DeletePlacementGroup", group_name=pg)


class SecurityGroupCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None, exclude_vpc=False):
        # returns (sg_info, ...)
        # DescribeSecurityGroups
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        groups = self.call("DescribeSecurityGroups",
                           response_data_key="SecurityGroups",
                           **params)
        if exclude_vpc:
            # Exclude any group that belongs to a VPC
            return [g for g in groups if not g.get('VpcId')]
        else:
            return groups

    def create(self, name, description, vpc=None):
        # returns sg_info
        params = {
            "Description": description,
        }
        # CreateSecurityGroup
        if callable(name):
            params['GroupName'] = name(self.environment)
        else:
            params['GroupName'] = name
        if vpc:
            params["VpcId"] = vpc
        return self.call("CreateSecurityGroup", **params)

    def destroy(self, sg):
        # returns bool
        # DeleteSecurityGroup
        return self.call("DeleteSecurityGroup", GroupId=sg)


class IpPermissionsCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (sgr_info, ...)
        # DescribeSecurityGroups
        raise NotImplementedError()

    def modify(self, api_action, sgid, other, proto_spec):
        """Make a change to a security group. api_action is an EC2 API name.
           Other is one of:
            - a group (sg-nnnnnnnn)
            - a group with account (<user id>/sg-nnnnnnnn)
            - a CIDR block (n.n.n.n/n)
           Proto spec is a triplet (<proto>, low_port, high_port)."""
        params = {'group_id': sgid, 'ip_permissions': []}
        perm = {}
        params['ip_permissions'].append(perm)

        proto, from_port, to_port = proto_spec
        perm['IpProtocol'] = proto
        perm['FromPort'] = from_port or 0
        perm['ToPort'] = to_port or from_port or 65535

        if other.startswith("sg-"):
            perm['UserIdGroupPairs'] = [{'GroupId': other}]
        elif "/sg-" in other:
            account, group_id = other.split("/", 1)
            perm['UserIdGroupPairs'] = [{
                'UserId': account,
                'GroupId': group_id,
            }]
        else:
            perm['IpRanges'] = [{'CidrIp': other}]

        return self.call(api_action, **params)

    def add(self, sgid, other, proto_spec, direction="in"):
        """Add a security group rule to group <sgid>.
           Direction is either 'in' (ingress) or 'out' (egress).
           See modify() for other parameters."""
        # returns bool
        # AuthorizeSecurityGroupIngress, AuthorizeSecurityGroupEgress
        if direction == "in":
            api = "AuthorizeSecurityGroupIngress"
        elif direction == "out":
            api = "AuthorizeSecurityGroupEgress"
        else:
            raise ValueError("direction must be one of ('in', 'out')")
        return self.modify(api, sgid, other, proto_spec)

    def remove(self, sgid, other, proto_spec, direction="in"):
        """Remove a security group rule from group <sgid>.
           Direction is either 'in' (ingress) or 'out' (egress).
           See modify() for other parameters."""
        # returns (removed_sgr_info, ...)
        # RevokeSecurityGroupIngress, RevokeSecurityGroupEgress
        if direction == "in":
            api = "RevokeSecurityGroupIngress"
        elif direction == "out":
            api = "RevokeSecurityGroupEgress"
        else:
            raise ValueError("direction must be one of ('in', 'out')")
        return self.modify(api, sgid, other, proto_spec)


class VolumeCollection(AwsCollection, EC2ApiClient):
    """Interface to get, create, destroy, and attach for EBS Volumes.
    (Amazon EC2 API Version 2014-06-15)
    """
    def get(self, volume_ids=None, filters=None):
        """List EBS Volume info."""
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        if isinstance(volume_ids, str):
            volume_ids = [volume_ids]
        return self.call("DescribeVolumes",
                         VolumeIds=volume_ids,
                         response_data_key="Volumes",
                         **params)

    def create(self, az, size_or_snap, volume_type=None, iops=None,
               encrypted=True):
        """Create an EBS Volume using an availability-zone and size_or_snap
        parameter, encrypted by default.
        If the volume is crated from a snapshot, (str)size_or_snap denotes
        the snapshot id. Otherwise, (int)size_or_snap denotes the amount of
        GiB's to allocate. iops must be set if the volume type is io1.
        """
        kwargs = {}
        kwargs['encrypted'] = encrypted
        if volume_type:
            kwargs['VolumeType'] = volume_type
        if iops:
            kwargs['Iops'] = iops
        is_snapshot_id = False
        try:
            size_or_snap = int(size_or_snap)
        except ValueError:
            is_snapshot_id = True
        if is_snapshot_id:
            return self.call("CreateVolume", AvailabilityZone=az,
                             SnapshotId=size_or_snap, **kwargs)
        return self.call("CreateVolume", AvailabilityZone=az,
                         Size=size_or_snap, **kwargs)

    def destroy(self, volume_id):
        """Delete a volume by volume-id and return success boolean."""
        return 'true' == self.call("DeleteVolume", VolumeId=volume_id,
                                   response_data_key="return")

    def attach(self, volume_id, instance_id, device_path):
        """Attach a volume to an instance, exposing it with a device name."""
        return self.call("AttachVolume",
                         VolumeId=volume_id, InstanceId=instance_id,
                         Device=device_path)

    def detach(self, volume_id, instance_id='', device_path='', force=False):
        """Detach a volume from an instance."""
        return self.call("DetachVolume",
                         VolumeId=volume_id, InstanceId=instance_id,
                         Device=device_path, force=force)


class SnapshotCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (snap_info, ...)
        # DescribeSnapshots
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        return self.call("DescribeSnapshots",
                         response_data_key="Snapshots",
                         **params)

    def create(self, volume_id, description=None):
        # returns snap_info
        # CreateSnapshot
        return self.call("CreateSnapshot",
                         VolumeId=volume_id,
                         Description=description)

    def destroy(self, snapshot_id):
        # returns bool
        # DeleteSnapshot
        return self.call("DeleteSnapshot", SnapshotId=snapshot_id)


class SubnetCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (subnet_info, ...)
        # DescribeSubnets
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        return self.call("DescribeSubnets",
                         response_data_key="Subnets",
                         **params)

    def create(self, vpc_id, cidr, availability_zone):
        # returns subnet_info
        # CreateSubnet
        return self.call("CreateSubnet",
                         VpcId=vpc_id,
                         CidrBlock=cidr,
                         response_data_key="Subnet")

    def destroy(self, subnet_id):
        # returns bool
        # DeleteSubnet
        if self.call("DeleteSubnet", SubnetId=subnet_id,
                     response_data_key="return"):
            return True
        return False


class VPCCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (vpc_info, ...)
        # DescribeVpcs
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        return self.call("DescribeVpcs", response_data_key="Vpcs", **params)

    def create(self, cidr, tenancy="default"):
        # returns vpc_info
        # CreateVpc
        raise NotImplementedError()

    def destroy(self, vpc):
        # returns bool
        # DeleteVpc
        raise NotImplementedError()


class TagCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (tag_info, ...)
        # DescribeTags
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        return self.call("DescribeTags",
                         response_data_key="Tags",
                         **params)

    def create(self, resource_ids, tags):
        # returns bool
        # CreateTags
        return self.call("CreateTags", resources=resource_ids, tags=tags)

    def destroy(self, resource_ids, tags):
        # returns bool
        # DeleteTags
        return self.call("DeleteTags", resources=resource_ids, tags=tags)


class ImageCollection(AwsCollection, EC2ApiClient):
    def get(self, image_ids=None, owners=None, executable_users=None, filters=None):
        # returns (image_info, ...)
        # DescribeImages
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        if image_ids:
            params["ImageIds"] = image_ids
        if owners:
            params["Owners"] = owners
        if executable_users:
            params["ExecutableUsers"] = executable_users
        return self.call("DescribeImages",
                         response_data_key="Images",
                         **params)

    def create(self, instance_id, name, no_reboot=True, description=None, block_device_mappings=None):
        # returns image_id
        # CreateImage
        params = {
            "InstanceId": instance_id,
            "Name": name,
            "NoReboot": no_reboot
        }
        if description:
            params["Description"] = description
        if block_device_mappings:
            params["BlockDeviceMappings"] = block_device_mappings
        return self.call("CreateImage",
                         response_data_key="ImageId",
                         **params)

    def destroy(self, image_id):
        # returns bool
        # CreateImage
        return self.call("DeregisterImage", ImageId=image_id)
