import os
import boto3

bucket = "mdml-experiments"

# Credentials come from env vars loaded in .bashrc
access_key = os.environ['STORAGE_GRID_ACCESS_KEY']
secret_key = os.environ['STORAGE_GRID_SECRET_KEY']

# Create boto3 client
s3 = boto3.client('s3', 
    region_name='us-east-1',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url='https://s3.it.anl.gov:18082')

# Gather objects from the 'mdml-experiments' bucket
objects = s3.list_objects(Bucket=bucket)

# Print them out
for obj in objects['Contents']:
    print(obj['Key'])

resp = input("\nEnter the name of an experiment file to delete it:")
if resp != '':
    print(f"Attempting to delete {resp}...")
    delete_resp = s3.delete_object(
        Bucket="mdml-experiments",
        Key=resp)
    if delete_resp is None:
        print(f"Deleted file: {resp}")
else:
    print(resp)

