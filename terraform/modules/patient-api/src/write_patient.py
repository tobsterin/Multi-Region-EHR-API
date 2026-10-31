import json
import os

import boto3
from botocore.exceptions import ClientError
from ehr_helpers import fhir_id, get_field, parse_groups

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

    if resource_type == "Patient":
        # Each required field in the one form we accept; None if missing or in any other form.
        # The MPI registrar reads nationalId and knownForeignIds from the stream, and a
        # record it can't read blocks the stream, so those two must be right before saving.
        fields = {
            "id": fhir_id(event.get("id")),
            "name": get_field(event, "name", kind=list),
            "identifier[0].value": get_field(event, "identifier", 0, "value"),
            "gender": get_field(event, "gender"),
            "birthDate": get_field(event, "birthDate"),
            "address": get_field(event, "address", kind=list),
            "generalPractitioner[0].display": get_field(
                event, "generalPractitioner", 0, "display"
            ),
            "knownForeignIds": foreign_ids(event.get("knownForeignIds")),
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
            "patient_id": fields["id"],
            "resourceType": "Patient",
            "name": fields["name"],
            "nationalId": fields["identifier[0].value"],
            "gender": fields["gender"],
            "birthDate": fields["birthDate"],
            "address": fields["address"],
            "generalPractitioner": fields["generalPractitioner[0].display"],
            "knownForeignIds": fields["knownForeignIds"],
        }
        # To prevent accidental overwrite
        try:
            table.put_item(
                Item=item, ConditionExpression="attribute_not_exists(patient_id)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "statusCode": 409,
                    "body": json.dumps({"error": "Patient already exists"}),
                }
            else:
                raise
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"}),
        }

    print(f"New patient saved: {event['id']}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} saved", "id": event["id"]}),
    }


def foreign_ids(value):
    # Optional, so missing means none. Otherwise a list of {"national_id": "..."},
    # stored with nothing else in it. None if any entry is in another form.
    if value is None:
        return []
    if not isinstance(value, list):
        return None
    national_ids = [get_field(entry, "national_id") for entry in value]
    if None in national_ids:
        return None
    return [{"national_id": national_id} for national_id in national_ids]
