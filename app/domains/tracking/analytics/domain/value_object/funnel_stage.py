from enum import Enum


class FunnelStage(str, Enum):
    LAND = "LAND"
    IMPRESSION = "IMPRESSION"
    START = "START"
    CONVERT = "CONVERT"
