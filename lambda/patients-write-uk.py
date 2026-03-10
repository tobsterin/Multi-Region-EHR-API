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

    if resource_type == "Patient":
        item = {
            "PK": f"PATIENT#{event['id']}",
            "SK": "METADATA",
            "resourceType": "Patient",
            "name": f'{event["name"][0]["family"]}, {" ".join(event["name"][0]["given"])}',
            "nhsNumber": event["identifier"][0]["value"],
            "gender": event["gender"],
            "birthDate": event["birthDate"],
            "address": f'{", ".join(event["address"][0]["line"])}, {event["address"][0]["city"]}, {event["address"][0]["postalCode"]}, {event["address"][0]["country"]}',
            "generalPractitioner": event["generalPractitioner"][0]["display"]
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