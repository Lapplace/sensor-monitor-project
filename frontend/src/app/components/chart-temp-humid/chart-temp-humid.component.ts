import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { ChartConfiguration, ChartData } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { DeviceReading } from '../../models/reading.model';

// Bảng màu cố định cho từng sensor id để đường vẽ nhất quán giữa các lần render
const COLORS = ['#2563eb', '#dc2626', '#16a34a', '#d97706', '#7c3aed', '#0891b2', '#db2777', '#65a30d'];

@Component({
  selector: 'app-chart-temp-humid',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './chart-temp-humid.component.html',
  styleUrls: ['./chart-temp-humid.component.scss'],
})
export class ChartTempHumidComponent implements OnChanges {
  @Input() readings: DeviceReading[] = [];

  sensorIds: number[] = [];
  activeSensorIds = new Set<number>();

  tempChartData: ChartData<'line'> = { labels: [], datasets: [] };
  rhChartData: ChartData<'line'> = { labels: [], datasets: [] };

  chartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    scales: {
      x: {
        // Dùng trục dạng category với nhãn là chuỗi giờ Việt Nam (UTC+7) do
        // backend tính sẵn (datetime_vn) -> luôn hiển thị đúng giờ VN, không
        // phụ thuộc múi giờ máy người xem.
        type: 'category',
        title: { display: true, text: 'Thời gian (giờ Việt Nam)' },
        ticks: { maxRotation: 45, minRotation: 0 },
      },
      y: { title: { display: true, text: '' } },
    },
    plugins: {
      legend: { position: 'bottom' },
    },
  };

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['readings']) {
      this.rebuildSensorList();
      this.rebuildDatasets();
    }
  }

  private rebuildSensorList() {
    const ids = new Set<number>();
    for (const r of this.readings) {
      for (const s of r.sensors) ids.add(s.id);
    }
    this.sensorIds = Array.from(ids).sort((a, b) => a - b);
    if (this.activeSensorIds.size === 0) {
      this.sensorIds.forEach((id) => this.activeSensorIds.add(id));
    }
  }

  toggleSensor(id: number) {
    if (this.activeSensorIds.has(id)) {
      this.activeSensorIds.delete(id);
    } else {
      this.activeSensorIds.add(id);
    }
    this.rebuildDatasets();
  }

  private labelFor(r: DeviceReading): string {
    // Ưu tiên datetime_vn do backend trả về; nếu bản ghi cũ chưa có field
    // này thì fallback sang convert phía trình duyệt.
    return r.datetime_vn ?? new Date(r.ts * 1000).toLocaleString('vi-VN');
  }

  private rebuildDatasets() {
    const labels = this.readings.map((r) => this.labelFor(r));

    const activeSensors = this.sensorIds.filter((id) => this.activeSensorIds.has(id));

    const tempDatasets = activeSensors.map((id, idx) => ({
      label: `Sensor ${id} - Nhiệt độ (°C)`,
      data: this.readings.map((r) => r.sensors.find((s) => s.id === id)?.temp ?? null),
      borderColor: COLORS[idx % COLORS.length],
      backgroundColor: COLORS[idx % COLORS.length],
      tension: 0.25,
      pointRadius: 3,
      spanGaps: true,
    }));

    const rhDatasets = activeSensors.map((id, idx) => ({
      label: `Sensor ${id} - Độ ẩm (%)`,
      data: this.readings.map((r) => r.sensors.find((s) => s.id === id)?.rh ?? null),
      borderColor: COLORS[idx % COLORS.length],
      backgroundColor: COLORS[idx % COLORS.length],
      tension: 0.25,
      pointRadius: 3,
      spanGaps: true,
    }));

    this.tempChartData = { labels, datasets: tempDatasets as any };
    this.rhChartData = { labels, datasets: rhDatasets as any };
  }
}
