from datetime import datetime, timezone
from zoneinfo import ZoneInfo

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def unix_ts_to_vn_datetime_str(ts: int) -> str:
    """
    Chuyển unix timestamp (giây, UTC) sang chuỗi giờ Việt Nam (UTC+7).
    Ví dụ: 1786556560 -> "10/09/2026 21:22:40"
    """
    dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
    dt_vn = dt_utc.astimezone(VN_TZ)
    return dt_vn.strftime("%d/%m/%Y %H:%M:%S")


def now_vn_datetime_str() -> str:
    """Thời điểm hiện tại (lúc server nhận request), theo giờ Việt Nam."""
    dt_vn = datetime.now(tz=timezone.utc).astimezone(VN_TZ)
    return dt_vn.strftime("%d/%m/%Y %H:%M:%S")
