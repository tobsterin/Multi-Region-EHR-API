import json
import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    # To handle both direct test events and API Gateway requests
    if 'body' in event:
        event = json.loads(event['body'])
    print("Received event:", json.dumps(event))
    
    resource_type = event.get("resourceType")

    if resource_type == "Patient":
        item = {
            "patient_id": event['id'],
            "resourceType": "Patient",
            "name": f'{event["name"][0]["family"]}, {" ".join(event["name"][0]["given"])}',
            "nationalId": event["identifier"][0]["value"],
            "gender": event["gender"],
            "birthDate": event["birthDate"],
            "address": f'{", ".join(event["address"][0]["line"])}, {event["address"][0]["city"]}, {event["address"][0]["postalCode"]}, {event["address"][0]["country"]}',
            "generalPractitioner": event["generalPractitioner"][0]["display"]
        }
        # To prevent accidental overwrite
        try:
            response = table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(patient_id)"
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return {
                    "statusCode": 409,
                    "body": json.dumps({"error": "Patient already exists"})
                }
            else:
                raise
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"})
        }

    print("DynamoDB response:", json.dumps(response))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} saved", "id": event["id"]})
    }