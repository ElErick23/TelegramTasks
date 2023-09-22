import json
import logging

from notion_client import Client

users = json.load(open('users.json'))
appsettings = json.load(open('appsettings.json'))


class Settings:

    def __init__(self, chat_id: int):
        self.chat_id = str(chat_id)

    @staticmethod
    def bot_token():
        return appsettings["botToken"]

    def get_notion_client(self):
        return Client(auth=users[self.chat_id]['notionKey'], log_level=logging.DEBUG)

    def get_database_id(self, key: str) -> str:
        return users[self.chat_id]['databases'][key]
