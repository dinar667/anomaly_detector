# coding: utf-8

from dataclasses import dataclass


@dataclass(frozen=True)
class CalculationConfig:
    width: int = 300
    height: int = 300
