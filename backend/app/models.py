from typing import List, Optional
from pydantic import BaseModel, Field


class SensorPoint(BaseModel):
    id: int
    temp: float
    rh: float
    status: str = "ok"


class DeviceReading(BaseModel):
    """Ứng với đúng cấu trúc file JSON mà thiết bị / người dùng gửi lên."""
    serial: str
    site: str
    ts: int  # unix timestamp (giây)
    sensors: List[SensorPoint]


class ReadingOut(DeviceReading):
    id: Optional[str] = Field(default=None, alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {}


class UploadResponse(BaseModel):
    inserted_id: str
    serial: str
    site: str
    ts: int
    datetime_vn: str
    sensor_count: int
