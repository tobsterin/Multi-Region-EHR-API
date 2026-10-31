import json
import os

import boto3
from botocore.exceptions import ClientError
from ehr_helpers import (
    coding,
    fhir_id,
    get_field,
    parse_groups,
    reference_id,
    supplied,
)

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

    if resource_type == "Encounter":
        # Each required field in the one form we accept; None if missing or in any other form
        fields = {
            "id": fhir_id(event.get("id")),
            "subject.reference": reference_id(event.get("subject"), "Patient"),
            "status": get_field(event, "status"),
            "period.start": get_field(event, "period", "start"),
            "serviceProvider.display": get_field(event, "serviceProvider", "display"),
            "type[0].text": get_field(event, "type", 0, "text"),
        }
        invalid = [name for name, value in fields.items() if value is None]

        # Optional fields may be left out, but if sent must be in the one form we accept
        end = get_field(event, "period", "end")
        if supplied(event, "period", "end") and not end:
            invalid.append("period.end")
        encounter_class = coding(event.get("class"))
        if supplied(event, "class") and not encounter_class:
            invalid.append("class")
        practitioner = get_field(event, "generalPractitioner", 0, "display")
        if supplied(event, "generalPractitioner") and not practitioner:
            invalid.append("generalPractitioner[0].display")

        if invalid:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": f"Missing or invalid fields: {', '.join(invalid)}"}
                ),
            }

        item = {
            "PK": f"PATIENT#{fields['subject.reference']}",
            "SK": f"ENCOUNTER#{fields['period.start']}#{fields['id']}",
            "resourceType": "Encounter",
            "status": fields["status"],
            "period": {"start": fields["period.start"], "end": end},
            "serviceProvider": fields["serviceProvider.display"],
            "class": encounter_class or {"system": None, "code": None, "display": None},
            "type": fields["type[0].text"],
            "generalPractitioner": practitioner,
        }
        # To prevent accidental overwrite
        try:
            table.put_item(Item=item, ConditionExpression="attribute_not_exists(SK)")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "statusCode": 409,
                    "body": json.dumps({"error": "Encounter already exists"}),
                }
            else:
                raise
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"}),
        }

    print(f"New encounter saved: {event['id']}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} saved", "id": event["id"]}),
    }
