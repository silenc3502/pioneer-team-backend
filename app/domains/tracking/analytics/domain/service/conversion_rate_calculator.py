from app.domains.tracking.analytics.domain.value_object.funnel_count import FunnelCount
from app.domains.tracking.analytics.domain.value_object.funnel_stage_metrics import (
    FunnelStageMetrics,
)


def compute_funnel_metrics(
    current: list[FunnelCount],
    previous: list[FunnelCount],
) -> list[FunnelStageMetrics]:
    previous_by_stage = {p.stage: p.distinct_sessions for p in previous}
    metrics: list[FunnelStageMetrics] = []
    previous_in_funnel: FunnelCount | None = None
    for current_count in current:
        conversion = _conversion_rate(
            current_count.distinct_sessions, previous_in_funnel
        )
        previous_distinct = previous_by_stage.get(current_count.stage, 0)
        delta = _delta_rate(current_count.distinct_sessions, previous_distinct)
        metrics.append(
            FunnelStageMetrics(
                stage=current_count.stage,
                distinct_sessions=current_count.distinct_sessions,
                conversion_rate=conversion,
                previous_distinct_sessions=previous_distinct,
                delta_rate=delta,
            )
        )
        previous_in_funnel = current_count
    return metrics


def _conversion_rate(current: int, previous: FunnelCount | None) -> float:
    if current == 0:
        return 0.0
    if previous is None:
        return 1.0
    if previous.distinct_sessions == 0:
        return 0.0
    return current / previous.distinct_sessions


def _delta_rate(current: int, previous: int) -> float | None:
    if previous == 0:
        return 0.0 if current == 0 else None
    return (current - previous) / previous
