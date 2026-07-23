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

    if resource_type == "Encounter":
        item = {
            "PK": f"PATIENT#{event['subject']['reference'].split('/')[1]}",
            "SK": f"ENCOUNTER#{event['period']['start']}#{event['id']}",
            "resourceType": "Encounter",
            "status": event["status"],
            "period": {
                "start": event["period"]["start"],
                "end": event["period"]["end"]
            },
            "serviceProvider": event["serviceProvider"]["display"],
            "class": {
                "system": event.get("class", {}).get("system"),
                "code": event.get("class", {}).get("code"),
                "display": event.get("class", {}).get("display")},
            "type": event["type"][0]["text"],
            "generalPractitioner": event.get("generalPractitioner")
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
                    "body": json.dumps({"error": "Encounter already exists"})
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