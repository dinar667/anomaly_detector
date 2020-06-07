# coding: utf-8

from tensorflow_core.python.keras.models import load_model, Sequential

from core.config import CalculationConfig
from core.settings import MODEL_PATH


def get_model() -> Sequential:
    model = load_model(MODEL_PATH)
    return model


def get_config() -> CalculationConfig:
    config = CalculationConfig()
    return config
