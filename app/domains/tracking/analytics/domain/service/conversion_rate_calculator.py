from app.domains.tracking.analytics.domain.value_object.funnel_count import FunnelCount
from app.domains.tracking.analytics.domain.value_object.funnel_stage_metrics import (
    FunnelStageMetrics,
)


def compute_funnel_metrics(counts: list[FunnelCount]) -> list[FunnelStageMetrics]:
    metrics: list[FunnelStageMetrics] = []
    previous: FunnelCount | None = None
    for current in counts:
        rate = _rate(current.distinct_sessions, previous)
        metrics.append(
            FunnelStageMetrics(
                stage=current.stage,
                distinct_sessions=current.distinct_sessions,
                conversion_rate=rate,
            )
        )
        previous = current
    return metrics


def _rate(current: int, previous: FunnelCount | None) -> float:
    if current == 0:
        return 0.0
    if previous is None:
        return 1.0
    if previous.distinct_sessions == 0:
        return 0.0
    return current / previous.distinct_sessions
