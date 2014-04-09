from acky.api import AwsApiClient


class STSApiClient(AwsApiClient):
    service_name = "sts"


class STS(STSApiClient):
    def GetFederationToken(self, name, policy='', duration_seconds=3600):
        params = {
            "name": name,
            "duration_seconds": duration_seconds,
        }
        if policy:
            params['policy'] = policy
        return self.call("GetFederationToken", **params)

    def GetSessionToken(self, duration_seconds=3600):
        params = {
            "duration_seconds": duration_seconds,
        }
        return self.call("GetSessionToken", **params)
