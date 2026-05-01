from pydantic import BaseModel


class FunnelStageItem(BaseModel):
    stage: str
    count: int


class FunnelResponse(BaseModel):
    stages: list[FunnelStageItem]
