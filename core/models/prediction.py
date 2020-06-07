# coding: utf-8

from dataclasses import dataclass


@dataclass(frozen=True)
class Prediction:
    normal: float = 0
    pneumonia: float = 0
