import os

import pandas as pd

BASE_DIR = ""
DATA_DIR = os.path.join(BASE_DIR, "datas")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")

PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
WAYPOINTS_DIR = os.path.join(PROCESSED_DATA_DIR, "waypoints")
WAYPOINT_LIST_PATH = os.path.join(WAYPOINTS_DIR, "list.csv")
TRACK_DIR = os.path.join(PROCESSED_DATA_DIR, "tracks")

WAYPOINT_LIST_COLUMNS = pd.Index(["code", "parent_place", "name", "lat", "lon", "ele"])
