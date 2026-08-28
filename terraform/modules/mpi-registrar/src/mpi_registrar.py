import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError
from ehr_helpers import salted_hash

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
mapping_table = dynamodb.Table(os.environ["MAPPING_TABLE_NAME"])
deserializer = TypeDeserializer()
region = os.environ["REGION"]
salt_param_name = os.environ["SALT_PARAM_NAME"]
SALT = boto3.client("ssm").get_parameter(Name=salt_param_name, WithDecryption=True)[
    "Parameter"
]["Value"]


def lambda_handler(event, context):
    print(f"Processing {len(event.get('Records', []))} records")

    for record in event["Records"]:
        if record["eventName"] != "INSERT":
            continue
        new_image = record["dynamodb"]["NewImage"]
        print(f"Processing new patient in {region}")

        national_id = deserializer.deserialize(new_image["nationalId"])
        foreign_ids = deserializer.deserialize(
            new_image.get("knownForeignIds", {"L": []})
        )
        patient_uuid = None

        # Check the national ID to find the existing patient UUID
        hashed = salted_hash(national_id, SALT)
        check = table.query(
            IndexName="national_id_hash_index",
            KeyConditionExpression=Key("national_id_hash").eq(hashed),
        )
        if check["Items"]:
            patient_uuid = check["Items"][0]["patient_uuid"]
        else:
            for foreign_id in foreign_ids:
                foreign_ni = foreign_id["national_id"]
                hashed_foreign = salted_hash(foreign_ni, SALT)
                response = table.query(
                    IndexName="national_id_hash_index",
                    KeyConditionExpression=Key("national_id_hash").eq(hashed_foreign),
                )
                if response["Items"]:
                    patient_uuid = response["Items"][0]["patient_uuid"]
                    print("Found existing patient UUID")
                    break

        if not patient_uuid:
            patient_uuid = str(uuid.uuid4())
            print("Generated new patient UUID")

        # To prevent accidental overwrite
        item = {
            "patient_uuid": patient_uuid,
            "region": region,
            "national_id_hash": hashed,
        }
        try:
            table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(patient_uuid) OR national_id_hash = :hashed",
                ExpressionAttributeValues={":hashed": hashed},
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print("Patient UUID already exists with a different national ID hash")
                continue
            raise

        # Write the patient UUID and patient id to the mapping table:
        patient_id = deserializer.deserialize(new_image["patient_id"])
        item = {"patient_uuid": patient_uuid, "patient_id": patient_id}
        try:
            mapping_table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(patient_uuid) OR patient_id = :patient_id",
                ExpressionAttributeValues={":patient_id": patient_id},
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print("Mapping table already has an entry for this patient UUID")
                continue
            raise

        print("Mapping table updated with patient_uuid and patient_id")
