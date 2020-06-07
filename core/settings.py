# coding: utf-8

from pathlib import Path

MODEL_DIR: str = "static"
MODEL_FILENAME: str = "np_150x150_e30_rmsprop_binary_v1706.h5"

# MODEL_PATH: Path = Path(__file__).parent.joinpath(MODEL_DIR, MODEL_FILENAME)
MODEL_PATH: Path = Path(
    r"D:\ml\sln\np_300x300_e30_rmsprop_categorical_v1726.h5"
    # r"D:\ml\sln\np_450x450_e30_rmsprop_binary_v1900.h5"
)
