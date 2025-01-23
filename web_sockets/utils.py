
import redis
import json
from datetime import datetime
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.conf import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)


def store_notification_in_redis(user_id, message, type, senderId):
    print('storing in the redis')
    # Key format: notifications:<user_id>
    key = f'notifications:{user_id}'
    if senderId:
        notification = {
        'senderId':senderId,
        'notification_type': type,
        'message': message,
        'timestamp': str(datetime.now())
        }
    else:    
        # Add the notification as a JSON string
        notification = {
            'notification_type': type,
            'message': message,
            'timestamp': str(datetime.now())
        }
    
    print('notification;;;', key, notification)
    
    redis_client.rpush(key, json.dumps(notification))
    print('pushed...')
    # Set TTL for the key (14 days in seconds)
    redis_client.expire(key, 14 * 24 * 60 * 60)
    
    res = get_notifications_from_redis(user_id)
    print('res',res)
    

def get_notifications_from_redis(user_id):
    # Key format: notifications:<user_id>
    print('going to get the notifications from redis')
    key = f'notifications:{user_id}'
    notifications = redis_client.lrange(key, 0, -1)
    print('notifications in getting view///', notifications)
    return [json.loads(notification) for notification in notifications[::-1]]

@sync_to_async
def send_user_notification(user_id, message, type, senderId=None):
    # Store the notification in Redis
    print('received the notification')
    store_notification_in_redis(user_id, message, type, senderId)
    print('storing in tehy redis ')
    # Send real-time notification via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notification_user_{user_id}',  # Unique group for the user
        {
            'type': 'send_notification',
            'message': message,
            'notification_type': type,
            'timestamp': str(datetime.now())
        }
    )
  
