import json
import os
import boto3
import hashlib
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    national_id = event.get('queryStringParameters', {}).get('national_id')
    salt = os.environ['SALT']
    hashed = hashlib.sha256((national_id+salt).encode()).hexdigest()
    response = table.query(
        IndexName='national_id_hash_index',
        KeyConditionExpression= Key('national_id_hash').eq(hashed)
    )
    items = response.get('Items', [])
    if not items:
        return {"statusCode": 404, "body": json.dumps({"error": "Patient not found"})}
    return {"statusCode": 200, "body": json.dumps(items)}