"""Classes to represent an Amazon Web Services connection and its objects"""
from datetime import datetime
import acky.ec2
import acky.iam
import acky.rds
import acky.sts
import acky.sqs
import botocore.session

__version__ = '0.0.1'


class AWS(object):
    def __init__(self, region, profile=None):
        env_vars = {
            'region': ('region', 'BOTO_DEFAULT_REGION', region),
            'profile': (None, 'BOTO_DEFAULT_PROFILE', profile),
        }
        self.session = botocore.session.get_session(env_vars)
        self.region = region

    @property
    def userinfo(self):
        if not hasattr(self, '_user'):
            self._user = self.iam.Users.get_current()
        return self._user

    @property
    def username(self):
        return self.userinfo['UserName']

    @property
    def account_id(self):
        arn = self.userinfo['Arn']
        return arn.split(":")[4]

    @property
    def environment(self):
        return {
            'region': self.region,
            'username': self.username,
            'account': self.account_id,
            'date': datetime().utcnow().isoformat(),
        }

    @property
    def ec2(self):
        return acky.ec2.EC2(self)

    @property
    def iam(self):
        return acky.iam.IAM(self)

    @property
    def rds(self):
        return acky.rds.RDS(self)

    @property
    def sqs(self):
        return acky.sqs.SQS(self)

    @property
    def sts(self):
        return acky.sts.STS(self)
