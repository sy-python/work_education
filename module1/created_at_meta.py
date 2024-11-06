# Задача - Атрибуты класса


import datetime


class CreatedAtMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs["created_at"] = datetime.datetime.now()
        return super().__new__(cls, name, bases, attrs)
