from decimal import Decimal
import json
import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    # check cognito group
    auth = event.get("requestContext", {}).get("authorizer", {})
    claims = auth.get("jwt", {}).get("claims") or auth.get("claims", {})
    cognito_groups = claims.get("cognito:groups", "")
    if "clinicians" not in cognito_groups:
        return {
            "statusCode": 403,
            "body": json.dumps({"error": "User is not authorised to perform this action"})
        }
    
    if "body" in event:
        event = json.loads(event["body"])
    print("Received event:", json.dumps(event))
    
    resource_type = event.get("resourceType")

    if resource_type == "Observation":
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
            response = table.put_item(
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

    print("DynamoDB response:", json.dumps(response))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} saved", "id": event["id"]})
    }