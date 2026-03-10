import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('patients-uk')

def lambda_handler(event, context):
    # To handle both direct test events and API Gateway requests
    if 'body' in event:
        event = json.loads(event['body'])
    print("Received event:", json.dumps(event))
    
    resource_type = event.get("resourceType")

    if resource_type == "Encounter":
        item = {
            "PK": f"PATIENT#{event['subject']['reference'].split('/')[1]}",
            "SK": f"ENCOUNTER#{event['id']}",
            "resourceType": "Encounter",
            "status": event["status"],
            "type": event["type"][0]["text"],
            "start": event["period"]["start"],
            "end": event["period"]["end"],
            "serviceProvider": event["serviceProvider"]["display"]
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