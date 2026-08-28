import json
import os

import boto3
from boto3.dynamodb.conditions import Key
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
    response = table.query(
        IndexName="national_id_hash_index",
        KeyConditionExpression=Key("national_id_hash").eq(hashed),
    )
    items = response.get("Items", [])
    if not items:
        return {"statusCode": 404, "body": json.dumps({"error": "Patient not found"})}
    matches = [
        {"region": i["region"], "patient_uuid": i["patient_uuid"]} for i in items
    ]
    return {"statusCode": 200, "body": json.dumps(matches)}
