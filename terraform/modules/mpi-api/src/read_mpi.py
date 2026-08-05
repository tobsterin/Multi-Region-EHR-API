import json
import os
import boto3
import hashlib
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])
salt_param_name = os.environ['SALT_PARAM_NAME']
SALT = boto3.client('ssm').get_parameter(Name=salt_param_name, WithDecryption=True)['Parameter']['Value']

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
    
    national_id = (event.get('queryStringParameters') or {}).get('national_id')
    if not national_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing national_id parameter"})}
    
    hashed = hashlib.sha256((national_id+SALT).encode()).hexdigest()
    response = table.query(
        IndexName='national_id_hash_index',
        KeyConditionExpression= Key('national_id_hash').eq(hashed)
    )
    items = response.get('Items', [])
    if not items:
        return {"statusCode": 404, "body": json.dumps({"error": "Patient not found"})}
    matches = [{"region": i["region"], "patient_uuid": i["patient_uuid"]} for i in items]
    return {"statusCode": 200, "body": json.dumps(matches)}