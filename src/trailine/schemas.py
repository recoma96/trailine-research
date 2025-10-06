from typing import List
from pydantic import BaseModel, Field


class RawTrackPoint(BaseModel):
    """
    GPS 트랙의 한 지점을 나타내는 모델
    JSON에서는 위도(lat)와 경도(lon)가 문자열이지만, Pydantic이 자동으로 float으로 변환합니다.
    """
    lat: float
    lon: float
    ele: int


class RawSegment(BaseModel):
    """등산 코스의 한 구간(segment)을 나타내는 모델"""
    name: str
    track: List[RawTrackPoint]
    start: str = Field(..., alias="from")
    end: str = Field(..., alias="to")


class RawCourse(BaseModel):
    """하나의 완전한 등산 코스(trail)를 나타내는 모델"""
    title: str
    subTitle: str
    parent_place: str = Field(..., alias="parentPlace")
    segments: List[RawSegment]
