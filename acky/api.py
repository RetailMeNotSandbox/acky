import logging
from xml.dom.minidom import parseString


def make_filters(data, key_name='Name', values_name='Values'):
    data = data.copy()
    for key, value in data.items():
        if isinstance(value, str) or not hasattr(value, '__iter__'):
            data[key] = [value]
    return make_map(data, key_name, values_name)


def make_map(data, key_name='Name', value_name='Value'):
    value_map = []
    for key, value in data.items():
        if not isinstance(value, str) and not hasattr(value, '__iter__'):
            value = str(value)
        value_map.append({key_name: key, value_name: value})
    return value_map


class AWSErrorNotFound(Exception):
    pass


def extract_aws_error(xml_string):
    def _bomb(xml_string):
        e = AWSErrorNotFound("The string provided does not appear to be an "
                             "XML AWS error response")
        e.xml_string = xml_string
        raise e

    try:
        dom = parseString(xml_string)
    except TypeError:
        _bomb(xml_string)

    for tag in dom.getElementsByTagName('Error'):
        children = [n.tagName for n in tag.childNodes
                    if n.nodeType != n.TEXT_NODE]
        if 'Code' in children and 'Message' in children:
            code = tag.getElementsByTagName('Code')[0].firstChild.data
            message = tag.getElementsByTagName('Message')[0].firstChild.data
            return code, message

    _bomb(xml_string)


class AWSServiceUnavailable(Exception):
    pass


class AWSCallError(Exception):
    def __init__(self, response, operation):
        self.response = response
        self.operation = operation
        self.args = (response, operation)
        self.code, self.message = extract_aws_error(response.text)

    def __str__(self):
        return "{}: {}: {}".format(self.operation,
                                   self.code,
                                   self.message)


class AwsApiClient(object):
    service_name = None

    def __init__(self, aws):
        self._aws = aws
        self._service = aws.session.get_service(self.service_name)
        self._endpoint = self._service.get_endpoint(aws.region)

    def call(self, operation, response_data_key=None, *args, **kwargs):
        log = logging.getLogger(__name__)
        op = self._service.get_operation(operation)
        log.debug("Calling {} action '{}'".format(self._service, operation))
        resp, data = op.call(self._endpoint, *args, **kwargs)
        if not resp.ok:
            raise AWSCallError(resp, operation)
        if response_data_key:
            if response_data_key in data:
                return data[response_data_key]
            return None
        else:
            return data

    def regions(self, continent='us', include_gov=False):
        # returns (string, ...)
        regions = self._service.region_names
        if continent and continent != "all":
            regions = [r for r in regions
                       if r.startswith("{}-".format(continent))]
        if not include_gov:
            regions = [r for r in regions if "-gov-" not in r]
        return regions

    @property
    def environment(self):
        return self.aws.environment


class AwsCollection(object):
    """Abstract class for AWS object collections"""
    def get(self, filters=None):
        raise NotImplementedError()

    def create(self, *args, **kwargs):
        raise NotImplementedError()

    def destroy(self, obj_id):
        raise NotImplementedError()
