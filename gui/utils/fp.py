# coding: utf-8

from pathlib import Path
from typing import Optional, List

from PyQt5.QtWidgets import QWidget, QFileDialog


def image_filepath_valid(path: Path) -> bool:
    return (
        path.exists()
        and path.is_file()
        and path.suffix in {".png", ".jpg", ".jpeg"}
    )


def save_file_dialog(
    parent: QWidget,
    caption: str,
    filters: str = "",
    filepath: str = "",
    options: Optional[QFileDialog.Options] = None,
) -> Path:
    if options is None:
        options = QFileDialog.Options()

    # noinspection PyCallByClass
    filepath, _ = QFileDialog.getSaveFileName(
        parent, caption, filepath, filters, options=options
    )
    return Path(filepath)


def open_files_dialog(
    parent: QWidget,
    caption: str,
    filters: str = "",
    filepath: str = "",
    options: QFileDialog.Options = None,
) -> List[Path]:
    if options is None:
        options = QFileDialog.Options()

    # noinspection PyCallByClass
    filepaths, _ = QFileDialog.getOpenFileNames(
        parent, caption, filepath, filters, options=options
    )
    return [Path(fp) for fp in filepaths]
