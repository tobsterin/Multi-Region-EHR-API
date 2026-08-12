import json
import os

import boto3
from botocore.exceptions import ClientError


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
    if 'body' in event:
        event = json.loads(event['body'])
    
    resource_type = event.get("resourceType")
    print(f"Processing {resource_type} update")

    if resource_type == "Patient":
        updates = {k: event.get(k) for k in ["address", "generalPractitioner"] if event.get(k) is not None}
        if not updates:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No valid fields to update"})
            }
        
        names, values, parts = {}, {}, []
        for i, (k, v) in enumerate(updates.items()):
            names[f"#f{i}"]  = k
            values[f":v{i}"] = v
            parts.append(f"#f{i} = :v{i}")

        try:
            table.update_item(
                Key={"patient_id": patient_id},
                UpdateExpression="SET " + ", ".join(parts),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
                ConditionExpression="attribute_exists(patient_id)"
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Patient not found"})
                }
            print("Error updating patient:", e)
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to update patient"})
            }
                
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"})
        }

    print(f"Patient updated: {patient_id}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} updated", "id": patient_id})
    }