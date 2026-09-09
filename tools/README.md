# Mô phỏng thiết bị IoT (để test hệ thống)

Script `simulate_device.py` giả lập 1 (hoặc nhiều) thiết bị đo nhiệt độ/độ
ẩm, tự sinh dữ liệu dao động ngẫu nhiên quanh giá trị mẫu, gửi định kỳ lên
API `POST /api/upload/json` — dùng để test giao diện/backend mà không cần
thiết bị thật.

## 1. Cài đặt

Có thể dùng chung venv với backend, hoặc tạo venv riêng:

```powershell
cd tools
pip install -r requirements.txt
```

## 2. Chạy thử nhanh (gửi 1 lần rồi thoát)

```powershell
python simulate_device.py --once
```

Đảm bảo backend đang chạy ở `http://localhost:8000` trước khi chạy lệnh
này (xem log báo `OK` là gửi thành công).

## 3. Chạy mô phỏng liên tục

```powershell
python simulate_device.py --interval 10
```

Cứ 10 giây gửi 1 lần, chạy tới khi bạn nhấn `Ctrl+C` để dừng. Trong lúc
này mở giao diện web (`http://localhost:4200`), bấm "Làm mới" hoặc đợi
tự động refresh (15s) để thấy chart cập nhật.

## 4. Các tùy chọn hay dùng

| Option | Ý nghĩa | Mặc định |
|---|---|---|
| `--url` | Địa chỉ API nhận dữ liệu | `http://localhost:8000/api/upload/json` |
| `--serial` | Mã serial thiết bị | `CMC-AX1500-0001` |
| `--site` | Vị trí lắp đặt | `B1/K4/1-DK2.KV4` |
| `--sensors` | Số lượng cảm biến (1-8) | `6` |
| `--interval` | Khoảng cách giữa 2 lần gửi (giây) | `10` |
| `--count` | Gửi đúng N lần rồi dừng (mặc định chạy vô hạn) | không giới hạn |
| `--once` | Chỉ gửi 1 lần rồi thoát | tắt |
| `--error-rate` | Tỉ lệ (0.0–1.0) cảm biến bị đánh dấu `status=error` mỗi lần gửi, để test xử lý dữ liệu lỗi | `0.0` |
| `--devices` | Số thiết bị mô phỏng chạy song song (serial tự tăng số cuối) | `1` |

## 5. Ví dụ nâng cao

```powershell
# Mô phỏng 3 thiết bị khác nhau, mỗi thiết bị 8 cảm biến, gửi mỗi 5 giây
python simulate_device.py --devices 3 --sensors 8 --interval 5

# Test giao diện xử lý sensor lỗi: 15% khả năng 1 cảm biến báo status=error
python simulate_device.py --error-rate 0.15

# Gửi đúng 20 lần rồi tự dừng (dùng để tạo sẵn dữ liệu test)
python simulate_device.py --count 20 --interval 2
```

## 6. Lưu ý

- Script gửi qua `POST /api/upload/json` (JSON body trực tiếp), không phải
  `POST /api/upload/file` (upload file) — vì đây là cách thiết bị thật
  thường gửi dữ liệu tự động.
- Nếu backend báo lỗi kết nối, kiểm tra lại `--url` và đảm bảo `uvicorn`
  đang chạy.
- Dữ liệu random walk (dao động nhẹ quanh giá trị trước, không nhảy số đột
  ngột) để mô phỏng gần giống cảm biến thật hơn là số ngẫu nhiên hoàn toàn.
