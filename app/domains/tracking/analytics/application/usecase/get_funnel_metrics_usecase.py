from app.domains.tracking.analytics.application.port.funnel_repository import (
    FunnelRepository,
)
from app.domains.tracking.analytics.domain.service.conversion_rate_calculator import (
    compute_funnel_metrics,
)
from app.domains.tracking.analytics.domain.value_object.funnel_stage_metrics import (
    FunnelStageMetrics,
)


class GetFunnelMetricsUseCase:
    def __init__(self, repository: FunnelRepository) -> None:
        self._repository = repository

    def execute(self) -> list[FunnelStageMetrics]:
        counts = self._repository.count_distinct_sessions_by_stage()
        return compute_funnel_metrics(counts)
