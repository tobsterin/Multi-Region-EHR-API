import json
import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
from ehr_helpers import fhir_id, get_field, parse_groups, reference_id

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

    resource_type = event.get("resourceType")
    print(f"Processing {resource_type}")

    if resource_type == "Observation":
        # Each required field in the one form we accept; None if missing or in any other form
        fields = {
            "id": fhir_id(event.get("id")),
            "status": get_field(event, "status"),
            "category[0].coding[0].display": get_field(
                event, "category", 0, "coding", 0, "display"
            ),
            "code.coding[0].display": get_field(event, "code", "coding", 0, "display"),
            "subject.reference": reference_id(event.get("subject"), "Patient"),
            "encounter.reference": reference_id(event.get("encounter"), "Encounter"),
            "effectiveDateTime": get_field(event, "effectiveDateTime"),
            "component": get_field(event, "component", kind=list),
        }
        invalid = [name for name, value in fields.items() if value is None]
        if invalid:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": f"Missing or invalid fields: {', '.join(invalid)}"}
                ),
            }

        item = {
            "PK": f"PATIENT#{fields['subject.reference']}",
            "SK": f"OBSERVATION#{fields['effectiveDateTime']}#{fields['id']}",
            "resourceType": "Observation",
            "status": fields["status"],
            "category": fields["category[0].coding[0].display"],
            "code": fields["code.coding[0].display"],
            "encounter": f"Encounter/{fields['encounter.reference']}",
            "effectiveDateTime": fields["effectiveDateTime"],
            "components": json.loads(
                json.dumps(fields["component"]), parse_float=Decimal
            ),
        }

        # To prevent accidental overwrite
        try:
            table.put_item(Item=item, ConditionExpression="attribute_not_exists(SK)")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "statusCode": 409,
                    "body": json.dumps({"error": "Observation already exists"}),
                }
            else:
                raise
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"}),
        }

    print(f"New observation saved: {event['id']}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} saved", "id": event["id"]}),
    }
