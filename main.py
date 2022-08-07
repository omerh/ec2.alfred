import json

import boto3
import sys

query = (sys.argv[1:])
if len(query) > 0:
    args = str.split(query[0], " ")

    if len(args) >= 1:
        region = args[0].strip()
        region = region.replace("\\", "", -1)
else:
    # Default to eu-west-1
    region = "eu-west-1"


def list_all_running_instances(region_name='eu-west-1'):
    client = boto3.client('ec2', region_name=region_name)
    all_instances = []

    ec2_response = client.describe_instances(
        Filters=[{
            'Name': 'instance-state-name',
            'Values': ['running']
        }],
        MaxResults=99999
    )
    all_instances.append(ec2_response["Reservations"])

    while 'NextToken' in ec2_response:
        ec2_response = client.describe_instances(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }],
            NextToken=ec2_response['NextToken']
        )
        all_instances.append(ec2_response["Reservations"])

    return all_instances


if __name__ == "__main__":
    instances = list_all_running_instances(region)
    alfred_result = []
    for instance in instances[0]:
        i = instance['Instances'][0]
        name = '-'
        for tag in i['Tags']:
            if tag['Key'] == 'Name':
                name = tag['Value']

        result = {
            "title": i['InstanceId'],
            "subtitle": f"{name} | {i['PrivateIpAddress']} | {i['InstanceType']} | {i['Architecture']} ",
            "arg": i['InstanceId'],
            "icon": {
                "path": "ec2.png"
            }
        }
        alfred_result.append(result)

    response = json.dumps({
        "items": alfred_result
    })

    sys.stdout.write(response)
