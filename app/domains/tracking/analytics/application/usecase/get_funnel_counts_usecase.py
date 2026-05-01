from app.domains.tracking.analytics.application.port.funnel_repository import (
    FunnelRepository,
)
from app.domains.tracking.analytics.domain.value_object.funnel_count import FunnelCount


class GetFunnelCountsUseCase:
    def __init__(self, repository: FunnelRepository) -> None:
        self._repository = repository

    def execute(self) -> list[FunnelCount]:
        return self._repository.count_distinct_sessions_by_stage()
