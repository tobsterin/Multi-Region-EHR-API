import json
import os

import boto3
from botocore.exceptions import ClientError
from ehr_helpers import coding, fhir_id, get_field, parse_groups, sort_key, supplied

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
    if not isinstance(event, dict):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Request body must be a JSON object"}),
        }

    # The record to change, keyed as the write handler stored it. The clinical table
    # also holds observations, so the SK must be an encounter's.
    patient_id = fhir_id(event.get("patient_id"))
    sk = sort_key(event.get("SK"), "ENCOUNTER")
    resource_type = event.get("resourceType")
    print(f"Processing {resource_type} update")

    if not patient_id or not sk:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing or invalid patient_id or SK"}),
        }

    if resource_type == "Encounter":
        # Everything this handler can change, in the form the write handler stores it;
        # None if malformed. Each is sent under its top-level name, e.g. "period".
        fields = {
            "status": get_field(event, "status"),
            "period.end": get_field(event, "period", "end"),
            "serviceProvider": get_field(event, "serviceProvider", "display"),
            "class": coding(event.get("class")),
            "type": get_field(event, "type", 0, "text"),
            "generalPractitioner": get_field(
                event, "generalPractitioner", 0, "display"
            ),
        }
        allowed = {"resourceType", "patient_id", "SK"} | {
            k.split(".")[0] for k in fields
        }
        # Anything else is refused, so a change the client asked for is never ignored
        not_updatable = sorted(set(event) - allowed)
        if not_updatable:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": f"Fields cannot be updated: {', '.join(not_updatable)}"}
                ),
            }
        updates = {k: v for k, v in fields.items() if supplied(event, k.split(".")[0])}
        invalid = [k for k, v in updates.items() if v is None]
        if invalid:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": f"Missing or invalid fields: {', '.join(invalid)}"}
                ),
            }
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
                Key={"PK": f"PATIENT#{patient_id}", "SK": sk},
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
        "body": json.dumps({"message": f"{resource_type} updated", "id": sk}),
    }
