from pydantic import BaseModel


class FunnelStageItem(BaseModel):
    event_type: str
    count: int
    conversion_rate: float


class FunnelResponse(BaseModel):
    stages: list[FunnelStageItem]
