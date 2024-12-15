# consumers.py
# Your code goes here:

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # This method is called when the WebSocket is handshaking as part of the connection process
        self.room_name = 'chatroom'  # Example: static chat room
        self.room_group_name = f'chat_{self.room_name}'  # Channel group name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # This method is called when the WebSocket closes for any reason
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # This method is called when a message is received from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # This method is called when a message is received from the room group
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
