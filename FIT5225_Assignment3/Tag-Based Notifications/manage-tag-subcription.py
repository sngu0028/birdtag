import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Initialize clients
sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

# Environment variables
SNS_TOPIC_ARN = 'arn:aws:sns:ap-southeast-2:057493959668:tagbasednotification-FIT5225'
SUBSCRIPTIONS_TABLE_NAME = os.environ.get('SUBSCRIPTIONS_TABLE_NAME', 'BirdTagSubscriptions')

# DynamoDB table for tracking subscriptions
subscriptions_table = dynamodb.Table(SUBSCRIPTIONS_TABLE_NAME)

def lambda_handler(event, context):
    """
    Main handler for managing tag subscriptions
    Supports operations: subscribe, unsubscribe, list
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Get user email from Cognito authorizer claims if available
        if event.get('requestContext', {}).get('authorizer', {}).get('claims'):
            user_email = event['requestContext']['authorizer']['claims']['email']
        else:
            user_email = body.get('email')
        
        operation = body.get('operation', 'subscribe')  # 'subscribe', 'unsubscribe', or 'list'
        tags_list = body.get('tags', [])
        
        # Validation
        if not user_email:
            return create_response(400, {'error': 'Email is required.'})
        
        # Route to appropriate handler
        if operation == 'subscribe':
            return handle_subscription(user_email, tags_list)
        elif operation == 'unsubscribe':
            return handle_unsubscription(user_email, tags_list)
        elif operation == 'list':
            return list_subscriptions(user_email)
        else:
            return create_response(400, {'error': 'Invalid operation. Use "subscribe", "unsubscribe", or "list".'})
            
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return create_response(500, {'error': f'Internal server error: {str(e)}'})

def handle_subscription(user_email, tags_list):
    """Handle subscription to bird tags"""
    if not tags_list:
        return create_response(400, {'error': 'No tags provided for subscription.'})
    
    try:
        # Check if user already has a subscription
        existing_subscription = get_user_subscription(user_email)
        
        if existing_subscription and existing_subscription.get('subscription_arn') != 'PendingConfirmation':
            # Update existing subscription
            subscription_arn = existing_subscription['subscription_arn']
            
            # Merge existing tags with new tags (no duplicates)
            existing_tags = set(existing_subscription.get('tags', []))
            new_tags = set(tags_list)
            all_tags = sorted(list(existing_tags.union(new_tags)))
            
            # Update SNS subscription filter
            update_subscription_filter(subscription_arn, all_tags)
            
            # Update DynamoDB record
            update_subscription_record(user_email, all_tags, subscription_arn)
            
            return create_response(200, {
                'message': f'Updated subscription for {user_email}',
                'tags': all_tags,
                'subscriptionArn': subscription_arn
            })
        else:
            # Create new subscription
            filter_policy = {
                "bird_species": tags_list
            }
            
            response = sns_client.subscribe(
                TopicArn=SNS_TOPIC_ARN,
                Protocol='email',
                Endpoint=user_email,
                Attributes={
                    'FilterPolicy': json.dumps(filter_policy)
                },
                ReturnSubscriptionArn=True
            )
            
            subscription_arn = response.get('SubscriptionArn')
            
            # Store in DynamoDB
            create_subscription_record(user_email, tags_list, subscription_arn)
            
            print(f"Created subscription for {user_email} with tags {tags_list}")
            
            return create_response(200, {
                'message': f'Subscription created for {user_email}. Please check your email to confirm.',
                'tags': tags_list,
                'subscriptionArn': subscription_arn,
                'requiresConfirmation': True
            })
            
    except Exception as e:
        print(f"Subscription error: {str(e)}")
        raise

def handle_unsubscription(user_email, tags_list):
    """Handle unsubscription from bird tags"""
    try:
        existing_subscription = get_user_subscription(user_email)
        
        if not existing_subscription:
            return create_response(404, {'error': 'No subscription found for this email.'})
        
        subscription_arn = existing_subscription['subscription_arn']
        
        if subscription_arn == 'PendingConfirmation':
            return create_response(400, {'error': 'Subscription is pending confirmation. Cannot unsubscribe.'})
        
        existing_tags = set(existing_subscription.get('tags', []))
        
        if not tags_list:
            # Unsubscribe from all
            sns_client.unsubscribe(SubscriptionArn=subscription_arn)
            delete_subscription_record(user_email)
            
            return create_response(200, {'message': f'Unsubscribed {user_email} from all notifications.'})
        else:
            # Remove specific tags
            tags_to_remove = set(tags_list)
            remaining_tags = sorted(list(existing_tags - tags_to_remove))
            
            if not remaining_tags:
                # No tags left, unsubscribe completely
                sns_client.unsubscribe(SubscriptionArn=subscription_arn)
                delete_subscription_record(user_email)
                
                return create_response(200, {'message': f'Unsubscribed {user_email} from all notifications.'})
            else:
                # Update filter with remaining tags
                update_subscription_filter(subscription_arn, remaining_tags)
                update_subscription_record(user_email, remaining_tags, subscription_arn)
                
                return create_response(200, {
                    'message': f'Updated subscription for {user_email}',
                    'remaining_tags': remaining_tags
                })
                
    except Exception as e:
        print(f"Unsubscription error: {str(e)}")
        raise

def list_subscriptions(user_email):
    """List user's current subscriptions"""
    try:
        subscription = get_user_subscription(user_email)
        
        if subscription:
            return create_response(200, {
                'email': user_email,
                'tags': subscription.get('tags', []),
                'subscription_arn': subscription.get('subscription_arn'),
                'confirmed': subscription.get('subscription_arn') != 'PendingConfirmation',
                'created_at': subscription.get('created_timestamp')
            })
        else:
            return create_response(404, {'message': 'No subscriptions found for this email.'})
            
    except Exception as e:
        print(f"List subscriptions error: {str(e)}")
        raise

def update_subscription_filter(subscription_arn, tags):
    """Update SNS subscription filter policy"""
    filter_policy = {
        "bird_species": tags
    }
    
    sns_client.set_subscription_attributes(
        SubscriptionArn=subscription_arn,
        AttributeName='FilterPolicy',
        AttributeValue=json.dumps(filter_policy)
    )

def get_user_subscription(user_email):
    """Get subscription record from DynamoDB"""
    try:
        response = subscriptions_table.get_item(Key={'email': user_email})
        return response.get('Item')
    except Exception as e:
        print(f"Error getting subscription: {str(e)}")
        return None

def create_subscription_record(user_email, tags, subscription_arn):
    """Create subscription record in DynamoDB"""
    timestamp = datetime.utcnow().isoformat()
    
    subscriptions_table.put_item(
        Item={
            'email': user_email,
            'tags': tags,
            'subscription_arn': subscription_arn,
            'created_timestamp': timestamp,
            'updated_timestamp': timestamp
        }
    )

def update_subscription_record(user_email, tags, subscription_arn):
    """Update subscription record in DynamoDB"""
    timestamp = datetime.utcnow().isoformat()
    
    subscriptions_table.update_item(
        Key={'email': user_email},
        UpdateExpression='SET tags = :tags, subscription_arn = :arn, updated_timestamp = :ts',
        ExpressionAttributeValues={
            ':tags': tags,
            ':arn': subscription_arn,
            ':ts': timestamp
        }
    )

def delete_subscription_record(user_email):
    """Delete subscription record from DynamoDB"""
    subscriptions_table.delete_item(Key={'email': user_email})

def create_response(status_code, body):
    """Create API Gateway response with proper headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(body)
    }
