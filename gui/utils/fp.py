# coding: utf-8

from pathlib import Path


def image_filepath_valid(path: Path) -> bool:
    return (
        path.exists()
        and path.is_file()
        and path.suffix in {".png", ".jpg", ".jpeg"}
    )
