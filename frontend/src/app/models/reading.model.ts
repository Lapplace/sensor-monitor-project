export interface SensorPoint {
  id: number;
  temp: number;
  rh: number;
  status: string;
}

export interface DeviceReading {
  serial: string;
  site: string;
  ts: number; // unix timestamp (giây, UTC) - dùng để sort/query
  datetime_vn?: string; // giờ Việt Nam (UTC+7), backend tính sẵn - dùng để hiển thị
  sensors: SensorPoint[];
}

export interface SiteOption {
  serial: string;
  site: string;
}

export interface UploadResponse {
  inserted_id: string;
  serial: string;
  site: string;
  ts: number;
  sensor_count: number;
}
