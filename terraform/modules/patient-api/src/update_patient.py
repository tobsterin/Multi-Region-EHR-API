import json
import os

import boto3
from botocore.exceptions import ClientError
from ehr_helpers import fhir_id, get_field, parse_groups, supplied

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

    patient_id = fhir_id((event.get("pathParameters") or {}).get("patient_id"))
    if not patient_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing or invalid patient_id"}),
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

    resource_type = event.get("resourceType")
    print(f"Processing {resource_type} update")

    if resource_type == "Patient":
        # Everything this handler can change, in the form the write handler stores it;
        # None if malformed. The national IDs can't change: the MPI registrar only
        # reads them when a patient is first registered.
        fields = {
            "address": get_field(event, "address", kind=list),
            "generalPractitioner": get_field(
                event, "generalPractitioner", 0, "display"
            ),
        }
        # Anything else is refused, so a change the client asked for is never ignored
        not_updatable = sorted(set(event) - {"resourceType"} - set(fields))
        if not_updatable:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": f"Fields cannot be updated: {', '.join(not_updatable)}"}
                ),
            }
        updates = {k: v for k, v in fields.items() if supplied(event, k)}
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
            names[f"#f{i}"] = k
            values[f":v{i}"] = v
            parts.append(f"#f{i} = :v{i}")

        try:
            table.update_item(
                Key={"patient_id": patient_id},
                UpdateExpression="SET " + ", ".join(parts),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
                ConditionExpression="attribute_exists(patient_id)",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Patient not found"}),
                }
            print("Error updating patient:", e)
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to update patient"}),
            }

    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"}),
        }

    print(f"Patient updated: {patient_id}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} updated", "id": patient_id}),
    }
