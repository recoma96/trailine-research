import typer
from typing_extensions import Annotated
import os

from enum import Enum
from pathlib import Path

from trailine.io import (
    load_raw_course_data_from_json,
    preprocess_raw_data
)
from trailine.schemas import RawCourse


class FileTypeChoices(str, Enum):
    JSON = "json"
    GPX = "gpx"


def process(
        filepath: Annotated[
            Path,
            typer.Argument(
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                help="JSON (혹은 GPX) 파일 경로",
            ),
        ],
        file_type: Annotated[
            FileTypeChoices,
            typer.Option(
                "--file-type", "-t",
                help="파일 타입 (GPX모드는 아직 개발중)",
                case_sensitive=False
            )
        ] = FileTypeChoices.JSON,
) -> None:
    """
    JSON혹은 GPX파일을 받고 구간별로 분리해서 재가공하는 스크립트
    """
    validate_filepath(filepath, file_type)
    course = read_from_file(filepath, file_type)
    preprocess_raw_data(course)


def validate_filepath(filepath: Path, file_type: FileTypeChoices) -> None:
    _, file_ext = os.path.splitext(filepath)
    if file_ext.lower() != f".{file_type.value}".lower():
        raise typer.BadParameter(
            f"파일 타입 '{file_type.value}'이(가) 지정되었지만, 실제 파일 확장자는 '{file_ext}'입니다. "
            f"파일 경로 혹은 --file-type 옵션을 확인해주세요."
        )


def read_from_file(filepath: Path, file_type: FileTypeChoices) -> RawCourse:
    match file_type:
        case FileTypeChoices.JSON:
            return load_raw_course_data_from_json(filepath)
        case FileTypeChoices.GPX:
            raise NotImplemented
        case _:
            raise ValueError(f"{file_type.value} is not supported")


def main() -> None:
    typer.run(process)


if __name__ == "__main__":
    main()
