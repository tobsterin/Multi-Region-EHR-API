import os
import uuid

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError
from ehr_helpers import salted_hash

dynamodb = boto3.resource("dynamodb")
client = boto3.client("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
mapping_table_name = os.environ["MAPPING_TABLE_NAME"]
deserializer = TypeDeserializer()
serializer = TypeSerializer()
region = os.environ["REGION"]
salt_param_name = os.environ["SALT_PARAM_NAME"]
SALT = boto3.client("ssm").get_parameter(Name=salt_param_name, WithDecryption=True)[
    "Parameter"
]["Value"]


def lambda_handler(event, context):
    records = event.get("Records", [])
    print(f"Processing {len(records)} records")

    for record in records:
        if record["eventName"] != "INSERT":
            continue
        try:
            register(record["dynamodb"]["NewImage"])
        except Exception as e:  # noqa: BLE001 - any failure must be reported to Lambda
            # Lambda retries from this record, so the rest of the batch comes back with it
            print(f"Registration failed, retrying from this record: {e}")
            return {
                "batchItemFailures": [
                    {"itemIdentifier": record["dynamodb"]["SequenceNumber"]}
                ]
            }

    return {"batchItemFailures": []}


def register(new_image):
    print(f"Processing new patient in {region}")

    national_id = deserializer.deserialize(new_image["nationalId"])
    foreign_ids = deserializer.deserialize(new_image.get("knownForeignIds", {"L": []}))
    patient_id = deserializer.deserialize(new_image["patient_id"])
    hashed = salted_hash(national_id, SALT)

    # Own hash first, so a replayed record reuses the UUID it already wrote
    patient_uuid = find_uuid(hashed)
    if not patient_uuid:
        for foreign_id in foreign_ids:
            patient_uuid = find_uuid(salted_hash(foreign_id["national_id"], SALT))
            if patient_uuid:
                print("Found existing patient UUID")
                break

    if not patient_uuid:
        patient_uuid = str(uuid.uuid4())
        print("Generated new patient UUID")

    # Both rows are written together or not at all
    try:
        client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": table.name,
                        "Item": to_dynamodb(
                            {
                                "national_id_hash": hashed,
                                "patient_uuid": patient_uuid,
                                "region": region,
                            }
                        ),
                        # A new hash, or a replay that binds it to the same UUID
                        "ConditionExpression": "attribute_not_exists(national_id_hash) OR patient_uuid = :uuid",
                        "ExpressionAttributeValues": to_dynamodb(
                            {":uuid": patient_uuid}
                        ),
                    }
                },
                {
                    "Put": {
                        "TableName": mapping_table_name,
                        "Item": to_dynamodb(
                            {"patient_uuid": patient_uuid, "patient_id": patient_id}
                        ),
                        "ConditionExpression": "attribute_not_exists(patient_uuid) OR patient_id = :patient_id",
                        "ExpressionAttributeValues": to_dynamodb(
                            {":patient_id": patient_id}
                        ),
                    }
                },
            ]
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "TransactionCanceledException":
            raise
        # One Code per item, in order: [MPI, mapping]. "None" means that item was fine.
        reasons = [r["Code"] for r in e.response.get("CancellationReasons", [])]
        if "ConditionalCheckFailed" not in reasons:
            raise  # e.g. TransactionConflict is transient, so let the stream retry
        # A conflicting binding is a permanent refusal, not something to retry
        print(f"Registration refused, conflicting binding: {reasons}")
        return

    print("MPI and mapping table updated")


def find_uuid(hashed):
    # Consistent, so a retry sees what this region has already written
    response = table.get_item(Key={"national_id_hash": hashed}, ConsistentRead=True)
    item = response.get("Item")
    return item["patient_uuid"] if item else None


def to_dynamodb(values):
    # A plain client needs typed values, e.g. {"S": "..."}. Not dynamodb.meta.client:
    # the resource's client converts values itself, so these would be converted twice.
    return {k: serializer.serialize(v) for k, v in values.items()}
