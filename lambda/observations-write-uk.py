import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('observations-uk')

def lambda_handler(event, context):
    # To handle both direct test events and API Gateway requests
    if 'body' in event:
        event = json.loads(event['body'])
    print("Received event:", json.dumps(event))
    
    resource_type = event.get("resourceType")

    if resource_type == "Observation":
        item = {
            "PK": f"PATIENT#{event['subject']['reference'].split('/')[1]}",
            "SK": f"OBSERVATION#{event['id']}",
            "resourceType": "Observation",
            "status": event["status"],
            "category": event["category"][0]["coding"][0]["display"],
            "code": event["code"]["coding"][0]["display"],
            "encounter": event["encounter"]["reference"],
            "effectiveDateTime": event["effectiveDateTime"],
            "components": json.dumps(event["component"])
        }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unsupported resourceType: {resource_type}"})
        }

    response = table.put_item(Item=item)
    print("DynamoDB response:", json.dumps(response))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"{resource_type} saved", "id": event["id"]})
    }