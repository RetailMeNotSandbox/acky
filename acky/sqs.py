from acky.api import (
    AwsCollection,
    AwsApiClient,
)
from hashlib import md5


class QueueNotFound(Exception):
    pass


class SQSApiClient(AwsApiClient):
    service_name = "sqs"


class SQS(SQSApiClient):
    @property
    def Queues(self):
        return QueuesCollection(self._aws)

    @property
    def Messages(self):
        return MessagesCollection(self._aws)


class QueuesCollection(AwsCollection, SQSApiClient):
    def get(self, queue_name=None, prefix_match=False):
        # returns [QueueUrl, ...]
        # ListQueues, GetQueueUrl (no native filter)
        params = {}
        if queue_name:
            if prefix_match:
                params["queue_name_prefix"] = queue_name
            else:
                # if it's already a URL, just send it back as-is
                if "://" in queue_name:
                    return [queue_name]
                params["queue_name"] = queue_name
                return [self.call("GetQueueUrl", response_data_key="QueueUrl",
                        **params)]
        return self.call("ListQueues", response_data_key="QueueUrls", **params)

    def get_attributes(self, queue_url):
        return self.call("GetQueueAttributes",
                         response_data_key="Attributes",
                         queue_url=queue_url,
                         attribute_names=['All'])

    def create(self, name, attributes=None):
        # returns QueueUrl
        # CreateQueue
        params = {'queue_name': name}
        if attributes:
            params['attributes'] = attributes
        return self.call("CreateQueue", response_data_key="QueueUrl", **params)

    def destroy(self, queue):
        # returns bool
        # DeleteDBSnapshot
        queue_url = self.get(queue)[0]
        self.call("DeleteQueue", queue_url=queue_url)
        return True


class MessagesCollection(AwsCollection, SQSApiClient):
    def get(self, queue, max_messages=10, wait_time_seconds=0, filters=None,
            attributes=None):
        # returns [{<Message>}, ...]
        # ReceiveMessage (no native filter)
        if filters:
            raise Warning("Filters are ignored for this call")
        if '://' not in queue:
            queue_urls = self._aws.sqs.Queues.get(queue)
            if not queue_urls:
                raise QueueNotFound(queue)
            queue = queue_urls[0]
        if not attributes:
            attributes = ['All']
        params = {
            "queue_url": queue,
            "max_number_of_messages": max_messages,
            "wait_time_seconds": wait_time_seconds,
            "attribute_names": attributes,
        }
        return self.call("ReceiveMessage", response_data_key="Messages",
                         **params)

    def create(self, queue, message_body, verify=False):
        # returns message_id
        # SendMessage
        if '://' not in queue:
            queue_urls = self._aws.sqs.Queues.get(queue)
            if not queue_urls:
                raise QueueNotFound(queue)
            queue = queue_urls[0]
        params = {
            'queue_url': queue,
            'message_body': message_body,
        }
        result = self.call("SendMessage", **params)
        if verify:
            assert md5(message_body).hexdigest() == result['MD5OfMessageBody']
        return result['MessageId']

    def destroy(self, queue, receipt_handle):
        # returns bool
        # DeleteMessage
        if '://' not in queue:
            queue_urls = self._aws.sqs.Queues.get(queue)
            if not queue_urls:
                raise QueueNotFound(queue)
            queue = queue_urls[0]
        self.call("DeleteMessage", queue_url=queue,
                  receipt_handle=receipt_handle)
        return True
