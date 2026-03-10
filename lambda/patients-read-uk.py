import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('patients-uk')

def lambda_handler(event, context):
    patient_id = event['pathParameters']['id']
    response = table.get_item(Key={
        "PK": f"PATIENT#{patient_id}",
        "SK": "METADATA"
    })
    item = response.get('Item')
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Patient not found"})}
    return {"statusCode": 200, "body": json.dumps(item)}