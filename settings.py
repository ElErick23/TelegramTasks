import json
import logging

from notion_client import Client

appsettings = json.load(open('appsettings.json'))


class Settings:

    @staticmethod
    def get_appsettings():
        return appsettings

    @staticmethod
    def get_notion_client():
        return Client(auth=appsettings['notionKey'], log_level=logging.DEBUG)

    @staticmethod
    def get_database_id(key: str) -> str:
        return appsettings['databases'][key]
