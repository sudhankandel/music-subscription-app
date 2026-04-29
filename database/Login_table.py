import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.create_table(
    TableName='login',
    KeySchema=[
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'  
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)

print("Table creating...")
table.wait_until_exists()
print("Table created successfully!")