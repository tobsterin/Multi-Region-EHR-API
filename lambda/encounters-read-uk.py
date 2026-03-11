import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('encounters-uk')

def lambda_handler(event, context):
    encounter_id = event['pathParameters']['encounter_id']
    response = table.get_item(Key={
        "PK": f"PATIENT#{event['pathParameters']['patient_id']}",
        "SK": f"ENCOUNTER#{encounter_id}"
    })
    item = response.get('Item')
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Encounter not found"})}
    return {"statusCode": 200, "body": json.dumps(item)}