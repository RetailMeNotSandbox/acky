%%%%%%%%%%%%
Acky Library
%%%%%%%%%%%%

The Acky library provides a consistent interface to AWS. Based on botocore, it
abstracts some of the API work involved and allows the user to interact with AWS
APIs in a consistent way with minimal overhead.

Acky takes a different approach to the API from libraries like the venerable
`Boto <https://github.com/boto/boto>`. Rather than model AWS objects as Python
objects, Acky simply wraps the API to provide a more consistent interface. Most
objects in AWS are represented as collections in Acky, with get(), create(),
and destroy() methods. The get() method always accepts a filter map, no matter
if the underlying API method does.

In cases where the API's multitude of parameters would make for awkward method
calls (as is the case with EC2's RunInstances), Acky provides a utility class
whose attributes can be set before executing the API call.


%%%%%%%%%%
Using Acky
%%%%%%%%%%

Acky uses a botocore-style AWS credential configuration, the same as the
official AWS CLI. Before you use Acky, you'll need to `set up your config
<http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html>`.

Once your credentials are set up, using acky is as simple as creating an
instance of the AWS object::

    from acky.aws import AWS
    aws = AWS(region, profile)
    instances = aws.ec2.Instances.get(filters={'tag:Name': 'web-*'})
    print('Found {} web servers'.format(len(instances))
    for instance in instances:
        print('  {}'.format(instance['PublicDNSAddress'])
    

%%%%%%%%%%%%%%%%
Module Structure
%%%%%%%%%%%%%%%%

The expected module structure for Acky follows. Many APIs are not yet
implemented, but those that are can be considered stable.

* AWS

  * username (property)
  * userinfo (property)
  * account_id (property)
  * environment (property)
  * ec2

    * regions
    * zones
    * ACEs
    * ACLs
    * ElasticIPs
    * Instances
    * IpPermissions
    * KeyPairs
    * PlacementGroups
    * SecurityGroups
    * Snapshots
    * Subnets
    * VPCs
    * Volumes

  * iam

    * Users
    * Groups
    * Keys

  * rds

    * engine_versions
    * Instances
    * Snapshots
    * EventSubscriptions
    * SecurityGroups
    * SecurityGroupRules

  * sqs

    * Queues
    * Messages

  * sts

    * GetFederationToken
    * GetSessionToken

Other services will be added in future versions.

%%%%%%%%%%%%%%%%%%
Installing acky
%%%%%%%%%%%%%%%%%%

acky is available in PyPI and is installable via pip::

    pip install acky

You may also install acky from source, perhaps from the GitHub repo::

    git clone https://github.com/RetailMeNot/acky.git
    cd acky
    python setup.py install
