import boto3
import sys

def create_subscriptions_table():
    """Create DynamoDB table for storing user subscriptions"""
    
    # Create DynamoDB client
    dynamodb = boto3.client('dynamodb', region_name='ap-southeast-2')
    
    table_name = 'BirdTagSubscriptions'
    
    try:
        # Check if table already exists
        existing_tables = dynamodb.list_tables()['TableNames']
        if table_name in existing_tables:
            print(f"Table {table_name} already exists!")
            return
        
        # Create table
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # On-demand pricing
        )
        
        print(f"Creating table {table_name}...")
        
        # Wait for table to be created
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        print(f"Table {table_name} created successfully!")
        print(f"Table ARN: {response['TableDescription']['TableArn']}")
        
        # Verify table structure
        table_description = dynamodb.describe_table(TableName=table_name)
        print(f"\nTable Details:")
        print(f"- Status: {table_description['Table']['TableStatus']}")
        print(f"- Item Count: {table_description['Table']['ItemCount']}")
        print(f"- Region: ap-southeast-2")
        
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_subscriptions_table()
