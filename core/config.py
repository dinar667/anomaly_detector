# coding: utf-8

from dataclasses import dataclass


@dataclass(frozen=True)
class CalculationConfig:
    width: int = 400
    height: int = 400
