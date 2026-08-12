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


    if resource_type == "Encounter":
        fields = {
            "status": body.get("status"),
            "period.end": body.get("period", {}).get("end"),
            "serviceProvider": body.get("serviceProvider"),
            "class": body.get("class"),
            "type": body.get("type"),
            "generalPractitioner": body.get("generalPractitioner")
        }
        updates = {k: v for k, v in fields.items() if v is not None}
        if not updates:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No valid fields to update"})
            }
        names, values, parts = {}, {}, []
        for i, (k, v) in enumerate(updates.items()):
            if "." in k:
                # Handle nested fields
                parent, child = k.split(".", 1)
                names[f"#f{i}"] = parent
                names[f"#f{i}_child"] = child
                values[f":v{i}"] = v
                parts.append(f"#f{i}.#f{i}_child = :v{i}")
            else:
                names[f"#f{i}"]  = k
                values[f":v{i}"] = v
                parts.append(f"#f{i} = :v{i}")

        try:
            table.update_item(
                Key={"PK": f"PATIENT#{patient_id}", "SK": body.get("SK")},
                UpdateExpression="SET " + ", ".join(parts),
                ExpressionAttributeNames=names,                        
                ExpressionAttributeValues=values,
                ConditionExpression="attribute_exists(SK)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Encounter not found"})
                }
            else:
                print("Error updating encounter:", e)
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Failed to update encounter"})
                }
                
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"})
        }

    print(f"Encounter updated: {patient_id}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} updated", "id": body.get("SK")})
    }