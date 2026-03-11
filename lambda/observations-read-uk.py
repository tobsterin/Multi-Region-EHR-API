import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('observations-uk')

def lambda_handler(event, context):
    observation_id = event['pathParameters']['observation_id']
    response = table.get_item(Key={
        "PK": f"PATIENT#{event['pathParameters']['patient_id']}",
        "SK": f"OBSERVATION#{observation_id}"
    })
    item = response.get('Item')
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Observation not found"})}
    return {"statusCode": 200, "body": json.dumps(item)}