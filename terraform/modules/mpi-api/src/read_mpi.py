import json
import os
import boto3
import hashlib
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    # check cognito group
    auth = event.get("requestContext", {}).get("authorizer", {})
    claims = auth.get("jwt", {}).get("claims") or auth.get("claims", {})
    cognito_groups = claims.get("cognito:groups", "")
    if "clinicians" not in cognito_groups:
        return {
            "statusCode": 403,
            "body": json.dumps({"error": "User is not authorized to perform this action"})
        }
    
    national_id = (event.get('queryStringParameters') or {}).get('national_id')
    if not national_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing national_id parameter"})}
    
    salt = os.environ['SALT']
    hashed = hashlib.sha256((national_id+salt).encode()).hexdigest()
    response = table.query(
        IndexName='national_id_hash_index',
        KeyConditionExpression= Key('national_id_hash').eq(hashed)
    )
    items = response.get('Items', [])
    if not items:
        return {"statusCode": 404, "body": json.dumps({"error": "Patient not found"})}
    return {"statusCode": 200, "body": json.dumps(items)}