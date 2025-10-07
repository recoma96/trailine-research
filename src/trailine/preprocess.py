import json
import os.path
from typing import List, Tuple, Dict, Any

import pandas as pd

from trailine.schemas import (
    RawCourse,
    RawSegment,
    RawTrackPoint
)
from trailine.utils import (
    create_track_geojson_object_from_raw,
    generate_unique_code
)
from trailine.vars import (
    WAYPOINT_LIST_PATH,
    WAYPOINT_LIST_COLUMNS,
    TRACK_DIR
)


class CoursePreProcessor:
    """
    트랙 RAW데이터를 가공하기 위한 클래스
    """
    raw_course: RawCourse

    def __init__(self, raw_course: RawCourse):
        self.raw_course = raw_course
        self._set_waypoints_csv()


    def save(self) -> None:
        """
        Raw 데이터를 가공해서 저장하는 함수
        """
        waypoint_codes: List[str] = []
        for i, segment in enumerate(self.raw_course.segments):
            new_waypoint_codes = self._save_waypoints(segment, i > 0)
            # 두번째 세그먼트부터 시작 웨이포인트를 무시 (중복이슈)
            waypoint_codes.extend(new_waypoint_codes)
            self._save_tracks(segment, waypoint_codes[-2], waypoint_codes[-1])


    def _set_waypoints_csv(self) -> None:
        """
        웨이포인트 관련 csv 파일 세팅
        파일들이 없을 경우 자동생성
        """
        if not os.path.isfile(WAYPOINT_LIST_PATH):
            os.makedirs(os.path.dirname(WAYPOINT_LIST_PATH), exist_ok=True)
            pd.DataFrame(columns=WAYPOINT_LIST_COLUMNS).to_csv(WAYPOINT_LIST_PATH, index=False)


    def _save_waypoints(self, segment: RawSegment, ignore_start: bool = False) -> List[str]:
        """
        웨이포인트 데이터 적재
        """

        # 웨이포인트 파일 로드
        waypoints_df = pd.read_csv(
            WAYPOINT_LIST_PATH,
            dtype={"lat": float, "lon": float, "ele": float}
        )
        parent_place = self.raw_course.parent_place

        # 생성 및 갱신할 웨이포인트 수집
        waypoints_to_check = self._collect_waypoints_for_create_or_update(segment, ignore_start)
        new_waypoints: List[Dict[str, Any]] = []
        for name, loc in waypoints_to_check:
            # 기존의 웨이포인트가 존재하는 지 확인
            is_waypoint_exists = not waypoints_df[
                (waypoints_df["parent_place"] == parent_place)
                & (waypoints_df["name"] == name)
            ].empty

            if not is_waypoint_exists:
                code = generate_unique_code()
                new_waypoint = {
                    "code": code,
                    "parent_place": parent_place,
                    "name": name,
                    "lat": loc.lat,
                    "lon": loc.lon,
                    "ele": loc.ele
                }
                new_waypoints.append(new_waypoint)

        # list.csv 업데이트
        new_df = pd.DataFrame(new_waypoints)
        if not new_df.empty:
            waypoints_df = pd.concat([waypoints_df, new_df], ignore_index=True)
        waypoints_df.to_csv(WAYPOINT_LIST_PATH, index=False)

        return [w["code"] for w in new_waypoints]


    def _save_tracks(self, segment: RawSegment, start_waypoint_code: str, end_waypoint_code: str) -> None:
        """
        트랙 저장 함수
        """

        # 상위 항목 디렉토리 세팅
        dirpath = os.path.join(TRACK_DIR, self.raw_course.parent_place)
        os.makedirs(dirpath, exist_ok=True)

        # 트렉 데이터 (GeoJSON) 생성
        track_full_name = f"{self.raw_course.parent_place}-{segment.start}-{segment.end}"
        geojson_obj = create_track_geojson_object_from_raw(
            segment,
            self.raw_course.parent_place,
            start_waypoint_code, end_waypoint_code
        )

        # 파일 저장
        filepath = os.path.join(dirpath, f"{track_full_name}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(geojson_obj, f, ensure_ascii=False, indent=2)


    def _collect_waypoints_for_create_or_update(
            self,
            segment: RawSegment,
            ignore_start: bool = False
    ) -> List[Tuple[str, RawTrackPoint]]:
        """
        웨이포인트 시작 및 끝지점 추출
        """
        target_waypoints = [(segment.start, segment.track[0])]
        if not ignore_start and len(segment.track) > 1:
            target_waypoints.append((segment.end, segment.track[-1]))
        return target_waypoints
