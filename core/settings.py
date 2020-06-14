# coding: utf-8

from pathlib import Path

MODEL_DIR: str = "static"
MODEL_FILENAME: str = "np_400x400_e10_rmsprop_categorical_vfinal.h5"

MODEL_PATH: Path = Path(__file__).parent.joinpath(MODEL_DIR, MODEL_FILENAME)
