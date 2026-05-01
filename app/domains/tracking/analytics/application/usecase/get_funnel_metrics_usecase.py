from app.domains.tracking.analytics.application.port.funnel_repository import (
    FunnelRepository,
)
from app.domains.tracking.analytics.domain.service.conversion_rate_calculator import (
    compute_funnel_metrics,
)
from app.domains.tracking.analytics.domain.service.period_resolver import (
    derive_previous_range,
)
from app.domains.tracking.analytics.domain.value_object.content_filter import (
    ContentFilter,
)
from app.domains.tracking.analytics.domain.value_object.funnel_stage_metrics import (
    FunnelStageMetrics,
)
from app.domains.tracking.analytics.domain.value_object.period import TimeRange


class GetFunnelMetricsUseCase:
    def __init__(self, repository: FunnelRepository) -> None:
        self._repository = repository

    def execute(
        self,
        time_range: TimeRange,
        content_filter: ContentFilter,
    ) -> list[FunnelStageMetrics]:
        current = self._repository.count_distinct_sessions_by_stage(
            time_range, content_filter
        )
        previous_range = derive_previous_range(time_range)
        previous = self._repository.count_distinct_sessions_by_stage(
            previous_range, content_filter
        )
        return compute_funnel_metrics(current, previous)
