<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align="center">
   XÂY DỰNG HỆ THỐNG PHÂN TÍCH ĐIỂM VÀ GỢI Ý LỘ TRÌNH HỌC
</h2>
<div align="center">
    <p align="center">
        <img src="docs/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="docs/fitdnu_logo.png" alt="FITDNU Logo" width="180"/>
        <img src="docs/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

## 💡 1. Giới thiệu về hệ thống

Ứng dụng "Hệ thống Quản lý Điểm Sinh viên" là một hệ thống quản lý học tập toàn diện, được phát triển để hỗ trợ quản lý thông tin sinh viên, môn học, điểm số và điểm danh một cách hiệu quả. Hệ thống được xây dựng với giao diện web hiện đại, cung cấp các tính năng phân tích, dự đoán và quản lý rủi ro học tập.

### 💻 Thành phần chính

#### **Backend Server**
- **Framework**: Flask (Python)
- **Database**: SQLite với SQLAlchemy ORM
- **API**: RESTful API cho tích hợp với các hệ thống khác
- **Xử lý dữ liệu**: Hỗ trợ import/export Excel
- **Phân tích**: Hệ thống phân tích học tập và quản lý rủi ro

#### **Frontend Web Interface**
- **Giao diện**: HTML/CSS/JavaScript với Flask Templates
- **Tính năng**:
  - Quản lý sinh viên (thêm, sửa, xóa, tìm kiếm)
  - Quản lý môn học và chương trình đào tạo
  - Nhập và xem điểm (theo sinh viên, môn học, học kỳ)
  - Điểm danh và thống kê chuyên cần
  - Phân tích học tập và dự đoán kết quả
  - Lộ trình học tập được đề xuất
  - Dashboard quản lý rủi ro học tập
  - Import/Export dữ liệu từ Excel

#### **Command Line Interface (CLI)**
- Giao diện dòng lệnh thân thiện
- Quản lý nhanh các thao tác cơ bản
- Phù hợp cho quản trị viên hệ thống

### 🌐 Kiến trúc & Công nghệ

- **Mô hình**: Client-Server với Web Application
- **Lý do chọn Flask**:
  - **Nhẹ và linh hoạt**: Framework Python nhẹ, dễ mở rộng
  - **ORM mạnh mẽ**: SQLAlchemy hỗ trợ quản lý database hiệu quả
  - **Template Engine**: Jinja2 cho giao diện động
  - **RESTful API**: Dễ dàng tích hợp với các hệ thống khác

### 💾 Lưu trữ dữ liệu

- **Database**: SQLite (`student_management.db`)
- **Cấu trúc**:
  - Bảng `students`: Thông tin sinh viên
  - Bảng `courses`: Thông tin môn học
  - Bảng `grades`: Điểm số (giữa kỳ, cuối kỳ, trung bình)
  - Bảng `attendance`: Điểm danh
  - Bảng `risk_alerts`: Cảnh báo rủi ro học tập
- **Tự động tính toán**: GPA, trạng thái điểm (Đạt/Không đạt), thống kê

### 📊 Tính năng chính

1. **Quản lý Sinh viên**
   - Thêm, sửa, xóa thông tin sinh viên
   - Xem danh sách và tìm kiếm
   - Import từ file Excel

2. **Quản lý Môn học**
   - Quản lý môn học và tín chỉ
   - Thiết lập môn học tiên quyết
   - Phân loại môn bắt buộc/tự chọn

3. **Quản lý Điểm**
   - Nhập điểm giữa kỳ và cuối kỳ
   - Tự động tính điểm trung bình và GPA
   - Xem điểm theo sinh viên, môn học, học kỳ
   - Import điểm từ Excel

4. **Điểm danh**
   - Điểm danh theo lớp và môn học
   - Thống kê tỷ lệ chuyên cần
   - Lịch sử điểm danh

5. **Phân tích & Dự đoán**
   - Phân tích kết quả học tập
   - Dự đoán GPA tương lai
   - Lộ trình học tập được đề xuất
   - Dashboard quản lý rủi ro

## 🔧 2. Công nghệ sử dụng

| Công nghệ | Phiên bản/Mô tả |
|-----------|----------------|
| **Ngôn ngữ** | Python 3.6+ |
| **Web Framework** | Flask 2.0+ |
| **Database** | SQLite với SQLAlchemy ORM |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Template Engine** | Jinja2 |
| **Xử lý dữ liệu** | Pandas (cho import Excel) |
| **Bảo mật** | bcrypt (mã hóa mật khẩu) |

## 📸 3. Hình ảnh các chức năng

### Giao diện Trang chủ
<img width="1912" height="610" alt="image" src="https://github.com/user-attachments/assets/d6d6e577-d37a-4a43-bc32-63ab84c7d41c" />

*[Hình ảnh trang chủ hệ thống]*

### Giao diện Quản lý Sinh viên
<img width="1900" height="926" alt="image" src="https://github.com/user-attachments/assets/0616d24f-37ac-4d90-81f0-2130255c950b" />

*[Hình ảnh danh sách sinh viên]*

### Giao diện Nhập Điểm
<img width="1904" height="792" alt="image" src="https://github.com/user-attachments/assets/d36b3f1b-1d57-46b6-b86b-06441c0680a1" />

*[Hình ảnh form nhập điểm]*

### Giao diện Phân tích Học tập
<img width="1422" height="901" alt="image" src="https://github.com/user-attachments/assets/8af73b9a-3636-43aa-adac-2889f02675a8" />

*[Hình ảnh dashboard phân tích]*

### Giao diện Lộ trình Học tập
<img width="1460" height="802" alt="image" src="https://github.com/user-attachments/assets/30be2cc4-7bea-469b-9a9d-7ffe1fc0a7ec" />

*[Hình ảnh lộ trình đề xuất]*


## ⚙️ 4. Các bước cài đặt & Chạy ứng dụng

### 🛠️ 4.1. Yêu cầu hệ thống

- **Python**: Phiên bản 3.6 trở lên (khuyến nghị Python 3.8+)
- **Hệ điều hành**: Windows, macOS, hoặc Linux
- **Bộ nhớ**: Tối thiểu 2GB RAM
- **Ổ cứng**: Tối thiểu 500MB dung lượng trống
- **Trình duyệt**: Chrome, Firefox, Edge (phiên bản mới nhất)

### 📥 4.2. Các bước cài đặt

#### 🧰 Bước 1: Chuẩn bị môi trường

**Cài đặt Python**

Dự án yêu cầu Python 3.6+ (Python 3.10+ được khuyến nghị).

Kiểm tra bằng lệnh:
```bash
python --version
# hoặc
python3 --version
```

Đảm bảo phiên bản >= 3.6.

**Cấu trúc thư mục dự án**
```
QuanLyDiemSinhVien/
├── src/
│   ├── models.py          # Định nghĩa database models
│   ├── managers.py        # Các class quản lý chức năng
│   ├── interface.py       # Giao diện CLI
│   ├── app.py             # Flask app chính
│   ├── analytics.py       # Phân tích học tập
│   ├── learning_path.py   # Lộ trình học tập
│   ├── risk_manager.py    # Quản lý rủi ro
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JS, images
├── web/
│   ├── app.py             # Web application
│   ├── templates/         # Web templates
│   └── static/            # Web static files
├── main.py                # Entry point CLI
├── requirements.txt       # Dependencies
└── README.md
```

#### 🏗️ Bước 2: Cài đặt dependencies

**Tạo môi trường ảo (khuyến nghị):**

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/Mac:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Cài đặt các thư viện cần thiết:**
```bash
pip install -r requirements.txt
```

Các thư viện chính sẽ được cài đặt:
- Flask >= 2.0
- SQLAlchemy == 2.0.23
- pandas (cho import Excel)
- bcrypt == 4.0.1
- tabulate == 0.9.0
- colorama == 0.4.6

#### ▶️ Bước 3: Khởi tạo Database

Database sẽ được tạo tự động khi chạy ứng dụng lần đầu. Nếu muốn tạo dữ liệu mẫu:

**Qua Web Interface:**
- Truy cập `/admin/seed` để tạo dữ liệu mẫu

**Qua CLI:**
- Chạy script khởi tạo (nếu có)

#### 🚀 Bước 4: Chạy ứng dụng

**Chạy Web Application:**

```bash
# Từ thư mục gốc
python web/app.py
# hoặc
cd web
python app.py
```

Ứng dụng sẽ chạy tại: `http://localhost:5000`

**Chạy CLI Application:**

```bash
python main.py
```

Sử dụng menu để điều hướng:
- Chọn 1 để quản lý sinh viên
- Chọn 2 để quản lý môn học
- Chọn 3 để quản lý điểm
- Chọn 4 để quản lý điểm danh
- Chọn 0 để thoát

## 🎮 Cách sử dụng

### Web Interface

1. **Truy cập hệ thống**: Mở trình duyệt và vào `http://localhost:5000`

2. **Quản lý Sinh viên**:
   - Xem danh sách: `/students`
   - Thêm mới: `/students/add`
   - Import Excel: Upload file từ trang danh sách

3. **Quản lý Môn học**:
   - Xem danh sách: `/courses`
   - Thêm mới: `/courses/add`
   - Import Excel: Upload file từ trang danh sách

4. **Quản lý Điểm**:
   - Xem tất cả điểm: `/grades`
   - Xem theo sinh viên: `/grades?student_id=<MSSV>`
   - Xem theo môn: `/grades?course_code=<MAMON>`
   - Thêm điểm: `/grades/add`
   - Import Excel: Upload file từ trang điểm

5. **Phân tích & Báo cáo**:
   - Phân tích sinh viên: `/students/<MSSV>/analysis`
   - Lộ trình học tập: `/students/<MSSV>/roadmap`
   - Dự đoán GPA: `/students/<MSSV>/forecast`
   - Dashboard rủi ro: `/analysis/risk`

### REST API

Hệ thống cung cấp REST API để tích hợp:

```bash
# Lấy danh sách sinh viên
GET /api/students

# Lấy thông tin chi tiết sinh viên
GET /api/students/<student_id>

# Lấy danh sách môn học
GET /api/courses

# Lấy điểm số
GET /api/grades?student_id=<MSSV>
GET /api/grades?course_code=<MAMON>
```

### Import/Export Excel

**Format file Excel cho Sinh viên:**
- Cột: `ma_sinh_vien`, `ho_ten`, `lop`, `chuyen_nganh`, `nam_nhap_hoc`

**Format file Excel cho Môn học:**
- Cột: `ma_mon_hoc`, `ten_mon_hoc`, `so_tin_chi`, `hoc_ky_de_xuat`, `bat_buoc`, `chuyen_nganh`, `mo_ta`

**Format file Excel cho Điểm:**
- Cột: `ma_sinh_vien`, `ma_mon_hoc`, `diem_giua_ky`, `diem_cuoi_ky`, `hoc_ky`, `nam_hoc`

## 📞 5. Liên hệ

**Nguyễn Hải Đăng**  
Lớp: CNTT 16-04  
Trường Đại học Đại Nam  
Email: Nguyenhaidangtb2004.tb@gmail.com  
GitHub: [Danganh1009](https://github.com/Danganh1009)


