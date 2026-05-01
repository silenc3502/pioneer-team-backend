from dataclasses import dataclass

from app.domains.tracking.analytics.domain.value_object.funnel_stage import (
    FunnelStage,
)


@dataclass(frozen=True)
class FunnelCount:
    stage: FunnelStage
    distinct_sessions: int

    def __post_init__(self) -> None:
        if self.distinct_sessions < 0:
            raise ValueError("distinct_sessions는 0 이상이어야 합니다.")
