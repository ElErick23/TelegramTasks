from datetime import datetime


class Homework:

    def __init__(self, name: str, subject: str, due: datetime, type_name: str, url: str):
        self.name = name
        self.subject = subject
        self.type_name = type_name
        self.due = due
        self.url = url

    def to_markdown(self):
        return f'• {self.name}\n`{"".ljust(5)}{self.subject.ljust(15)}({self.type_name})`\n'

    def __str__(self):
        return f'[{self.name}]({self.subject}) - {self.due} - {self.type_name} - {self.url}'
