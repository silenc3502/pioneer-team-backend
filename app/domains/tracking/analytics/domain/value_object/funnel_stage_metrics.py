from dataclasses import dataclass

from app.domains.tracking.analytics.domain.value_object.funnel_stage import (
    FunnelStage,
)


@dataclass(frozen=True)
class FunnelStageMetrics:
    stage: FunnelStage
    distinct_sessions: int
    conversion_rate: float
    previous_distinct_sessions: int
    delta_rate: float | None

    def __post_init__(self) -> None:
        if self.distinct_sessions < 0:
            raise ValueError("distinct_sessions는 0 이상이어야 합니다.")
        if self.conversion_rate < 0.0:
            raise ValueError("conversion_rate는 0.0 이상이어야 합니다.")
        if self.previous_distinct_sessions < 0:
            raise ValueError(
                "previous_distinct_sessions는 0 이상이어야 합니다."
            )
