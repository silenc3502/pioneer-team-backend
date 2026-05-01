from abc import ABC, abstractmethod

from app.domains.tracking.analytics.domain.value_object.funnel_count import FunnelCount


class FunnelRepository(ABC):
    @abstractmethod
    def count_distinct_sessions_by_stage(self) -> list[FunnelCount]:
        ...
