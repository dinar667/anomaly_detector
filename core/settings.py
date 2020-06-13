# coding: utf-8

from pathlib import Path

MODEL_DIR: str = "static"
MODEL_FILENAME: str = "np_300x300_e25_rmsprop_categorical_v1832.h5"

MODEL_PATH: Path = Path(__file__).parent.joinpath(MODEL_DIR, MODEL_FILENAME)
