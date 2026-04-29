import boto3

# 1. Setup the session (Learner Lab credentials)
dynamodb = boto3.client(
    'dynamodb',
    region_name='us-east-1'
)

def create_music_table():
    try:
        response = dynamodb.create_table(
            TableName='music',
            # Only define the keys here
            AttributeDefinitions=[
                {'AttributeName': 'artist', 'AttributeType': 'S'},
                {'AttributeName': 'title', 'AttributeType': 'S'}
            ],
            KeySchema=[
                {'AttributeName': 'artist', 'KeyType': 'HASH'},  # Partition Key
                {'AttributeName': 'title', 'KeyType': 'RANGE'}   # Sort Key
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        print("Table creation initiated...")
        
        # 2. Wait until the table exists
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName='music')
        print("Table 'music' is now ready to use!")
        
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_music_table()