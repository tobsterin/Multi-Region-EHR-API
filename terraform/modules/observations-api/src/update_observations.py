import json
import os

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
    
    body = json.loads(event.get("body") or "{}")

    patient_id = body.get("patient_id")
    resource_type = body.get("resourceType")
    print(f"Processing {resource_type} update")
   
    if not patient_id or not body.get("SK"):
        return {"statusCode": 400, "body": json.dumps({"error": "Missing patient_id or SK"})}

    if resource_type == "Observation":
        updates = {k: body.get(k) for k in ["status"] if body.get(k) is not None}
        if not updates:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No valid fields to update"})
            }
        try:
            table.update_item(
                Key={"PK": f"PATIENT#{patient_id}", "SK": body.get("SK")},
                ExpressionAttributeNames={"#s": "status"},
                UpdateExpression="SET #s = :stat",
                ExpressionAttributeValues={
                    ":stat": body.get("status")
                },
                ConditionExpression="attribute_exists(SK)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Observation not found"})
                }
            else:
                print("Error updating observation:", e)
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Failed to update observation"})
                }
                
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"})
        }

    print(f"Observation updated: {patient_id}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} updated", "id": body.get("SK")})
    }