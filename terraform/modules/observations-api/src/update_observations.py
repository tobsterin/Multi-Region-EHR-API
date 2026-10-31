import json
import os

import boto3
from botocore.exceptions import ClientError
from ehr_helpers import fhir_id, get_field, parse_groups, sort_key, supplied

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
    # also holds encounters, so the SK must be an observation's.
    patient_id = fhir_id(event.get("patient_id"))
    sk = sort_key(event.get("SK"), "OBSERVATION")
    resource_type = event.get("resourceType")
    print(f"Processing {resource_type} update")

    if not patient_id or not sk:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing or invalid patient_id or SK"}),
        }

    if resource_type == "Observation":
        # Only status can change. Anything else is refused, so a change the client
        # asked for is never ignored.
        not_updatable = sorted(
            set(event) - {"resourceType", "patient_id", "SK", "status"}
        )
        if not_updatable:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": f"Fields cannot be updated: {', '.join(not_updatable)}"}
                ),
            }
        if not supplied(event, "status"):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No valid fields to update"}),
            }
        status = get_field(event, "status")
        if not status:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing or invalid fields: status"}),
            }
        try:
            table.update_item(
                Key={"PK": f"PATIENT#{patient_id}", "SK": sk},
                ExpressionAttributeNames={"#s": "status"},
                UpdateExpression="SET #s = :stat",
                ExpressionAttributeValues={":stat": status},
                ConditionExpression="attribute_exists(SK)",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Observation not found"}),
                }
            else:
                print("Error updating observation:", e)
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Failed to update observation"}),
                }

    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"}),
        }

    print(f"Observation updated: {patient_id}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} updated", "id": sk}),
    }
