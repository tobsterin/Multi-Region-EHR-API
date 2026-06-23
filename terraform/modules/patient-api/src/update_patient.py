import json
import boto3
import os
from botocore.exceptions import ClientError


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    patient_id = event.get('pathParameters', {}).get('patient_id')
    if 'body' in event:
        event = json.loads(event['body'])
    print("Received event:", json.dumps(event))
    
    resource_type = event.get("resourceType")

    if resource_type == "Patient":
            try:
                response = table.update_item(
                    Key={"patient_id": patient_id},
                    UpdateExpression="SET address = :addr, generalPractitioner = :gp",
                    ExpressionAttributeValues={
                        ":addr": event.get("address"),
                        ":gp": event.get("generalPractitioner")
                    },
                    ConditionExpression="attribute_exists(patient_id)"
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    return {
                        "statusCode": 404,
                        "body": json.dumps({"error": "Patient not found"})
                    }
                else:
                    print("Error updating patient:", e)
                    return {
                        "statusCode": 500,
                        "body": json.dumps({"error": "Failed to update patient"})
                    }
                
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"})
        }

    print("DynamoDB response:", json.dumps(response))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} updated", "id": patient_id})
    }