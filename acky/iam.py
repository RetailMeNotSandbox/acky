from acky.api import (
    AwsCollection,
    AwsApiClient,
)


class IAMApiClient(AwsApiClient):
    service_name = "iam"


class IAM(IAMApiClient):
    @property
    def Users(self):
        return UserCollection(self._aws)

    @property
    def Groups(self):
        return GroupCollection(self._aws)

    @property
    def Keys(self):
        return KeysCollection(self._aws)


class UserCollection(AwsCollection, IAMApiClient):
    def get(self, filters=None):
        # returns (user, ...)
        # ListUsers, GetUser
        raise NotImplementedError()

    def get_current(self):
        # returns user
        # GetUser
        return self.call("GetUser", response_data_key="User")

    def create(self):
        # returns user
        # CreateUser
        raise NotImplementedError()

    def destroy(self, user):
        # returns bool
        # DeleteUser
        raise NotImplementedError()


class GroupCollection(AwsCollection, IAMApiClient):
    def get(self, filters=None):
        # returns (grp, ...)
        # ListGroups, GetGroup
        raise NotImplementedError()

    def add_user(self):
        # returns bool
        # AddUserToGroup
        raise NotImplementedError()

    def remove_user(self):
        # returns bool
        # RemoveUserFromGroup
        raise NotImplementedError()


class KeysCollection(AwsCollection, IAMApiClient):
    def create(self, username=None):
        # returns (access_key, secret_key)
        # CreateAccessKey
        if not username:
            username = self._aws.username
        creds = self.call('CreateAccessKey', user_name=username,
                          response_data_key='AccessKey')
        return creds['AccessKeyId'], creds['SecretAccessKey']

    def destroy(self, access_key, username=None):
        # returns bool
        # DeleteAccessKey
        if not username:
            username = self._aws.username
        self.call('DeleteAccessKey', user_name=username,
                  access_key_id=access_key)
        return True
