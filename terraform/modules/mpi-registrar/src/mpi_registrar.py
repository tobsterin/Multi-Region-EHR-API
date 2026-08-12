import hashlib
import os
import uuid
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
deserializer = TypeDeserializer()
region = os.environ['REGION']
salt_param_name = os.environ['SALT_PARAM_NAME']
SALT = boto3.client('ssm').get_parameter(Name=salt_param_name, WithDecryption=True)['Parameter']['Value']


def lambda_handler(event, context):
    print(f"Processing {len(event.get('Records', []))} records")

    for record in event['Records']:
        if record['eventName'] != 'INSERT':
            continue
        new_image = record['dynamodb']['NewImage']
        print(f"Processing new patient in {region}")

        national_id = deserializer.deserialize(new_image["nationalId"])
        foreign_ids = deserializer.deserialize(new_image["knownForeignIds"])
        patient_uuid = None

        for foreign_id in foreign_ids:
            foreign_ni = foreign_id["national_id"]
            hashed_foreign = hashlib.sha256((foreign_ni + SALT).encode()).hexdigest()
            response = table.query(
                IndexName='national_id_hash_index',
                KeyConditionExpression=Key('national_id_hash').eq(hashed_foreign)
            )
            if response['Items']:
                patient_uuid = response['Items'][0]['patient_uuid']
                print(f"Found existing patient UUID {patient_uuid}")
                break
            
        if not patient_uuid:
            patient_uuid = str(uuid.uuid4())
            print(f"Generated new patient UUID {patient_uuid}")
            
        hashed = hashlib.sha256((national_id + SALT).encode()).hexdigest()

        table.put_item(
            Item={
                "patient_uuid": patient_uuid,
                "region": region,
                "national_id_hash": hashed
            }
        )