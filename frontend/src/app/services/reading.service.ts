import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DeviceReading, SiteOption, UploadResponse } from '../models/reading.model';

@Injectable({ providedIn: 'root' })
export class ReadingService {
  // Đổi lại nếu backend chạy ở host/port khác
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  uploadFile(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResponse>(`${this.baseUrl}/upload/file`, formData);
  }

  getSites(): Observable<SiteOption[]> {
    return this.http.get<SiteOption[]>(`${this.baseUrl}/readings/meta/sites`);
  }

  getLatest(filters: { serial?: string; site?: string; limit?: number }): Observable<DeviceReading[]> {
    let params = new HttpParams();
    if (filters.serial) params = params.set('serial', filters.serial);
    if (filters.site) params = params.set('site', filters.site);
    params = params.set('limit', filters.limit ?? 10);

    return this.http.get<DeviceReading[]>(`${this.baseUrl}/readings/latest`, { params });
  }

  getTimeseries(filters: {
    serial?: string;
    site?: string;
    sensorId?: number;
    tsFrom?: number;
    tsTo?: number;
  }): Observable<DeviceReading[]> {
    let params = new HttpParams();
    if (filters.serial) params = params.set('serial', filters.serial);
    if (filters.site) params = params.set('site', filters.site);
    if (filters.sensorId != null) params = params.set('sensor_id', filters.sensorId);
    if (filters.tsFrom != null) params = params.set('ts_from', filters.tsFrom);
    if (filters.tsTo != null) params = params.set('ts_to', filters.tsTo);

    return this.http.get<DeviceReading[]>(`${this.baseUrl}/readings/timeseries`, { params });
  }
}
