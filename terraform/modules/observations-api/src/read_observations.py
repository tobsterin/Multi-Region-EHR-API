import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from ehr_helpers import parse_groups

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)

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
        KeyConditionExpression=Key("PK").eq(f"PATIENT#{patient_id}") & Key("SK").begins_with("OBSERVATION#")
    )
    items = response.get("Items", [])
    if not items:
        return {"statusCode": 404, "body": json.dumps({"error": "No observations found"})}
    return {"statusCode": 200, "body": json.dumps(items, cls=DecimalEncoder)}