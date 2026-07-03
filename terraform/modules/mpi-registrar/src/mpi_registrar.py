import json
import boto3
import os
import hashlib
from boto3.dynamodb.conditions import Key
import uuid
from boto3.dynamodb.types import TypeDeserializer

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
deserializer = TypeDeserializer()
SALT = os.environ['SALT']


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    for record in event['Records']:
        if record['eventName'] != 'INSERT':
            continue
        new_image = record['dynamodb']['NewImage']
        print("New patient:", json.dumps(new_image))

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
                break
            
        if not patient_uuid:
            patient_uuid = str(uuid.uuid4())
            
        hashed = hashlib.sha256((national_id + SALT).encode()).hexdigest()

        table.put_item(
            Item={
                "patient_uuid": patient_uuid,
                "region": os.environ['REGION'],
                "national_id_hash": hashed
            }
        )