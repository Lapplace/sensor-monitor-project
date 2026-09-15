# Tổng quan toàn bộ API Backend

| Method | Endpoint | Công dụng | Tham số | Trả về |
|---|---|---|---|---|
| `POST` | `/api/upload/file` | Nhận **file .json** upload qua form (multipart) | `file` (form-data) | `{inserted_id, serial, site, ts, datetime_vn, sensor_count}` |
| `POST` | `/api/upload/json` | Nhận **JSON body trực tiếp** — dùng cho thiết bị/gateway gửi tự động (không qua form) | JSON body đúng cấu trúc `{serial, site, ts, sensors[]}` | Giống trên |
| `GET` | `/api/readings/meta/sites` | Liệt kê danh sách **thiết bị duy nhất** đã từng gửi dữ liệu | không có | `[{serial, site}, ...]` |
| `GET` | `/api/readings/latest` | Lấy đúng **N bản ghi gần nhất** | `serial`, `site`, `limit` (mặc định 10) | Mảng bản ghi, sort tăng dần theo `ts` |
| `GET` | `/api/readings/timeseries` | Lấy dữ liệu theo **khoảng thời gian** tùy chọn | `serial`, `site`, `sensor_id`, `ts_from`, `ts_to`, `limit` | Mảng bản ghi trong khoảng đó |
| `GET` | `/api/readings/count` | **Đếm** số bản ghi khớp điều kiện (không kéo data về) — dùng chẩn đoán/cảnh báo trước khi export lớn | `serial`, `site`, `ts_from`, `ts_to` | `{count: number}` |
| `GET` | `/api/health` | Health check — kiểm tra server còn sống | không có | `{status: "ok"}` |

---

# Frontend — nút nào gọi API nào

## `DashboardComponent` (trang chính duy nhất hiện có)

| Hành động người dùng | Hàm được gọi | API gọi | Mục đích |
|---|---|---|---|
| **Mở trang lần đầu** (`ngOnInit`) | `loadSites()` | `GET /readings/meta/sites` | Đổ danh sách vào dropdown "Thiết bị" |
| | `loadData()` | `GET /readings/latest?limit=10` | Lấy 10 bản ghi gần nhất để vẽ chart lần đầu |
| | *(interval ngầm, không phải nút bấm)* | `GET /readings/latest?limit=10` | Cứ 10 giây tự gọi lại 1 lần để chart cập nhật realtime |
| **Chọn thiết bị khác** ở dropdown | `onSerialChange()` → `loadData()` | `GET /readings/latest?serial=X&limit=10` | Lọc chart theo đúng thiết bị vừa chọn |
| **Bấm "Làm mới"** | `refreshNow()` → `loadData()` | `GET /readings/latest?limit=10` | Chủ động ép tải lại ngay, không cần chờ 10s |
| **Bấm "Xuất Excel"** | `toggleExportPanel()` | *(không gọi API)* | Chỉ mở/đóng panel chọn chế độ xuất |
| ↳ Chọn tab **"Số bản ghi gần nhất"** rồi bấm "Xuất file" | `exportExcel()` (mode `latest`) | `GET /readings/latest?limit=<số bạn nhập>` | Lấy đúng N bản ghi gần nhất theo số tự nhập, **độc lập** với 10 bản ghi trên chart |
| ↳ Chọn tab **"Theo khoảng thời gian"** rồi bấm "Xuất file" | `exportExcel()` (mode `range`) | `GET /readings/timeseries?ts_from=...&ts_to=...` | Lấy toàn bộ bản ghi trong khoảng ngày giờ đã chọn |

## `ChartTempHumidComponent`

**Không tự gọi API nào cả** — nó chỉ nhận dữ liệu qua `@Input() readings` do `DashboardComponent` truyền vào sau khi gọi API xong, rồi vẽ 2 biểu đồ (nhiệt độ, độ ẩm) từ mảng đó.

## `UploadComponent`

File này **vẫn tồn tại trong code** (`components/upload/`), gọi `POST /upload/file` khi bấm nút "Tải lên" — nhưng **hiện KHÔNG còn được gắn vào giao diện** `DashboardComponent` nữa (đã gỡ bỏ theo yêu cầu "giao diện chỉ để xem biểu đồ" của bạn trước đó). Có thể coi đây là component dự phòng, sẵn sàng dùng lại nếu sau này bạn muốn có trang admin riêng để upload thủ công.

---

# Luồng dữ liệu tổng thể (ai gọi API nào để đưa dữ liệu vào hệ thống)

```
Thiết bị thật / script mô phỏng (simulate_device.py)
        │
        │  POST /api/upload/json   (JSON body trực tiếp)
        ▼
   Backend FastAPI  ──►  Validate (Pydantic)  ──►  Lưu vào MongoDB
                                                    (kèm datetime_vn, received_at_vn)
        ▲
        │  GET /readings/latest, /timeseries, /meta/sites, /count
        │
   Frontend Angular (Dashboard) ──► Vẽ chart / xuất Excel
```

Nói cách khác: **hướng vào** (ghi dữ liệu) chỉ có 1 đường qua `POST /upload/json` (do simulator hoặc thiết bị thật gọi) hoặc `POST /upload/file` (nếu dùng lại UploadComponent). **Hướng ra** (đọc dữ liệu để hiển thị) có 3 API: `meta/sites` (danh sách thiết bị), `latest` (chart + export theo số lượng), `timeseries` (export theo khoảng thời gian) + `count` (chẩn đoán/cảnh báo).# Tổng quan toàn bộ API Backend

| Method | Endpoint | Công dụng | Tham số | Trả về |
|---|---|---|---|---|
| `POST` | `/api/upload/file` | Nhận **file .json** upload qua form (multipart) | `file` (form-data) | `{inserted_id, serial, site, ts, datetime_vn, sensor_count}` |
| `POST` | `/api/upload/json` | Nhận **JSON body trực tiếp** — dùng cho thiết bị/gateway gửi tự động (không qua form) | JSON body đúng cấu trúc `{serial, site, ts, sensors[]}` | Giống trên |
| `GET` | `/api/readings/meta/sites` | Liệt kê danh sách **thiết bị duy nhất** đã từng gửi dữ liệu | không có | `[{serial, site}, ...]` |
| `GET` | `/api/readings/latest` | Lấy đúng **N bản ghi gần nhất** | `serial`, `site`, `limit` (mặc định 10) | Mảng bản ghi, sort tăng dần theo `ts` |
| `GET` | `/api/readings/timeseries` | Lấy dữ liệu theo **khoảng thời gian** tùy chọn | `serial`, `site`, `sensor_id`, `ts_from`, `ts_to`, `limit` | Mảng bản ghi trong khoảng đó |
| `GET` | `/api/readings/count` | **Đếm** số bản ghi khớp điều kiện (không kéo data về) — dùng chẩn đoán/cảnh báo trước khi export lớn | `serial`, `site`, `ts_from`, `ts_to` | `{count: number}` |
| `GET` | `/api/health` | Health check — kiểm tra server còn sống | không có | `{status: "ok"}` |

---

# Frontend — nút nào gọi API nào

## `DashboardComponent` (trang chính duy nhất hiện có)

| Hành động người dùng | Hàm được gọi | API gọi | Mục đích |
|---|---|---|---|
| **Mở trang lần đầu** (`ngOnInit`) | `loadSites()` | `GET /readings/meta/sites` | Đổ danh sách vào dropdown "Thiết bị" |
| | `loadData()` | `GET /readings/latest?limit=10` | Lấy 10 bản ghi gần nhất để vẽ chart lần đầu |
| | *(interval ngầm, không phải nút bấm)* | `GET /readings/latest?limit=10` | Cứ 10 giây tự gọi lại 1 lần để chart cập nhật realtime |
| **Chọn thiết bị khác** ở dropdown | `onSerialChange()` → `loadData()` | `GET /readings/latest?serial=X&limit=10` | Lọc chart theo đúng thiết bị vừa chọn |
| **Bấm "Làm mới"** | `refreshNow()` → `loadData()` | `GET /readings/latest?limit=10` | Chủ động ép tải lại ngay, không cần chờ 10s |
| **Bấm "Xuất Excel"** | `toggleExportPanel()` | *(không gọi API)* | Chỉ mở/đóng panel chọn chế độ xuất |
| ↳ Chọn tab **"Số bản ghi gần nhất"** rồi bấm "Xuất file" | `exportExcel()` (mode `latest`) | `GET /readings/latest?limit=<số bạn nhập>` | Lấy đúng N bản ghi gần nhất theo số tự nhập, **độc lập** với 10 bản ghi trên chart |
| ↳ Chọn tab **"Theo khoảng thời gian"** rồi bấm "Xuất file" | `exportExcel()` (mode `range`) | `GET /readings/timeseries?ts_from=...&ts_to=...` | Lấy toàn bộ bản ghi trong khoảng ngày giờ đã chọn |

## `ChartTempHumidComponent`

**Không tự gọi API nào cả** — nó chỉ nhận dữ liệu qua `@Input() readings` do `DashboardComponent` truyền vào sau khi gọi API xong, rồi vẽ 2 biểu đồ (nhiệt độ, độ ẩm) từ mảng đó.

## `UploadComponent`

File này **vẫn tồn tại trong code** (`components/upload/`), gọi `POST /upload/file` khi bấm nút "Tải lên" — nhưng **hiện KHÔNG còn được gắn vào giao diện** `DashboardComponent` nữa (đã gỡ bỏ theo yêu cầu "giao diện chỉ để xem biểu đồ" của bạn trước đó). Có thể coi đây là component dự phòng, sẵn sàng dùng lại nếu sau này bạn muốn có trang admin riêng để upload thủ công.

---

# Luồng dữ liệu tổng thể (ai gọi API nào để đưa dữ liệu vào hệ thống)

```
Thiết bị thật / script mô phỏng (simulate_device.py)
        │
        │  POST /api/upload/json   (JSON body trực tiếp)
        ▼
   Backend FastAPI  ──►  Validate (Pydantic)  ──►  Lưu vào MongoDB
                                                    (kèm datetime_vn, received_at_vn)
        ▲
        │  GET /readings/latest, /timeseries, /meta/sites, /count
        │
   Frontend Angular (Dashboard) ──► Vẽ chart / xuất Excel
```

Nói cách khác: **hướng vào** (ghi dữ liệu) chỉ có 1 đường qua `POST /upload/json` (do simulator hoặc thiết bị thật gọi) hoặc `POST /upload/file` (nếu dùng lại UploadComponent). **Hướng ra** (đọc dữ liệu để hiển thị) có 3 API: `meta/sites` (danh sách thiết bị), `latest` (chart + export theo số lượng), `timeseries` (export theo khoảng thời gian) + `count` (chẩn đoán/cảnh báo).
