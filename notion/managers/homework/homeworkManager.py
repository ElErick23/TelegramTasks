from notion_client.helpers import collect_paginated_api
from notion.managers.homework.homework import Homework
from settings import Settings
import datetime as dt


class HomeworkManager:

    def __init__(self, chat_id: int):
        self.settings = Settings(chat_id)
        self.notion_client = self.settings.get_notion_client()
        self.database_id = self.settings.get_database_id("homeworks")

    def query_undone(self) -> list:
        undone = []
        raw_results = collect_paginated_api(
            self.notion_client.databases.query,
            database_id=self.database_id,
            filter={"property": "Hecho", "checkbox": {"equals": False}},
            sorts=[{"property": "Vencimiento", "direction": "ascending"}]
        )
        for result in raw_results:
            properties = result['properties']
            title = properties['Nombre']['title']
            if len(title) == 0:
                continue
            name = title[0].get('plain_text')

            due = properties['Vencimiento']['date'].get('start')
            if due is None:
                continue
            try:
                due = dt.datetime.strptime(due, "%Y-%m-%dT%H:%M:%S.%f%z")
            except ValueError:
                due = dt.datetime.strptime(due, '%Y-%m-%d')
            due = due.replace(tzinfo=None) - dt.timedelta(minutes=1)

            rollup = properties['MateriaNombre']['rollup']['array']
            if len(rollup) == 0 or len(rollup[0]['rich_text']) == 0:
                subject = 'Sin materia'
            else:
                subject = rollup[0]['rich_text'][0]['plain_text']

            type_select = properties['Tipo']['select']
            type_name = type_select['name'] if type_select is not None else 'Sin tipo'

            url = properties['URL']['url']

            undone.append(Homework(name, subject, due, type_name, url))

        return undone
