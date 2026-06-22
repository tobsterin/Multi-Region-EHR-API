import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    patient_id = event.get('pathParameters', {}).get('patient_id')
    response = table.get_item(Key={
        "patient_id": patient_id
    })
    item = response.get('Item')
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Patient not found"})}
    return {"statusCode": 200, "body": json.dumps(item)}