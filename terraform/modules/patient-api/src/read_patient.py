import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

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
    
    patient_id = event.get('pathParameters', {}).get('patient_id')
    response = table.get_item(Key={
        "patient_id": patient_id
    })
    item = response.get('Item')
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Patient not found"})}
    return {"statusCode": 200, "body": json.dumps(item)}