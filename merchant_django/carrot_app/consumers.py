import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "test"  # 채팅방 이름
        self.room_group_name = f"chat_{self.room_name}"

        # 채팅 그룹에 참가
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # 채팅 그룹에서 나가기
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # 클라이언트로부터 메시지 받기
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # 받은 메시지를 채팅 그룹으로 전송
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # 채팅 메시지 받아서 클라이언트로 전송
    async def chat_message(self, event):
        message = event["message"]

        # 클라이언트로 메시지 보내기
        await self.send(text_data=json.dumps({"message": message}))
