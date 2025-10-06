import os
from pathlib import Path

from trailine.exc import FileTypeError
from trailine.preprocess import CoursePreProcessor
from trailine.schemas import RawCourse


def load_raw_course_data_from_json(filepath: str | Path) -> RawCourse:
    """
    주어진 경로의 JSON 파일을 읽어 CourseSchema 객체로 변환합니다.

    :param filepath: JSON 파일의 경로
    :return: CourseSchema 객체
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError

    _, ext = os.path.splitext(filepath)
    if ext.lower() != ".json":
        raise FileTypeError("")

    with open(filepath, "r", encoding="utf-8") as f:
        json_data = f.read()
    return RawCourse.model_validate_json(json_data)


def preprocess_raw_data(course: RawCourse) -> None:
    """
    코스데이터를 재가공 또는 적재하는 함수

    :param course:
    :param output_dir:
    """
    pre_processor = CoursePreProcessor(course)
    pre_processor.save()
