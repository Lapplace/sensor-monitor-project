from typing import List, Optional

from fastapi import APIRouter, Query

from app.database import readings_collection

router = APIRouter(prefix="/api/readings", tags=["readings"])


@router.get("/meta/sites")
async def list_sites():
    """Trả về danh sách (serial, site) duy nhất để hiển thị dropdown lọc."""
    pipeline = [
        {"$group": {"_id": {"serial": "$serial", "site": "$site"}}},
        {"$project": {"_id": 0, "serial": "$_id.serial", "site": "$_id.site"}},
        {"$sort": {"serial": 1}},
    ]
    cursor = readings_collection.aggregate(pipeline)
    return [doc async for doc in cursor]


@router.get("/latest")
async def get_latest(
    serial: Optional[str] = Query(None, description="Lọc theo mã serial thiết bị"),
    site: Optional[str] = Query(None, description="Lọc theo vị trí lắp đặt"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi gần nhất cần lấy"),
):
    """
    Trả về đúng `limit` bản ghi GẦN NHẤT (mặc định 10), sắp xếp theo thời
    gian TĂNG DẦN (để vẽ chart theo đúng chiều thời gian trái -> phải).
    """
    query: dict = {}
    if serial:
        query["serial"] = serial
    if site:
        query["site"] = site

    projection = {"_id": 0, "serial": 1, "site": 1, "ts": 1, "datetime_vn": 1, "sensors": 1}

    cursor = (
        readings_collection.find(query, projection)
        .sort("ts", -1)  # mới nhất trước
        .limit(limit)
    )

    docs: List[dict] = [doc async for doc in cursor]
    docs.reverse()  # đảo lại thành tăng dần theo thời gian cho chart
    return docs


@router.get("/timeseries")
async def get_timeseries(
    serial: Optional[str] = Query(None, description="Lọc theo mã serial thiết bị"),
    site: Optional[str] = Query(None, description="Lọc theo vị trí lắp đặt"),
    sensor_id: Optional[int] = Query(None, description="Lọc theo id cảm biến cụ thể"),
    ts_from: Optional[int] = Query(None, description="Unix timestamp bắt đầu"),
    ts_to: Optional[int] = Query(None, description="Unix timestamp kết thúc"),
    limit: int = Query(2000, le=20000),
):
    """
    Trả về dữ liệu dạng time-series để frontend vẽ chart.
    Mỗi phần tử: { ts, sensors: [{id, temp, rh, status}] }
    """
    query: dict = {}
    if serial:
        query["serial"] = serial
    if site:
        query["site"] = site
    if ts_from is not None or ts_to is not None:
        ts_filter = {}
        if ts_from is not None:
            ts_filter["$gte"] = ts_from
        if ts_to is not None:
            ts_filter["$lte"] = ts_to
        query["ts"] = ts_filter

    projection = {"_id": 0, "serial": 1, "site": 1, "ts": 1, "datetime_vn": 1, "sensors": 1}

    cursor = (
        readings_collection.find(query, projection)
        .sort("ts", 1)
        .limit(limit)
    )

    docs: List[dict] = [doc async for doc in cursor]

    if sensor_id is not None:
        for doc in docs:
            doc["sensors"] = [s for s in doc["sensors"] if s["id"] == sensor_id]

    return docs
