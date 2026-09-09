"""
Mô phỏng thiết bị IoT gửi dữ liệu nhiệt độ/độ ẩm lên hệ thống để test.

Cách dùng cơ bản:
    python simulate_device.py

Cách dùng nâng cao (xem đầy đủ options):
    python simulate_device.py --help

Ví dụ:
    # Gửi 1 lần rồi thoát (test nhanh)
    python simulate_device.py --once

    # Gửi liên tục mỗi 10 giây, 8 cảm biến, chạy vô hạn tới khi Ctrl+C
    python simulate_device.py --interval 10 --sensors 8

    # Mô phỏng 3 thiết bị khác nhau chạy song song
    python simulate_device.py --devices 3 --interval 15

    # Tạo tình huống lỗi cảm biến ngẫu nhiên để test giao diện xử lý status != ok
    python simulate_device.py --error-rate 0.1
"""

import argparse
import random
import sys
import threading
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print("Thiếu thư viện 'requests'. Cài bằng lệnh: pip install requests")
    sys.exit(1)


# ----- Cấu hình giá trị nền cho từng cảm biến (dựa theo dữ liệu mẫu bạn đưa) -----
BASE_SENSORS = [
    {"id": 1, "temp": 31.2, "rh": 67.5},
    {"id": 2, "temp": 31.4, "rh": 68.1},
    {"id": 3, "temp": 30.9, "rh": 69.0},
    {"id": 4, "temp": 31.0, "rh": 68.6},
    {"id": 5, "temp": 30.8, "rh": 69.4},
    {"id": 6, "temp": 31.3, "rh": 67.9},
    {"id": 7, "temp": 31.1, "rh": 68.3},
    {"id": 8, "temp": 30.7, "rh": 69.8},
]

TEMP_MIN, TEMP_MAX = 18.0, 45.0
RH_MIN, RH_MAX = 30.0, 95.0


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class DeviceSimulator:
    """
    Mô phỏng 1 thiết bị: giữ trạng thái nhiệt độ/độ ẩm hiện tại của từng
    cảm biến, mỗi lần gọi `next_reading()` sẽ dao động ngẫu nhiên kiểu
    "random walk" quanh giá trị trước đó (giống cảm biến thật, không nhảy
    số đột ngột).
    """

    def __init__(self, serial: str, site: str, sensor_count: int, error_rate: float):
        self.serial = serial
        self.site = site
        self.error_rate = error_rate
        self.sensors = [
            {"id": s["id"], "temp": s["temp"], "rh": s["rh"]}
            for s in BASE_SENSORS[:sensor_count]
        ]

    def next_reading(self) -> dict:
        sensors_out = []
        for s in self.sensors:
            # Random walk: mỗi lần dao động nhẹ +/- một chút quanh giá trị cũ
            s["temp"] = clamp(s["temp"] + random.uniform(-0.4, 0.4), TEMP_MIN, TEMP_MAX)
            s["rh"] = clamp(s["rh"] + random.uniform(-0.8, 0.8), RH_MIN, RH_MAX)

            is_error = random.random() < self.error_rate
            sensors_out.append(
                {
                    "id": s["id"],
                    "temp": round(s["temp"], 1),
                    "rh": round(s["rh"], 1),
                    "status": "error" if is_error else "ok",
                }
            )

        return {
            "serial": self.serial,
            "site": self.site,
            "ts": int(time.time()),
            "sensors": sensors_out,
        }


def send_reading(url: str, payload: dict, timeout: float = 5.0) -> None:
    now = datetime.now().strftime("%H:%M:%S")
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            print(
                f"[{now}] OK  serial={data.get('serial')} "
                f"ts={data.get('ts')} datetime_vn={data.get('datetime_vn')} "
                f"sensors={data.get('sensor_count')}"
            )
        else:
            print(f"[{now}] LỖI HTTP {resp.status_code}: {resp.text[:300]}")
    except requests.exceptions.ConnectionError:
        print(f"[{now}] LỖI: Không kết nối được tới {url} — backend có đang chạy không?")
    except requests.exceptions.Timeout:
        print(f"[{now}] LỖI: Request timeout sau {timeout}s")
    except Exception as e:  # noqa: BLE001 - script test, in lỗi ra cho dễ debug
        print(f"[{now}] LỖI không xác định: {e}")


def run_device_loop(
    url: str,
    serial: str,
    site: str,
    sensor_count: int,
    interval: float,
    error_rate: float,
    once: bool,
    count: int | None,
):
    sim = DeviceSimulator(serial, site, sensor_count, error_rate)
    sent = 0

    while True:
        payload = sim.next_reading()
        send_reading(url, payload)
        sent += 1

        if once or (count is not None and sent >= count):
            break

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(
        description="Mô phỏng thiết bị IoT gửi dữ liệu nhiệt độ/độ ẩm lên API để test.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000/api/upload/json",
        help="Địa chỉ API nhận dữ liệu (mặc định: %(default)s)",
    )
    parser.add_argument(
        "--serial",
        default="CMC-AX1500-0001",
        help="Mã serial thiết bị gốc (nếu --devices > 1, các thiết bị sau sẽ tự tăng số cuối)",
    )
    parser.add_argument("--site", default="B1/K4/1-DK2.KV4", help="Vị trí lắp đặt")
    parser.add_argument(
        "--sensors", type=int, default=6, choices=range(1, 9), help="Số lượng cảm biến (1-8)"
    )
    parser.add_argument(
        "--interval", type=float, default=10.0, help="Khoảng cách giữa 2 lần gửi (giây)"
    )
    parser.add_argument(
        "--error-rate",
        type=float,
        default=0.0,
        help="Tỉ lệ (0.0 - 1.0) một cảm biến bị đánh dấu status=error ở mỗi lần gửi, để test xử lý lỗi",
    )
    parser.add_argument(
        "--once", action="store_true", help="Chỉ gửi 1 lần rồi thoát (bỏ qua --interval/--count)"
    )
    parser.add_argument(
        "--count", type=int, default=None, help="Số lần gửi rồi dừng (mặc định: chạy vô hạn)"
    )
    parser.add_argument(
        "--devices", type=int, default=1, help="Số lượng thiết bị mô phỏng chạy song song"
    )

    args = parser.parse_args()

    if args.devices <= 1:
        run_device_loop(
            args.url,
            args.serial,
            args.site,
            args.sensors,
            args.interval,
            args.error_rate,
            args.once,
            args.count,
        )
        return

    # Nhiều thiết bị: mỗi thiết bị 1 thread riêng, serial tự tăng số cuối
    # VD serial gốc CMC-AX1500-0001 -> 0002, 0003, ...
    threads = []
    for i in range(args.devices):
        prefix = args.serial[:-4] if len(args.serial) >= 4 else args.serial
        try:
            base_num = int(args.serial[-4:])
        except ValueError:
            base_num = 1
        device_serial = f"{prefix}{base_num + i:04d}"

        t = threading.Thread(
            target=run_device_loop,
            args=(
                args.url,
                device_serial,
                args.site,
                args.sensors,
                args.interval,
                args.error_rate,
                args.once,
                args.count,
            ),
            daemon=True,
        )
        threads.append(t)
        t.start()
        time.sleep(0.3)  # rải nhẹ để log không in chồng lên nhau ngay lúc đầu

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nĐã dừng mô phỏng (Ctrl+C).")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nĐã dừng mô phỏng (Ctrl+C).")
