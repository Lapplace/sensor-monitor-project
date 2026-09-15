import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import * as XLSX from 'xlsx';
import { DeviceReading, SiteOption } from '../../models/reading.model';
import { ReadingService } from '../../services/reading.service';
import { ChartTempHumidComponent } from '../chart-temp-humid/chart-temp-humid.component';

const LATEST_COUNT = 10; // số bản ghi hiển thị trên CHART

type ExportMode = 'latest' | 'range';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, ChartTempHumidComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  sites: SiteOption[] = [];
  selectedSerial = '';
  selectedSite = '';

  readings: DeviceReading[] = [];
  loading = false;

  // ----- Cấu hình riêng cho việc XUẤT EXCEL -----
  showExportPanel = false;
  exportMode: ExportMode = 'latest';
  exportLimit = 10;
  exportFrom = '';
  exportTo = '';
  exporting = false;
  exportError = '';

  constructor(
    private readingService: ReadingService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadSites();
    this.loadData();
  }

  loadSites() {
    this.readingService.getSites().subscribe((sites) => {
      this.sites = sites;
      this.cdr.detectChanges();
    });
  }

  onSerialChange() {
    const found = this.sites.find((s) => s.serial === this.selectedSerial);
    this.selectedSite = found?.site ?? '';
    this.loadData();
  }

  loadData() {
    this.loading = true;
    this.cdr.detectChanges(); // hiển thị ngay trạng thái "Đang tải..." trên nút

    this.readingService
      .getLatest({
        serial: this.selectedSerial || undefined,
        limit: LATEST_COUNT,
      })
      .subscribe({
        next: (data) => {
          this.readings = data;
          this.loading = false;
          this.cdr.detectChanges(); // ép render ngay khi có kết quả, không delay
        },
        error: (err) => {
          console.error('Lấy dữ liệu thất bại:', err);
          this.loading = false;
          this.cdr.detectChanges();
        },
      });
  }

  refreshNow() {
    this.loadData();
  }

  toggleExportPanel() {
    this.showExportPanel = !this.showExportPanel;
    this.exportError = '';
  }

  exportExcel() {
    this.exportError = '';

    if (this.exportMode === 'latest') {
      if (!this.exportLimit || this.exportLimit < 1) {
        this.exportError = 'Số bản ghi phải lớn hơn 0';
        return;
      }
      this.exporting = true;
      this.readingService
        .getLatest({
          serial: this.selectedSerial || undefined,
          limit: this.exportLimit,
        })
        .subscribe({
          next: (data) => {
            this.exporting = false;
            this.writeExcelFile(data, `${this.exportLimit}-ban-ghi-gan-nhat`);
            this.cdr.detectChanges();
          },
          error: () => {
            this.exporting = false;
            this.exportError = 'Lấy dữ liệu thất bại, thử lại sau.';
            this.cdr.detectChanges();
          },
        });
      return;
    }

    if (!this.exportFrom || !this.exportTo) {
      this.exportError = 'Vui lòng chọn đầy đủ thời gian bắt đầu và kết thúc';
      return;
    }
    const tsFrom = Math.floor(new Date(this.exportFrom).getTime() / 1000);
    const tsTo = Math.floor(new Date(this.exportTo).getTime() / 1000);
    if (tsFrom > tsTo) {
      this.exportError = 'Thời gian bắt đầu phải trước thời gian kết thúc';
      return;
    }

    this.exporting = true;
    this.readingService
      .getTimeseries({
        serial: this.selectedSerial || undefined,
        tsFrom,
        tsTo,
      })
      .subscribe({
        next: (data) => {
          this.exporting = false;
          if (!data.length) {
            this.exportError = 'Không có dữ liệu trong khoảng thời gian này';
            this.cdr.detectChanges();
            return;
          }
          this.writeExcelFile(data, 'theo-khoang-thoi-gian');
          this.cdr.detectChanges();
        },
        error: () => {
          this.exporting = false;
          this.exportError = 'Lấy dữ liệu thất bại, thử lại sau.';
          this.cdr.detectChanges();
        },
      });
  }

  private writeExcelFile(data: DeviceReading[], suffix: string) {
    if (!data.length) {
      this.exportError = 'Không có dữ liệu để xuất';
      return;
    }

    const rows: any[] = [];
    for (const r of data) {
      const timeLabel = r.datetime_vn ?? new Date(r.ts * 1000).toLocaleString('vi-VN');
      for (const s of r.sensors) {
        rows.push({
          'Thời gian (giờ VN)': timeLabel,
          'Unix timestamp': r.ts,
          Serial: r.serial,
          'Vị trí': r.site,
          'Sensor ID': s.id,
          'Nhiệt độ (°C)': s.temp,
          'Độ ẩm (%)': s.rh,
          'Trạng thái': s.status,
        });
      }
    }

    const worksheet = XLSX.utils.json_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Du lieu');

    const fileName = `nhietdo-doam-${this.selectedSerial || 'tatca'}-${suffix}-${Date.now()}.xlsx`;
    XLSX.writeFile(workbook, fileName);
    this.showExportPanel = false;
  }
}
