import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import ValidationError

from app.database import readings_collection
from app.models import DeviceReading, UploadResponse
from app.timeutils import now_vn_datetime_str, unix_ts_to_vn_datetime_str

router = APIRouter(prefix="/api/upload", tags=["upload"])


async def _save_reading(payload: dict) -> UploadResponse:
    try:
        reading = DeviceReading(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    doc = reading.model_dump()

    # ts: unix timestamp gốc do thiết bị gửi lên -> dùng để sort/query/vẽ chart
    # datetime_vn: cùng thời điểm đó nhưng đã quy đổi ra giờ Việt Nam (UTC+7) -> dùng để hiển thị
    datetime_vn = unix_ts_to_vn_datetime_str(reading.ts)
    doc["datetime_vn"] = datetime_vn

    # received_at: thời điểm THỰC TẾ server nhận được request (theo thời gian thực),
    # có thể khác với `ts` nếu thiết bị gửi trễ hoặc đồng hồ thiết bị bị lệch.
    doc["received_at"] = datetime.now(timezone.utc)
    doc["received_at_vn"] = now_vn_datetime_str()

    result = await readings_collection.insert_one(doc)

    return UploadResponse(
        inserted_id=str(result.inserted_id),
        serial=reading.serial,
        site=reading.site,
        ts=reading.ts,
        datetime_vn=datetime_vn,
        sensor_count=len(reading.sensors),
    )


@router.post("/file", response_model=UploadResponse)
async def upload_json_file(file: UploadFile = File(...)):
    """Nhận 1 file .json được upload từ trình duyệt và lưu vào MongoDB."""
    if not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file .json")

    raw = await file.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="File không phải JSON hợp lệ")

    return await _save_reading(payload)


@router.post("/json", response_model=UploadResponse)
async def upload_json_body(payload: DeviceReading):
    """Cho phép thiết bị/gateway gửi thẳng JSON body (application/json)."""
    return await _save_reading(payload.model_dump())
