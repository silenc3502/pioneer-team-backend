from datetime import datetime, time
from zoneinfo import ZoneInfo

from app.domains.tracking.analytics.domain.value_object.period import (
    PeriodOption,
    TimeRange,
)


class InvalidPeriodError(Exception):
    pass


_DAY_MS = 86_400_000


def resolve_time_range(
    period: PeriodOption | None,
    start_ms: int | None,
    end_ms: int | None,
    timezone_name: str,
    *,
    now_ms: int | None = None,
) -> TimeRange:
    has_period = period is not None
    has_custom = start_ms is not None or end_ms is not None

    if has_period and has_custom:
        raise InvalidPeriodError(
            "period와 start/end는 함께 지정할 수 없습니다."
        )

    if has_custom:
        if start_ms is None or end_ms is None:
            raise InvalidPeriodError("start와 end는 둘 다 필요합니다.")
        try:
            return TimeRange(start_ms=start_ms, end_ms=end_ms)
        except ValueError as exc:
            raise InvalidPeriodError(str(exc)) from exc

    option = period or PeriodOption.LAST_30_DAYS
    try:
        tz = ZoneInfo(timezone_name)
    except Exception as exc:
        raise InvalidPeriodError(f"알 수 없는 timezone: {timezone_name}") from exc

    now = (
        datetime.fromtimestamp(now_ms / 1000, tz=tz)
        if now_ms is not None
        else datetime.now(tz=tz)
    )
    end_resolved_ms = int(now.timestamp() * 1000)

    if option == PeriodOption.TODAY:
        midnight = datetime.combine(now.date(), time.min, tzinfo=tz)
        start_resolved_ms = int(midnight.timestamp() * 1000)
    elif option == PeriodOption.LAST_7_DAYS:
        start_resolved_ms = end_resolved_ms - 7 * _DAY_MS
    elif option == PeriodOption.LAST_30_DAYS:
        start_resolved_ms = end_resolved_ms - 30 * _DAY_MS
    else:
        raise InvalidPeriodError(f"알 수 없는 기간 옵션: {option}")

    return TimeRange(start_ms=start_resolved_ms, end_ms=end_resolved_ms)
