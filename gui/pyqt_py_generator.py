# coding: utf-8
# Генератор .ui -> .py-файлов и плагинов

import os
import shutil
import subprocess as sp
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Iterator, Union, Optional

# Текущий файл и директория с текущим файлом
CURRENT_FILE = Path(__file__)
CURRENT_PATH = CURRENT_FILE.parent

# Названия папок
#   1) ui-файлов
#   2) сгенерированных файлов
#   3) плагинов для QtDesigner
#   4) ресурсов, в которой лежит resources.qrc
UI_PATH_NAME = "ui"
GENERATED_PATH_NAME = "generated"
PLUGINS_PATH_NAME = "plugins"
RESOURCES_PATH_NAME = "resources"

# --- файлы ресурсов
RESOURCES_QRC_FILE_NAME = "resources.qrc"
RESOURCES_PY_FILE_NAME = "resources_rc.py"

# --- пути к папкам
UI_PATH = CURRENT_PATH.joinpath(UI_PATH_NAME)
GENERATED_PATH = CURRENT_PATH.joinpath(GENERATED_PATH_NAME)
PLUGINS_PATH = CURRENT_PATH.joinpath(PLUGINS_PATH_NAME)
RESOURCES_PATH = CURRENT_PATH.joinpath(RESOURCES_PATH_NAME)


class Utils:
    @staticmethod
    def snake_to_camel(word: str) -> str:
        return "".join(w.capitalize() or "_" for w in word.split("_"))

    @staticmethod
    def form_generated_filepath(root: str, file: str) -> Path:
        """
        Формирует путь к файлу .py, сгенерированному из .ui
        :param root: путь к файлу .ui
        :param file: название файла
        :return:
        """
        relpath = os.path.relpath(root, CURRENT_PATH)
        genpath = Path(os.path.join(
            GENERATED_PATH_NAME, f"{os.sep}".join(relpath.split(os.sep)[1:])
        ))
        return CURRENT_PATH.joinpath(genpath, f"ui_{file}").with_suffix(".py")

    # noinspection PyUnusedLocal
    @staticmethod
    def form_plugin_filepath(root: str, file: str) -> Path:
        """
        Формирует путь к файлу плагина .py, сгенерированному из .ui
        :param root: путь к файлу .ui
        :param file: название файла
        :return:
        """
        file_name = file.rsplit(".", maxsplit=1)[0]
        return PLUGINS_PATH.joinpath(f"{file_name}_plugin.py")

    @staticmethod
    def form_widget_import_path(root: str) -> str:
        """
        Генерирует относительный путь импорта
        Например, генерация путей при структуре:
        ui/
            subdir/
                subdir2/
                    file3.ui        # --> subdir.subdir2
                file2.ui            # --> subdir
            file1.ui                # --> <пусто>
        :param root:
        :return:
        """
        relpath = os.path.relpath(root, CURRENT_PATH)
        return f".".join(relpath.split(os.sep)[1:])

    @staticmethod
    def form_generated_dir_path(path: str) -> Path:
        relpath = os.path.relpath(path, CURRENT_PATH)
        return Path(os.path.join(
            GENERATED_PATH, f"{os.sep}".join(relpath.split(os.sep)[1:])
        ))

    @staticmethod
    def form_plugin_dir_path(path: str) -> str:
        relpath = os.path.relpath(path, CURRENT_PATH)
        return Path(os.path.join(
            PLUGINS_PATH, f"{os.sep}".join(relpath.split(os.sep)[1:])
        ))


class BaseTask:
    def __init__(
            self,
            src_path: Optional[Path] = None,
            dst_path: Optional[Path] = None
    ) -> None:
        self._src_path: Optional[Path] = src_path
        self._dst_path: Optional[Path] = dst_path

    def __str__(self) -> str:
        return f"<BaseTask>: {self._src_path} -> {self._dst_path}"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def src_path(self) -> Path:
        return self._src_path

    @property
    def dst_path(self) -> Path:
        return self._dst_path


class GeneratedTask(BaseTask):
    ...


class PluginTask(BaseTask):
    PLUGIN_TEMPLATE = """# coding: utf-8

# ----
# Внимание! 
# Этот плагин был сгенерирован автоматически.
# Любые изменения в нем могут быть потеряны!

from PyQt5.QtGui import QIcon
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin

from gui.widgets.{widget_path} import {widget_cls_name}


class {plugin_cls_name}(QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initialized = False

    def initialize(self, core):
        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return {widget_cls_name}(parent)

    def name(self):
        return "{widget_cls_name}"

    def group(self):
        return "Custom Widgets"

    def icon(self):
        return QIcon()

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="{widget_cls_name}" name="{widget_name}">\\n' \\
               '</widget>\\n'

    def includeFile(self):
        return "gui.widgets.{widget_path}"

"""

    def __init__(self, iwp: str = "", *args, **kwargs) -> None:
        """
        iwp - путь импорта виджета
        :param iwp:
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self._import_widget_path: str = iwp

    @property
    def import_path(self):
        return self._import_widget_path


class CreateResourcesRcTask(BaseTask):
    ...


class CopyTask(BaseTask):
    ...


class PrepareGeneratedDirTask(BaseTask):
    ...


class PreparePluginDirTask(BaseTask):
    ...


class TaskPerformer:
    @staticmethod
    def make_generated(task: GeneratedTask) -> None:
        src_path: Path = task.src_path
        dst_path: Path = task.dst_path

        cmd: str = "pyuic5.exe"
        p = sp.Popen(
            args=[
                cmd, "--from-imports", "--output", f"{dst_path}", f"{src_path}"
            ],
            shell=True,
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        p.wait()
        print(f"Создание файла {dst_path} завершено.")

    @staticmethod
    def make_plugin(task: PluginTask) -> None:
        dst_path: Path = task.dst_path

        dst_path_stem = dst_path.stem

        plugin_cls_name = Utils.snake_to_camel(dst_path_stem)

        # Имя виджета - MyWidgetPlugin -> [:-6] -> MyWidget
        widget_cls_name = plugin_cls_name[:-6]
        widget_name = f"{widget_cls_name[0].lower()}{widget_cls_name[1:]}"

        widget_path = dst_path_stem[:-7]
        import_path = task.import_path
        if import_path:
            widget_path = f"{import_path}.{widget_path}"

        dst_path.write_text(
            PluginTask.PLUGIN_TEMPLATE.format(**{
                "widget_path": widget_path,
                "widget_cls_name": widget_cls_name,
                "widget_name": widget_name,
                "plugin_cls_name": plugin_cls_name,
            }), encoding="utf-8"
        )

        print(f"Создание файла {dst_path} завершено.")

    @staticmethod
    def make_python_directory(path: Path) -> None:
        if not path.exists():
            path.mkdir(parents=True)

        init_file_path = path.joinpath("__init__.py")
        if not init_file_path.exists():
            init_file_path.write_text("")

    @staticmethod
    def prepare_directory(
            task: Union[PrepareGeneratedDirTask, PreparePluginDirTask]
    ) -> None:
        TaskPerformer.make_python_directory(task.dst_path)

    @staticmethod
    def make_resources_rc(task: CreateResourcesRcTask) -> None:
        print("Создание файла ресурсов...")

        src_path: Path = task.src_path
        dst_path: Path = task.dst_path

        cmd = "pyrcc5.exe"
        p = sp.Popen(
            args=[cmd, "-o", f"{dst_path}", f"{src_path}"],
            shell=True,
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        p.wait()

        print(f"Файл ресурсов \"{dst_path}\" создан.")

    @staticmethod
    def make_copy(task: CopyTask) -> None:
        src_path = task.src_path
        dst_path = task.dst_path

        shutil.copy(str(src_path), str(dst_path))
        print(f"Файл \"{src_path}\" скопирован в \"{dst_path}\"")


def prepare_tasks(argv, filters=("ui",)) -> Iterator[BaseTask]:
    yield PrepareGeneratedDirTask(dst_path=GENERATED_PATH)

    if argv.get("plugins_need"):
        yield PreparePluginDirTask(dst_path=PLUGINS_PATH)

    # генерируем все необходимые файлы (сгенерированные и плагины)
    yield from prepare_needed_tasks(argv, filters)

    if argv.get("resources_need"):
        # генерировать файлы ресурсов
        # --- resources_rc.py

        yield CreateResourcesRcTask(
            src_path=RESOURCES_PATH.joinpath(RESOURCES_QRC_FILE_NAME),
            dst_path=GENERATED_PATH.joinpath(RESOURCES_PY_FILE_NAME),
        )

        # yield from prepare_resources_copy_tasks()


def prepare_needed_tasks(argv, filters=("ui",)):
    plugins_need = argv.get("plugins_need")
    for root, dirs, files in os.walk(UI_PATH):

        # Подготавливаем каждую директорию
        for directory in dirs:
            path = Path(os.path.join(root, directory))
            generated_dir = Utils.form_generated_dir_path(path)
            yield PrepareGeneratedDirTask(dst_path=generated_dir)

            # if plugins_need:
            #     plugin_dir = Utils.form_plugin_dir_path(path)
            #     yield PreparePluginDirTask(dst_path=plugin_dir)

        for file in (file for file in files if file.endswith(filters)):
            src_path = Path(root).joinpath(file)

            # --- generated .ui -> ui_*.py
            py_generated_path = Utils.form_generated_filepath(root, file)
            yield GeneratedTask(src_path=src_path, dst_path=py_generated_path)

            if plugins_need:
                # генерировать плагины
                # --- generated .ui -> *_plugin.py
                py_plugin_path = Utils.form_plugin_filepath(root, file)
                iwp = Utils.form_widget_import_path(root)
                yield PluginTask(
                    iwp=iwp, src_path=src_path, dst_path=py_plugin_path
                )


def prepare_resources_copy_tasks() -> Iterator[CopyTask]:
    resources_rc_src = GENERATED_PATH.joinpath(RESOURCES_PY_FILE_NAME)
    for root, dirs, files in os.walk(GENERATED_PATH):
        for directory in dirs:

            # Игнорируем папки вида __pycache__ и т.д.
            if directory.startswith("__") and directory.endswith("__"):
                continue

            yield CopyTask(
                src_path=resources_rc_src,
                dst_path=Path(root).joinpath(directory, RESOURCES_PY_FILE_NAME)
            )


tasks_mapping = {
    GeneratedTask: TaskPerformer.make_generated,
    PrepareGeneratedDirTask: TaskPerformer.prepare_directory,

    PluginTask: TaskPerformer.make_plugin,
    PreparePluginDirTask: TaskPerformer.prepare_directory,

    CreateResourcesRcTask: TaskPerformer.make_resources_rc,
    CopyTask: TaskPerformer.make_copy,
}


def handle_task(task: Union[GeneratedTask, PluginTask]) -> None:
    tasks_mapping[type(task)](task)


def run_tasks(tasks) -> None:
    # --- Прямой прогон
    # for task in tasks:
    #     handle_task(task)

    # --- С помощью multiprocessing
    pool = Pool(cpu_count())
    pool.imap(handle_task, tasks)
    pool.close()
    pool.join()

    # --- С помощью threading.Thread
    # from threading import Thread
    # threads = [
    #     Thread(target=handle_task, args=(task, ))
    #     for task in tasks
    # ]
    # for t in threads:
    #     t.start()
    # for t in threads:
    #     t.join()
    # ---


def main():
    print("Запуск программы...")

    argv = {
        "plugins_need": True,
        "resources_need": True,
    }

    print("Выполнение заданий...")

    # ---
    start = time.time()
    run_tasks(prepare_tasks(argv))

    if argv.get("resources_need"):
        print("Копируем файл ресурсов в подпапки...")
        run_tasks(prepare_resources_copy_tasks())
    # ---

    print(f"Завершено. ({time.time() - start:>.4f} с)")

    print("Программа завершила свою работу.")


if __name__ == "__main__":
    main()
