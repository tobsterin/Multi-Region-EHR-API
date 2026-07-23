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
    
    body = json.loads(event.get("body") or "{}")
    print("Received event:", json.dumps(body))

    patient_id = body.get("patient_id")
    resource_type = body.get("resourceType")
   
    if not patient_id or not body.get("SK"):
        return {"statusCode": 400, "body": json.dumps({"error": "Missing patient_id or SK"})}

    if resource_type == "Observation":
            try:
                response = table.update_item(
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

    print("DynamoDB response:", json.dumps(response))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} updated", "id": body.get("SK")})
    }