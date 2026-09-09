import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { ReadingService } from '../../services/reading.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss'],
})
export class UploadComponent {
  @Output() uploaded = new EventEmitter<void>();

  selectedFile: File | null = null;
  isDragging = false;
  isUploading = false;
  message = '';
  isError = false;

  constructor(private readingService: ReadingService) {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave() {
    this.isDragging = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
    if (event.dataTransfer?.files?.length) {
      this.selectedFile = event.dataTransfer.files[0];
    }
  }

  upload() {
    if (!this.selectedFile) return;
    this.isUploading = true;
    this.message = '';

    this.readingService.uploadFile(this.selectedFile).subscribe({
      next: (res) => {
        this.isUploading = false;
        this.isError = false;
        this.message = `Đã lưu dữ liệu: ${res.serial} (${res.sensor_count} cảm biến)`;
        this.selectedFile = null;
        this.uploaded.emit();
      },
      error: (err) => {
        this.isUploading = false;
        this.isError = true;
        this.message = err?.error?.detail
          ? JSON.stringify(err.error.detail)
          : 'Upload thất bại. Kiểm tra lại file hoặc kết nối backend.';
      },
    });
  }
}
