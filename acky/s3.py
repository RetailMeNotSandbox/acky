from acky.api import AwsApiClient
try:
    from urllib import parse
except ImportError:
    import urlparse as parse


class InvalidURL(Exception):
    def __init__(self, url, msg=None):
        self.url = url
        if not msg:
            msg = "Invalid URL: {0}".format(url)
        super(InvalidURL, self).__init__(msg)


def _parse_url(url=None):
    """Split the path up into useful parts: bucket, obj_key"""
    if url is None:
        return ('', '')

    scheme, netloc, path, _, _ = parse.urlsplit(url)

    if scheme != 's3':
        raise InvalidURL(url, "URL scheme must be s3://")

    if path and not netloc:
        raise InvalidURL(url)

    return netloc, path[1:]


class S3(AwsApiClient):
    """Interface for managing S3 buckets. (API Version 2006-03-01)"""
    service_name = "s3"

    def get(self, url=None, delimiter="/"):
        """Path is an s3 url. Ommiting the path or providing "s3://" as the
        path will return a list of all buckets. Otherwise, all subdirectories
        and their contents will be shown.
        """
        params = {'Delimiter': delimiter}
        bucket, obj_key = _parse_url(url)

        if bucket:
            params['Bucket'] = bucket
        else:
            return self.call("ListBuckets", response_data_key="Buckets")

        if obj_key:
            params['Prefix'] = obj_key

        objects = self.call("ListObjects", response_data_key="Contents",
                            **params)
        for obj in objects:
            obj['url'] = "s3://{0}/{1}".format(bucket, obj['Key'])

        return objects

    def create(self, url):
        """Create a bucket, directory, or empty file."""
        bucket, obj_key = _parse_url(url)

        if not bucket:
            raise InvalidURL(url,
                             "You must specify a bucket and (optional) path")

        if obj_key:
            target = "/".join((bucket, obj_key))
        else:
            target = bucket

        return self.call("CreateBucket", bucket=target)

    def destroy(self, url, recursive=False):
        """Destroy a bucket, directory, or file. Specifying recursive=True
        recursively deletes all subdirectories and files."""
        bucket, obj_key = _parse_url(url)

        if not bucket:
            raise InvalidURL(url,
                             "You must specify a bucket and (optional) path")

        if obj_key:
            target = "/".join((bucket, obj_key))
        else:
            target = bucket

        if recursive:
            for obj in self.get(url, delimiter=''):
                self.destroy(obj['url'])

        return self.call("DeleteBucket", bucket=target)

    def upload(self, local_path, remote_url):
        """Copy a local file to an S3 location."""
        bucket, key = _parse_url(remote_url)

        with open(local_path, 'rb') as fp:
            return self.call("PutObject", bucket=bucket, key=key, body=fp)

    def download(self, remote_url, local_path, buffer_size=8 * 1024):
        """Copy S3 data to a local file."""
        bucket, key = _parse_url(remote_url)

        response_file = self.call("GetObject", bucket=bucket, key=key)['Body']
        with open(local_path, 'wb') as fp:
            buf = response_file.read(buffer_size)
            while buf:
                fp.write(buf)
                buf = response_file.read(buffer_size)

    def copy(self, src_url, dst_url):
        """Copy an S3 object to another S3 location."""
        src_bucket, src_key = _parse_url(src_url)
        dst_bucket, dst_key = _parse_url(dst_url)

        if not dst_bucket:
            dst_bucket = src_bucket
        params = {
            'copy_source': '/'.join((src_bucket, src_key)),
            'bucket': dst_bucket,
            'key': dst_key,
        }
        return self.call("CopyObject", **params)

    def move(self, src_url, dst_url):
        """Copy a single S3 object to another S3 location, then delete the
        original object."""
        self.copy(src_url, dst_url)
        self.destroy(src_url)
