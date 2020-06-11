# coding: utf-8

from pathlib import Path

from PIL import Image
from asq import query
from dataclasses import dataclass


@dataclass(frozen=True)
class CropOffset:
    """
    Параметры отступа от краёв картинки в процентах (от 0 до 1)
    """

    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0


DEFAULT_CROP_CONFIG = CropOffset(top=0.15, right=0.15, left=0.15)


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix in {".png", ".jpg", ".jpeg"}


def crop(path: Path, offset: CropOffset = DEFAULT_CROP_CONFIG) -> Image.Image:
    im: Image.Image = Image.open(path)
    width, height = im.size

    top = offset.top * height
    right = offset.right * width
    bottom = offset.bottom * height
    left = offset.left * width

    shape = (left, top, width - right, height - bottom)
    cropped = im.crop(shape)

    return cropped


@dataclass(frozen=True)
class CopyInfo:
    src_path: Path
    dst_path: Path


def main():
    base_dir = Path("d:/ml/input/chest_xray/chest_xray")
    train_dir = base_dir.joinpath("train")
    val_dir = base_dir.joinpath("val")
    test_dir = base_dir.joinpath("test")

    base_copy_dir = Path("d:/ml/input/chest_xray/cropped")
    train_copy_dir = base_copy_dir.joinpath("train")
    val_copy_dir = base_copy_dir.joinpath("val")
    test_copy_dir = base_copy_dir.joinpath("test")

    copy_info = (
        CopyInfo(train_dir, train_copy_dir),
        CopyInfo(val_dir, val_copy_dir),
        CopyInfo(test_dir, test_copy_dir),
    )

    for info in copy_info:
        print(info.src_path)
        normal_dir = info.src_path.joinpath("NORMAL")
        pneumo_dir = info.src_path.joinpath("PNEUMONIA")

        for child_dir in (normal_dir, pneumo_dir):
            print(f"\t{child_dir.name}")
            images = query(child_dir.iterdir()).where(lambda x: is_image(x))

            for index, image_path in enumerate(images):
                cropped = crop(image_path)

                dst = info.dst_path.joinpath(child_dir.name, image_path.name)
                dst.parent.mkdir(parents=True, exist_ok=True)

                failed: bool = False
                cause: str = ""
                try:
                    cropped.save(dst)
                except Exception as ex:
                    failed = True
                    cause = str(ex)

                text: str = "(success)"
                if failed:
                    text = f"(failed: {cause})"
                print(f"\t\t{index} -- {image_path.name} {text}", flush=True)


if __name__ == "__main__":
    main()
