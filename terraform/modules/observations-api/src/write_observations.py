import json
import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    # check cognito group
    auth = event.get("requestContext", {}).get("authorizer", {})
    claims = auth.get("jwt", {}).get("claims") or auth.get("claims", {})
    raw_groups = claims.get("cognito:groups", "")
    if isinstance(raw_groups, str):
        cognito_groups = raw_groups.strip("[]").split()
    else:
        cognito_groups = raw_groups
    if "clinicians" not in cognito_groups:
        return {
            "statusCode": 403,
            "body": json.dumps({"error": "User is not authorised to perform this action"})
        }
    

    if "body" in event:
        try:
            event = json.loads(event['body']or'{}')
        except json.JSONDecodeError:
            return {"statusCode": 400, "body": json.dumps({"error": "Request body is not valid JSON"})}
    
    resource_type = event.get("resourceType")
    print(f"Processing {resource_type}")

    if resource_type == "Observation":
        required = ["id", "status", "category", "code", "subject", "encounter", "effectiveDateTime", "component"]
        missing = [f for f in required if not event.get(f)]
        if missing:
            return {"statusCode": 400,
            "body": json.dumps({"error": f"Missing required fields: {', '.join(missing)}"})}
        
        item = {
            "PK": f"PATIENT#{event['subject']['reference'].split('/')[1]}",
            "SK": f"OBSERVATION#{event['effectiveDateTime']}#{event['id']}",
            "resourceType": "Observation",
            "status": event["status"],
            "category": event["category"][0]["coding"][0]["display"],
            "code": event["code"]["coding"][0]["display"],
            "encounter": event["encounter"]["reference"],
            "effectiveDateTime": event["effectiveDateTime"],
            "components": json.loads(json.dumps(event["component"]), parse_float=Decimal)
        }
        
        # To prevent accidental overwrite
        try:
            table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(SK)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "statusCode": 409,
                    "body": json.dumps({"error": "Observation already exists"})
                }
            else:
                raise
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"})
        }

    print(f"New observation saved: {event['id']}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} saved", "id": event["id"]})
    }