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
    def get(self, filters=None):
        # returns (eip_info, ...)
        # DescribeAddresses
        raise NotImplementedError()

    def create(self, vpc=False):
        # returns eip_info
        # AllocateAddresses
        raise NotImplementedError()

    def destroy(self, eip):
        # returns bool
        # ReleaseAddresses
        raise NotImplementedError()


class InstanceCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (inst_info, ...)
        # DescribeInstances
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        reservations = self.call("DescribeInstances",
                                 response_data_key="Reservations",
                                 **params)
        return list(chain(*(r["Instances"] for r in reservations)))

    def control(self, inst, state):
        # returns bool
        # valid states: start, stop, termate, protect, unprotect
        # StartInstances, StopInstances, TerminateInstances,
        #     ModifyInstanceAttribute(DisableApiTermination)
        raise NotImplementedError()

    def Launcher(self, config=None):
        class _launcher(object):
            # Configurable launcher for EC2 instances. Create the Launcher
            # (passing an optional dict of its attributes), set its attributes
            # (as described in the RunInstances API docs), then launch()
            def __init__(self, aws, config):
                self._aws = aws
                self.config = config

            def launch(self, count, ami, name):
                # returns inst_info
                # RunInstances
                raise NotImplementedError()

        if not config:
            config = {}
        return _launcher(self._aws, config)


class KeyPairCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (key_info, ...)
        # DescribeKeyPairs
        params = {}
        if filters:
            params["filters"] = make_filters(filters)
        return self.call("DescribeKeyPairs",
                         response_data_key="KeyPairs",
                         **params)

    def create(self, key_name):
        # returns (key_pair, ...)
        # CreateKeyPair
        raise NotImplementedError()

    def destroy(self, key_name):
        # returns bool
        # DeleteKeyPair
        raise NotImplementedError()


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
    def get(self, filters=None):
        # returns (vol_info, ...)
        # DescribeVolumes
        # key: Volumes
        raise NotImplementedError()

    def create(self, az, size_or_snap, iops=None):
        # returns vol_info
        # CreateVolume
        raise NotImplementedError()

    def destroy(self, vol):
        # returns bool
        # DeleteVolume
        raise NotImplementedError()

    def attach(self, vol, inst, dev=None):
        # returns bool
        # AttachVolume
        raise NotImplementedError()


class SnapshotCollection(AwsCollection, EC2ApiClient):
    def get(self, filters=None):
        # returns (snap_info, ...)
        # DescribeSnapshots
        raise NotImplementedError()

    def create(self, vol, desc=None):
        # returns snap_info
        # CreateSnapshot
        raise NotImplementedError()

    def destroy(self, vol):
        # returns bool
        # DeleteSnapshot
        raise NotImplementedError()


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
