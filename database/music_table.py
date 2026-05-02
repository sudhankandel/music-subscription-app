import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.client("dynamodb", region_name="us-east-1")

def create_music_table():
    try:
        response = dynamodb.create_table(
            TableName="music",
            AttributeDefinitions=[
                {"AttributeName": "artist", "AttributeType": "S"},
                {"AttributeName": "title", "AttributeType": "S"}
            ],
            KeySchema=[
                {"AttributeName": "artist", "KeyType": "HASH"},
                {"AttributeName": "title", "KeyType": "RANGE"}
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1
            }
        )

        print("Table creation initiated...")

        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName="music")

        print("Table 'music' is now ready to use!")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("Table 'music' already exists.")
        else:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_music_table()