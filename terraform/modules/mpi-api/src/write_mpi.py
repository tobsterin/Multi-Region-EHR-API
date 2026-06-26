import json
import boto3
import os
from botocore.exceptions import ClientError
import hashlib
from boto3.dynamodb.conditions import Key
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    if 'body' in event:
        event = json.loads(event['body'])
    national_id = event.get ("national_id")
    region = event.get ("region")
    salt = os.environ ["SALT"]
    hashed = hashlib.sha256 ( (national_id+ salt).encode() ).hexdigest()
    response = table.query(
        IndexName='national_id_hash_index',
        KeyConditionExpression= Key('national_id_hash').eq(hashed)
    )

    items = response.get('Items', [])
    if items:
        patient_uuid = items[0]['patient_uuid']
    else:
        patient_uuid = str(uuid.uuid4())
    
    table.put_item(
        Item={
            "patient_uuid": patient_uuid,
            "region": region,
            "national_id_hash": hashed
        }
    )
    return {"statusCode": 200, "body": json.dumps({"patient_uuid": patient_uuid, "region": region})}