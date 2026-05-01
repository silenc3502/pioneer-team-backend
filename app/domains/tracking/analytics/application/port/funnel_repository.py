from abc import ABC, abstractmethod

from app.domains.tracking.analytics.domain.value_object.content_filter import (
    ContentFilter,
)
from app.domains.tracking.analytics.domain.value_object.funnel_count import FunnelCount
from app.domains.tracking.analytics.domain.value_object.period import TimeRange


class FunnelRepository(ABC):
    @abstractmethod
    def count_distinct_sessions_by_stage(
        self,
        time_range: TimeRange,
        content_filter: ContentFilter,
    ) -> list[FunnelCount]:
        ...
