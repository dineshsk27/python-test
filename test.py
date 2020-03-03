import boto3
ec2 = boto3.resource('ec2', aws_access_key_id='AKIA5EJSZTE265SB3LN6',
                     aws_secret_access_key='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',
                     region_name='ap-southeast-2')

vpc = ec2.create_vpc(CidrBlock='192.168.0.0/16')
vpc.create_tags(Tags=[{"Key": "Name", "Value": "test_vpc"}])
vpc.wait_until_available()
print(vpc.id)

ec2Client = boto3.client('ec2')
ec2Client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsSupport = { 'Value': True } )
ec2Client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsHostnames = { 'Value': True } )


ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
print(ig.id)

route_table = vpc.create_route_table()
route = route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=ig.id
)
print(route_table.id)

subnet = ec2.create_subnet(CidrBlock='192.168.1.0/24', VpcId=vpc.id)
print(subnet.id)

route_table.associate_with_subnet(SubnetId=subnet.id)

sec_group = ec2.create_security_group(
    GroupName='slice_0', Description='slice_0 sec group', VpcId=vpc.id)
sec_group.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=22,
    ToPort=22
)

print(sec_group.id)
instances = ec2.create_instances(
    ImageId='ami-0f767afb799f45102', InstanceType='t2.micro', MaxCount=1, MinCount=1,
    NetworkInterfaces=[{'SubnetId': subnet.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_group.group_id]}])


outfile = open('ec2-keypair.pem','w')

# call the boto ec2 function to create a key pair
key_pair = ec2.create_key_pair(KeyName='ec2-keypair')

# capture the key and store it in a file
KeyPairOut = str(key_pair.key_material)
print(KeyPairOut)
outfile.write(KeyPairOut)

