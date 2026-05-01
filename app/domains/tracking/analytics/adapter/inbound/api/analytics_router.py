from collections.abc import Callable, Iterator

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
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
from app.domains.tracking.analytics.domain.service.period_resolver import (
    InvalidPeriodError,
    resolve_time_range,
)
from app.domains.tracking.analytics.domain.value_object.content_filter import (
    CONTENT_KEY_MAX_LENGTH,
    ContentFilter,
)
from app.domains.tracking.analytics.domain.value_object.period import PeriodOption


class StrictValidationRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], object]:
        original = super().get_route_handler()

        async def handler(request: Request) -> Response:
            try:
                return await original(request)
            except RequestValidationError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=exc.errors(),
                ) from exc

        return handler


def create_analytics_router(
    session_dependency: Callable[[], Iterator[Session]],
    require_gate_token: Callable[[Request], None],
    analytics_timezone: str,
) -> APIRouter:
    router = APIRouter(
        prefix="/dashboard/analytics",
        tags=["analytics"],
        dependencies=[Depends(require_gate_token)],
        route_class=StrictValidationRoute,
    )

    @router.get(
        "/funnel",
        response_model=FunnelResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_funnel(
        period: PeriodOption | None = Query(default=None),
        start: int | None = Query(default=None, ge=0),
        end: int | None = Query(default=None, ge=0),
        content_id: str | None = Query(
            default=None,
            min_length=1,
            max_length=CONTENT_KEY_MAX_LENGTH,
        ),
        session: Session = Depends(session_dependency),
    ) -> FunnelResponse:
        try:
            time_range = resolve_time_range(
                period=period,
                start_ms=start,
                end_ms=end,
                timezone_name=analytics_timezone,
            )
        except InvalidPeriodError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        try:
            content_filter = ContentFilter(prefix=content_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        repository = SqlAlchemyFunnelRepository(session)
        usecase = GetFunnelMetricsUseCase(repository)
        metrics = usecase.execute(time_range, content_filter)
        return FunnelResponse(
            stages=[
                FunnelStageItem(
                    event_type=metric.stage.value,
                    count=metric.distinct_sessions,
                    conversion_rate=metric.conversion_rate,
                    previous_count=metric.previous_distinct_sessions,
                    delta_rate=metric.delta_rate,
                )
                for metric in metrics
            ]
        )

    return router
