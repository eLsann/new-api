from pydantic import BaseModel, Field

class RecognizeResponse(BaseModel):
    status: str
    device_id: str
    name: str | None = None
    distance: float | None = None
    event_type: str | None = None
    late: bool = False
    audio_text: str | None = None
    reason: str | None = None

class PolicyUpdate(BaseModel):
    timezone: str | None = None
    in_start_time: str | None = Field(default=None, description="HH:MM")
    late_after_time: str | None = Field(default=None, description="HH:MM")
    out_start_time: str | None = Field(default=None, description="HH:MM")
    retention_days: int | None = None