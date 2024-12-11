import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import get_notifications_from_redis


class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('Connecting in the backend')  # Console print
        await self.accept()

    async def disconnect(self, close_code):
        print('disconnecting')
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        print('received')
        # Send message back to client
        await self.send(text_data=json.dumps({
            'message': f"Server received: {message}"
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        print('user_id', self.user_id)
        
        if not self.user_id:
            print('IS_ANONYMOUS')
            await self.close()
        else:
            print('NOT ANONYMOUS')
            self.room_name = f'notification_user_{self.user_id}'

            # Add the user to their notification group
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()

            # Fetch historical notifications from Redis
            notifications = get_notifications_from_redis(self.user_id)
            print('notifications in the connect view', notifications)

            # # Send historical notifications to the WebSocket
            # for notification in notifications:
            #     print('notifictian in the loop', notification)
            #     await self.send(text_data=json.dumps(notification))
            await self.send(text_data=json.dumps(notifications))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def send_notification(self, event):
        pushmessage = event['message']
        await self.send(text_data=json.dumps({'pushmessage': pushmessage}))