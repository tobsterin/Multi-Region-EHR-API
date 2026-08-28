import json
import os

import boto3
from botocore.exceptions import ClientError
from ehr_helpers import parse_groups

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    # check cognito group
    cognito_groups = parse_groups(event)
    if "clinicians" not in cognito_groups:
        return {
            "statusCode": 403,
            "body": json.dumps(
                {"error": "User is not authorised to perform this action"}
            ),
        }

    if "body" in event:
        try:
            event = json.loads(event["body"] or "{}")
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Request body is not valid JSON"}),
            }

    patient_id = event.get("patient_id")
    resource_type = event.get("resourceType")
    print(f"Processing {resource_type} update")

    if not patient_id or not event.get("SK"):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing patient_id or SK"}),
        }

    if resource_type == "Encounter":
        fields = {
            "status": event.get("status"),
            "period.end": event.get("period", {}).get("end"),
            "serviceProvider": event.get("serviceProvider"),
            "class": event.get("class"),
            "type": event.get("type"),
            "generalPractitioner": event.get("generalPractitioner"),
        }
        updates = {k: v for k, v in fields.items() if v is not None}
        if not updates:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No valid fields to update"}),
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
                names[f"#f{i}"] = k
                values[f":v{i}"] = v
                parts.append(f"#f{i} = :v{i}")

        try:
            table.update_item(
                Key={"PK": f"PATIENT#{patient_id}", "SK": event.get("SK")},
                UpdateExpression="SET " + ", ".join(parts),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
                ConditionExpression="attribute_exists(SK)",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Encounter not found"}),
                }
            else:
                print("Error updating encounter:", e)
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Failed to update encounter"}),
                }

    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"}),
        }

    print(f"Encounter updated: {patient_id}")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": f"{resource_type} updated", "id": event.get("SK")}
        ),
    }
