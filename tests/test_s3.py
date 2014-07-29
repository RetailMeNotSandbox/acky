import unittest
import os
from pprint import pprint
import acky.aws
from acky.s3 import _parse_url, InvalidURL
import random

AWS = acky.aws.AWS('us-east-1', 'sbx')
TEST_BUCKET = "ackytest1"
TEST_PREFIX = "ackytest_"
BAD_URLS = ("", "s3:/", "s3:///", "s3:////file", "s3:////path/",
            "bucket/file", "bucket/dir/",
            "bucket/", "bucket")


def functional_tests_enabled():
    """Only do functional tests if the 'FUNCTIONAL' environment variable is
    set to 'yes'.
    """
    return os.environ.get('FUNCTIONAL', False) == 'yes'


def _get_values(arr, key='Key'):
    return [e.get(key, None) for e in arr]


class TestS3Functional(unittest.TestCase):
    """Functional tests for all S3 methods. Testing get() requires the
    TEST_BUCKET to be properly set up.
    TODO: automate setting up TEST_BUCKET.
    """

    def test_parse_url(self):
        test_urls = ["s3://",
                     "s3://bucket",
                     "s3://bucket/",
                     "s3://bucket/key",
                     "s3://bucket/dir/",
                     "s3://bucket/dir/key"]
        desired_parts = [('', ''),
                         ('bucket', ''),
                         ('bucket', ''),
                         ('bucket', 'key'),
                         ('bucket', 'dir/'),
                         ('bucket', 'dir/key')]
        for url, parts in zip(test_urls, desired_parts):
            assert _parse_url(url) == parts, "URL:  {0} improperly parsed."
        # Invalid URLS
        for bad_url in BAD_URLS:
            try:
                AWS.s3.get(bad_url)
                assert False, ("Invalid URL: '{0}' "
                               "did not trigger exception.".format(bad_url))
            except InvalidURL:
                pass

    @unittest.expectedFailure
    @unittest.skipUnless(functional_tests_enabled(),
                         "Functional tests not enabled.")
    def test_get(self):
        # Fetching lists of buckets
        buckets = [AWS.s3.get(), AWS.s3.get("s3://")]
        assert buckets[0] == buckets[1],\
            "Inconsistent operation for s3.get() when fetching buckets."
        pprint("Existing bucket names: {0}".format(_get_values(buckets[0],
                                                               'Name')))

        # Fetching buckets contents
        bucket_contents = [AWS.s3.get("s3://{0}".format(TEST_BUCKET)),
                           AWS.s3.get("s3://{0}/".format(TEST_BUCKET))]
        assert buckets[0] == buckets[1],\
            "Inconsistent operation for s3.get "\
            "when fetching buckets contents."
        pprint("Bucket keys: {0}".format(_get_values(bucket_contents[0])))

        # Fetching individual objects
        bucket_file = AWS.s3.get("s3://{0}/file".format(TEST_BUCKET))
        assert bucket_file['Key'] == 'file',\
            "Incorrect operation for s3.get "\
            "when fetching file."

        # Fetching directory trees
        bucket_contents = [AWS.s3.get("s3://{0}/dir".format(TEST_BUCKET)),
                           AWS.s3.get("s3://{0}/dir/".format(TEST_BUCKET))]
        assert bucket_contents[0] == bucket_contents[1],\
            "Inconsistent operation for s3.get "\
            "when fetching directory contents."
        # assert _get_values(buckets[0]) == [test_values, ...],\
        #     "Incorrect objects fetched by s3.get "\
        #     "when fetching directory trees."

    @unittest.skipUnless(functional_tests_enabled(),
                         "Functional tests not enabled.")
    def test_create_destroy(self):
        # Test s3.create()
        AWS.s3.create("s3://{0}create_test".format(TEST_PREFIX))
        AWS.s3.create("s3://{0}create_test/create_test".format(TEST_PREFIX))
        AWS.s3.create("s3://{0}create_test/"
                      "create_test/test".format(TEST_PREFIX))
        buckets = AWS.s3.get()
        assert "{0}create_test".format(TEST_PREFIX) in\
            _get_values(buckets, 'Name'), "Could not create bucket."
        assert AWS.s3.get("s3://{0}create_test/"
                          "create_test".format(TEST_PREFIX)) and\
            AWS.s3.get("s3://{0}create_test/"
                       "create_test/test".format(TEST_PREFIX)),\
            "Could not create objects in {0}create_test".format(TEST_PREFIX)

        # Test s3.destroy()
        # File deletion
        AWS.s3.destroy("s3://{0}create_test/create_test".format(TEST_PREFIX),
                       recursive=False)
        bucket_objects = AWS.s3.get("s3://{0}create_test".format(TEST_PREFIX))
        assert 'create_test' not in _get_values(bucket_objects),\
               "Inaccurate destroy() method."

        # Recursive directory deletion
        AWS.s3.destroy("s3://{0}create_test/create_test/".format(TEST_PREFIX),
                       recursive=True)
        bucket_objects = AWS.s3.get("s3://{0}create_test/"
                                    "create_test/".format(TEST_PREFIX))
        assert 'create_test/test' not in _get_values(bucket_objects),\
               "Inaccurate deletion in destroy() with recursive=True."

        # Recursive bucket deletion
        AWS.s3.destroy("s3://{0}create_test".format(TEST_PREFIX),
                       recursive=True)
        buckets = AWS.s3.get()
        assert not "{0}create_test".format(TEST_PREFIX) in _get_values(buckets,
                                                                       'Name')

    @unittest.skipUnless(functional_tests_enabled(),
                         "Functional tests not enabled.")
    def test_upload_download(self):
        test_value = str(random.randint(100000000, 999999999))
        with open("/tmp/acky_test", 'w') as temp_file:
            temp_file.write(test_value)
        AWS.s3.create("s3://{0}upload_test".format(TEST_PREFIX))
        AWS.s3.upload("/tmp/acky_test",
                      "s3://{0}upload_test/upload".format(TEST_PREFIX))
        bucket_objects = AWS.s3.get("s3://{0}upload_test".format(TEST_PREFIX))
        assert len(bucket_objects) == 1, "Testing bucket unclean."
        assert 9 == bucket_objects[0]['Size'],\
            "Data upload error: size does not match."
        AWS.s3.download("s3://{0}upload_test/upload".format(TEST_PREFIX),
                        "/tmp/acky_test_dl")

        with open("/tmp/acky_test_dl", 'r') as temp_file:
            assert temp_file.read() == test_value,\
                "Download error: incorrect data."

if __name__ == "__main__":
    unittest.main()
