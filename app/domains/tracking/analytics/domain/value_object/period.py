from dataclasses import dataclass
from enum import Enum


class PeriodOption(str, Enum):
    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"


@dataclass(frozen=True)
class TimeRange:
    start_ms: int
    end_ms: int

    def __post_init__(self) -> None:
        if self.start_ms < 0 or self.end_ms < 0:
            raise ValueError("timestamp는 0 이상이어야 합니다.")
        if self.start_ms > self.end_ms:
            raise ValueError("start_ms는 end_ms보다 작거나 같아야 합니다.")
