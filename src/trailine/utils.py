from typing import Dict
from uuid import uuid4

from trailine.schemas import RawSegment


def generate_unique_code() -> str:
    """
    CSV, JSON등 unique code 생성하는데 사용되는 함수
    uui4를 사용하며 하이픈(-)은 제거한다.
    """
    return str(uuid4()).replace("-", "")


def create_track_geojson_object_from_raw(
        segment: RawSegment,
        parent_place: str,
        start_waypoint_code: str,
        end_waypoint_code: str
) -> Dict:
    track_full_name = f"{parent_place}-{segment.start}-{segment.end}"
    return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "kind": "track",
                        "name": track_full_name,
                        "start_waypoint_code": start_waypoint_code,
                        "end_waypoint_code": end_waypoint_code,
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [p.lon, p.lat, p.ele]
                            for p in segment.track
                        ]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "kind": "start",
                        "code": start_waypoint_code,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            segment.track[0].lon, segment.track[0].lat, segment.track[0].ele
                        ]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "kind": "end",
                        "code": end_waypoint_code,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            segment.track[-1].lon, segment.track[-1].lat, segment.track[-1].ele
                        ]
                    }
                }
            ],
        }