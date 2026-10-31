import json
import os

import boto3
from ehr_helpers import parse_groups, salted_hash

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
salt_param_name = os.environ["SALT_PARAM_NAME"]
SALT = boto3.client("ssm").get_parameter(Name=salt_param_name, WithDecryption=True)[
    "Parameter"
]["Value"]


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

    national_id = (event.get("queryStringParameters") or {}).get("national_id")
    if not national_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing national_id parameter"}),
        }

    hashed = salted_hash(national_id, SALT)
    item = table.get_item(Key={"national_id_hash": hashed}).get("Item")
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Patient not found"})}
    # A hash holds one identity; the list keeps the documented response shape
    matches = [{"region": item["region"], "patient_uuid": item["patient_uuid"]}]
    return {"statusCode": 200, "body": json.dumps(matches)}
