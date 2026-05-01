from dataclasses import dataclass

from app.domains.tracking.analytics.domain.value_object.funnel_stage import (
    FunnelStage,
)


@dataclass(frozen=True)
class FunnelStageMetrics:
    stage: FunnelStage
    distinct_sessions: int
    conversion_rate: float

    def __post_init__(self) -> None:
        if self.distinct_sessions < 0:
            raise ValueError("distinct_sessions는 0 이상이어야 합니다.")
        if not 0.0 <= self.conversion_rate <= 1.0:
            raise ValueError("conversion_rate는 0.0~1.0 범위여야 합니다.")
