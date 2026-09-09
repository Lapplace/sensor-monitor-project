# Sensor Temp/Humidity Monitor

Web app hiển thị biểu đồ nhiệt độ & độ ẩm theo thời gian từ dữ liệu cảm biến
được upload dạng file JSON (đúng cấu trúc bạn mô tả: `serial`, `site`, `ts`,
`sensors[]`).

- **Backend**: Python FastAPI + MongoDB (Motor async driver)
- **Frontend**: Angular (standalone components) + Chart.js (qua ng2-charts)

## 1. Cấu trúc dự án

```
backend/
  app/
    main.py            # khởi tạo FastAPI, CORS, include routers
    database.py         # kết nối MongoDB, tạo index
    models.py            # Pydantic schema khớp với file JSON của bạn
    routers/
      upload.py           # POST /api/upload/file, /api/upload/json
      readings.py          # GET /api/readings/timeseries, /meta/sites
  requirements.txt
  .env.example

frontend/
  src/
    app/
      models/reading.model.ts
      services/reading.service.ts       # gọi API backend
      components/
        upload/                          # form upload file .json
        chart-temp-humid/                # 2 biểu đồ line: nhiệt độ + độ ẩm
        dashboard/                        # gộp bộ lọc + upload + chart
      app.component.ts
      app.config.ts
    main.ts
  EXTRA_DEPENDENCIES.txt
```

## 2. Chạy Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # sửa MONGO_URI nếu MongoDB không chạy local
uvicorn app.main:app --reload --port 8000
```

Kiểm tra: mở `http://localhost:8000/docs` để thấy Swagger UI với 2 API chính:

- `POST /api/upload/file` – upload file `.json` (multipart/form-data)
- `GET /api/readings/timeseries` – lấy dữ liệu để vẽ chart, hỗ trợ filter
  theo `serial`, `site`, `sensor_id`, `ts_from`, `ts_to`

Bạn có thể test ngay bằng cách lưu đoạn JSON mẫu bạn gửi thành file
`sample.json` rồi upload qua Swagger UI hoặc qua giao diện web ở bước 3.

## 3. Chạy Frontend

Vì Angular cần scaffold đầy đủ (angular.json, tsconfig, polyfills...),
cách nhanh nhất là tạo project mới bằng CLI rồi copy các file trong
`frontend/src/app` vào:

```bash
npm install -g @angular/cli
ng new frontend --standalone --routing=false --style=scss
cd frontend
npm install chart.js ng2-charts chartjs-adapter-date-fns date-fns
```

Sau đó:
1. Copy toàn bộ thư mục `src/app/*` (đè lên project vừa tạo, giữ lại
   `app.component.ts` và `app.config.ts` đã cung cấp).
2. Copy `src/main.ts`.
3. Chạy:

```bash
ng serve
```

Mở `http://localhost:4200` — giao diện gồm:
- Ô upload file JSON (kéo thả hoặc chọn file)
- Bộ lọc theo thiết bị (serial) và khoảng thời gian
- 2 biểu đồ đường: Nhiệt độ (°C) và Độ ẩm (%) theo thời gian, mỗi cảm biến
  1 đường màu riêng, có thể bật/tắt từng cảm biến

**Lưu ý**: `reading.service.ts` đang trỏ tới
`http://localhost:8000/api` — sửa lại nếu bạn deploy backend ở địa chỉ khác.

## 4. Luồng dữ liệu

1. Người dùng chọn file `.json` (đúng format bạn đưa) → upload lên
   `POST /api/upload/file`.
2. Backend validate bằng Pydantic, lưu nguyên document vào MongoDB
   (collection `readings`), có thêm field `received_at`.
3. Frontend gọi `GET /api/readings/timeseries` để lấy danh sách các bản ghi
   theo thời gian, mỗi bản ghi có `ts` và mảng `sensors[]`.
4. Chart component tách dữ liệu theo từng `sensor.id`, vẽ 2 line chart
   (trục X là thời gian, trục Y là nhiệt độ / độ ẩm).

## 5. Mở rộng gợi ý (chưa làm trong bản này)

- Xác thực (JWT) cho API upload nếu public ra internet.
- WebSocket để cập nhật chart real-time khi có dữ liệu mới thay vì phải
  bấm "reload".
- Cron job/thiết bị gọi thẳng `POST /api/upload/json` để gửi dữ liệu định kỳ
  mà không cần upload file thủ công.
- Trang cảnh báo khi `status != "ok"` hoặc nhiệt độ/độ ẩm vượt ngưỡng.
