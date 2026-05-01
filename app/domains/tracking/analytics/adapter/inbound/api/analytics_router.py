from collections.abc import Callable, Iterator

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.domains.tracking.analytics.adapter.outbound.persistence.sqlalchemy_funnel_repository import (
    SqlAlchemyFunnelRepository,
)
from app.domains.tracking.analytics.application.response.funnel_response import (
    FunnelResponse,
    FunnelStageItem,
)
from app.domains.tracking.analytics.application.usecase.get_funnel_metrics_usecase import (
    GetFunnelMetricsUseCase,
)


def create_analytics_router(
    session_dependency: Callable[[], Iterator[Session]],
    require_gate_token: Callable[[Request], None],
) -> APIRouter:
    router = APIRouter(
        prefix="/dashboard/analytics",
        tags=["analytics"],
        dependencies=[Depends(require_gate_token)],
    )

    @router.get(
        "/funnel",
        response_model=FunnelResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_funnel(
        session: Session = Depends(session_dependency),
    ) -> FunnelResponse:
        repository = SqlAlchemyFunnelRepository(session)
        usecase = GetFunnelMetricsUseCase(repository)
        metrics = usecase.execute()
        return FunnelResponse(
            stages=[
                FunnelStageItem(
                    event_type=metric.stage.value,
                    count=metric.distinct_sessions,
                    conversion_rate=metric.conversion_rate,
                )
                for metric in metrics
            ]
        )

    return router
