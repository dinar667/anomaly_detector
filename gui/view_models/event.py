# coding: utf-8

import enum


class Event(enum.Enum):
    ImageAdded = enum.auto()
    ImageRemoved = enum.auto()

    ResultUpdated = enum.auto()
