from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.domains.tracking.analytics.application.port.funnel_repository import (
    FunnelRepository,
)
from app.domains.tracking.analytics.domain.value_object.funnel_count import FunnelCount
from app.domains.tracking.analytics.domain.value_object.funnel_stage import FunnelStage
from app.domains.tracking.ingestion.infrastructure.orm.tracking_event_orm import (
    TrackingEventORM,
)


class SqlAlchemyFunnelRepository(FunnelRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def count_distinct_sessions_by_stage(self) -> list[FunnelCount]:
        stage_values = [stage.value for stage in FunnelStage]
        statement = (
            select(
                TrackingEventORM.event_type,
                func.count(distinct(TrackingEventORM.session_id)).label("sessions"),
            )
            .where(TrackingEventORM.event_type.in_(stage_values))
            .group_by(TrackingEventORM.event_type)
        )
        rows = self._session.execute(statement).all()
        counts_by_stage: dict[str, int] = {row.event_type: int(row.sessions) for row in rows}
        return [
            FunnelCount(
                stage=stage,
                distinct_sessions=counts_by_stage.get(stage.value, 0),
            )
            for stage in FunnelStage
        ]
