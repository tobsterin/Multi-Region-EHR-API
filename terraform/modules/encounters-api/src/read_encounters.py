import json
import os

import boto3
from boto3.dynamodb.conditions import Key
from ehr_helpers import parse_groups

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    # check cognito group
    cognito_groups = parse_groups(event)
    if "clinicians" not in cognito_groups:
        return {
            "statusCode": 403,
            "body": json.dumps({"error": "User is not authorised to perform this action"})
        }
    
    patient_id = (event.get("pathParameters") or {}).get("patient_id")
    if not patient_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing patient_id"})}
    response = table.query(
        KeyConditionExpression=Key("PK").eq(f"PATIENT#{patient_id}") & Key("SK").begins_with("ENCOUNTER#")
    )
    items = response.get("Items", [])
    if not items:
        return {"statusCode": 404, "body": json.dumps({"error": "No encounters found"})}
    return {"statusCode": 200, "body": json.dumps(items)}