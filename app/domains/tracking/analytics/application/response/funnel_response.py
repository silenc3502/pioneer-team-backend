from pydantic import BaseModel


class FunnelStageItem(BaseModel):
    event_type: str
    count: int
    conversion_rate: float
    previous_count: int
    delta_rate: float | None


class FunnelResponse(BaseModel):
    stages: list[FunnelStageItem]
