from acky.api import (
    AwsCollection,
    AwsApiClient,
)


class RDSApiClient(AwsApiClient):
    service_name = "rds"


class RDS(RDSApiClient):
    def engine_versions(engine='mysql', default_only=False):
        pass

    @property
    def Instances(self):
        return InstanceCollection(self._aws)

    @property
    def Snapshots(self):
        return SnapshotCollection(self._aws)

    @property
    def EventSubscriptions(self):
        return EventSubscriptionCollection(self._aws)

    @property
    def SecurityGroups(self):
        return SecurityGroupCollection(self._aws)

    @property
    def SecurityGroupRules(self):
        return SecurityGroupRuleCollection(self._aws)


class InstanceCollection(AwsCollection, RDSApiClient):
    def get(self, filters=None):
        # returns (inst, ...)
        # DescribeDBInstances (no native filter)
        raise NotImplementedError()

    def Launcher(self, config=None):
        class _launcher(object):
            def __init__(self, aws, config):
                # Configurable launcher for RDS instances. Create the Launcher
                # (passing an optional dict of its attributes), set its
                # attributes (as described in the CreateDBnstance API docs),
                # then launch()
                self._aws = aws
                self.config = config

            def launch(self, inst_id, password):
                # returns inst_info
                # CreateDBInstance
                raise NotImplementedError()

        if not config:
            config = {}
        return _launcher(self._aws, config)

    def Replicator(self, config=None):
        class _replicator(object):
            def __init__(self, aws, config):
                # Configurable launcher for RDS Read Replicas. Create the
                # Replicator (passing an optional dict of its attributes), set
                # its attributes (as described in the
                # CreateDBInstanceReadReplica API docs), then replicate()
                self._aws = aws
                self.config = config

            def replicate(self, src, dest):
                # returns replica_info
                # CreateDBInstanceReadReplica
                raise NotImplementedError()

        if not config:
            config = {}
        return _replicator(self._aws, config)

    def destroy(self, inst, final_snap=None):
        # returns bool
        # DeleteDBInstance
        raise NotImplementedError()

    def promote(self, replica, retention, window):
        # returns bool
        # PromoteReadReplica
        raise NotImplementedError()

    def reboot(self, inst):
        # returns bool
        # RebootDBInstance
        raise NotImplementedError()


class SnapshotCollection(AwsCollection, RDSApiClient):
    def get(self, filters=None):
        # returns (snap, ...)
        # DescribeDBSnapshots (no native filter)
        raise NotImplementedError()

    def create(self, inst, snap_id):
        # returns snap
        # CreateDBSnapshot
        raise NotImplementedError()

    def copy(self, orig, new):
        # returns snap
        # CopyDBSnapshot
        raise NotImplementedError()

    def destroy(self, snap):
        # returns bool
        # DeleteDBSnapshot
        raise NotImplementedError()


class EventSubscriptionCollection(AwsCollection, RDSApiClient):
    def get(self, filters=None):
        # returns (sub, ...)
        # DescribeEventSubscriptions (no native filter)
        raise NotImplementedError()

    def create(self, name, topic):
        # returns sub
        # CreateEventSubscription
        raise NotImplementedError()

    def destroy(self, sub):
        # returns bool
        # DeleteEventSubscription
        raise NotImplementedError()

    def categories(self, sourcetype=None):
        # returns (cat, ...)
        # DescribeEventCategories
        raise NotImplementedError()


class SecurityGroupCollection(AwsCollection, RDSApiClient):
    def get(self, filters=None):
        # returns (sg_info, ...)
        # DescribeDBSecurityGroups
        raise NotImplementedError()

    def create(self, name, description):
        # returns sg_info
        # CreateDBSecurityGroup
        raise NotImplementedError()

    def destroy(self, sg):
        # returns bool
        # DeleteDBSecurityGroup
        raise NotImplementedError()


class SecurityGroupRuleCollection(AwsCollection, RDSApiClient):
    def get(self, filters=None):
        # returns (sgr_info, ...)
        # DescribeDBSecurityGroups
        raise NotImplementedError()

    def add(self, sg, rules):
        # returns (added_sgr_info, ...)
        # AuthorizeDBSecurityGroupIngress
        raise NotImplementedError()

    def remove(self, sg, rules):
        # returns (removed_sgr_info, ...)
        # RevokeDBSecurityGroupIngress
        raise NotImplementedError()

    def replace(self, sg, rules):
        # returns (removed, added)
        # AuthorizeDBSecurityGroupIngress
        # RevokeDBSecurityGroupIngress
        raise NotImplementedError()
