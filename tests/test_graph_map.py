from trailine.graph_map import GraphMap


def test_search_waypoint_by_waypoint_name():
    graph_map = GraphMap()

    # 사당 이라는 이름으로 연관검색
    waypoints = graph_map.search_waypoints(name="연주")
    
    """
    아래와 같은 데이터가 검색되어야 한다
    
    연주대
    연주암
    """
    assert len(waypoints) == 2
    assert waypoints[0].name == "연주대"
    assert waypoints[1].name == "연주암"


def test_search_waypoint_by_parent_place_name():
    graph_map = GraphMap()

    # 관악이라는 이름으로 검색
    waypoints = graph_map.search_waypoints(parent_place_name="관악")

    """
    관악산에 포함된 모든 데이터가 검색되어야 한다.
    """
    assert len(waypoints) == 6
    for waypoint in waypoints:
        assert waypoint.parent_place.name == "관악산"
