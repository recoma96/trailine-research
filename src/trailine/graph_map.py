import json
import os
import glob
from typing import List, Dict, DefaultDict, Optional
from collections import defaultdict

import pandas as pd

from trailine.vars import WAYPOINT_LIST_PATH, TRACK_DIR


class LocationPoint:
    """
    위경도/해발고도 정보를 표현
    """
    lat: float
    lon: float
    ele: float

    def __init__(self, lat: float, lon: float, ele: float):
        self.lat, self.lon, self.ele = lat, lon, ele

class ParentPlace:
    """
    상위 카테고리
    예: 해파랑길, 관악산, 청주시 등...
    """
    id: int
    name: str

    def __init__(self, name: str, id: int):
        self.name, self.id = name, id

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"


class Waypoint(LocationPoint):
    """
    주요 지점
    르래킹 구간의 첫/끝점이 될 수 있고,
    특정 조망대나, 다른 볼거리고 포함된다.
    """
    code: str
    name: str
    parent_place: ParentPlace

    def __init__(self, lat: float, lon: float, ele: float, code: str, name: str, parent_place: ParentPlace):
        super().__init__(lat, lon, ele)
        self.code, self.name, self.parent_place = code, name, parent_place


class Track:
    """
    트레킹 또는 하이킹 구간을 표현
    """
    start: Waypoint
    end: Waypoint
    circuit: List[LocationPoint]
    name: str

    def __init__(self, start: Waypoint, end: Waypoint, circuit: List[LocationPoint], name: str):
        self.start, self.end, self.circuit, self.name = start, end, circuit, name


type TrackGraph = DefaultDict[str, DefaultDict[str, List[Track]]]


class GraphMap:
    """
    지도상의 코스 및 지점 정보를 담는 주요 클라스
    """
    parent_places: Dict[str, ParentPlace]
    waypoints: Dict[str, Waypoint]
    tracks: TrackGraph

    def __init__(self):
        self.tracks = defaultdict(lambda: defaultdict(list[Track]))
        self.waypoints = {}
        self.parent_places = {}

        self._set_waypoints()
        self._set_tracks()

    def get_waypoint(self, code: str) -> Optional[Waypoint]:
        return self.waypoints.get(code)
    
    def search_waypoints(
            self,
            *,
            parent_place_name: Optional[str] = None,
            name: Optional[str] = None
    ) -> List[Waypoint]:
        """
        조건에 맞는 Waypoint를 검색.

        :param parent_place_name: Waypoint의 상위 카테고리 이름 (부분 일치)
        :param name: Waypoint 이름 (부분 일치)
        :return: 검색 조건에 맞는 Waypoint 리스트
        """
        candidates = list(self.waypoints.values())

        if parent_place_name:
            candidates = [wp for wp in candidates if parent_place_name in wp.parent_place.name]
        if name:
            candidates = [wp for wp in candidates if name in wp.name]

        # 글자 오름차순으로 정렬
        candidates.sort(key=lambda e: e.name)
        return candidates

    def _set_waypoints(self):
        """
        /datas/processed/waypoint/list.csv 파일로부터 정보를 가져온다.
        """
        waypoints_df = pd.read_csv(
            WAYPOINT_LIST_PATH,
            dtype={"lat": float, "lon": float, "ele": float}
        )

        new_parent_id = 1
        for _, row in waypoints_df.iterrows():
            # 상위 항목 설정하기
            parent_place = row["parent_place"]
            if parent_place not in self.parent_places:
                self.parent_places[parent_place] = ParentPlace(parent_place, new_parent_id)
                new_parent_id += 1

            # waypoint 저장
            parent = self.parent_places[parent_place]
            waypoint = Waypoint(row["lat"], row["lon"], row["ele"], row["code"], row["name"], parent)
            self.waypoints[row["code"]] = waypoint

    def _set_tracks(self):
        """
        /datas/processed/tracks 내의 모든 트랙 json 파일을 순회하며
        Track 객체를 생성하고 self.track_points에 저장
        """
        track_files = self._get_track_files()
        for filepath in track_files:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            track_feature = data["features"][0]

            # properties에서 Waypoint 객체 가져오기
            properties = track_feature["properties"]
            start_code = properties["start_waypoint_code"]
            end_code = properties["end_waypoint_code"]

            start_waypoint = self.waypoints[start_code]
            end_waypoint = self.waypoints[end_code]

            # geometry에서 LocationPoint 리스트 생성하기 (GeoJSON은 lon, lat 순서)
            coordinates = track_feature["geometry"]["coordinates"]
            circuit = [LocationPoint(lat=point[1], lon=point[0], ele=point[2]) for point in coordinates]

            # 3. Track 객체 생성 및 저장 (양방향)
            track = Track(start=start_waypoint, end=end_waypoint, circuit=circuit, name=properties["name"])
            self.tracks[start_code][end_code].append(track)
            self.tracks[end_code][start_code].append(track)


    def _get_track_files(self) -> List[str]:
        """
        /datas/processed/tracks 디렉토리 내의 모든 .json 파일 경로를 재귀적으로 찾아서 반환
        """
        if not os.path.isdir(TRACK_DIR):
            return []

        pattern = os.path.join(TRACK_DIR, '**', '*.json')
        return glob.glob(pattern, recursive=True)
