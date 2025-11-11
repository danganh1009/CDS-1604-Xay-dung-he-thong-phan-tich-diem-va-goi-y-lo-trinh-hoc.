# Hệ thống Quản lý Điểm Sinh viên

Đây là một ứng dụng Python đơn giản để quản lý điểm sinh viên, cho phép người dùng thực hiện các thao tác cơ bản như thêm, xem, cập nhật và xóa thông tin sinh viên, môn học và điểm số.

## Tính năng

- Quản lý sinh viên (thêm, xem, cập nhật, xóa)
- Quản lý môn học (thêm, xem)
- Quản lý điểm số (nhập điểm, xem điểm theo sinh viên/môn học)
- Giao diện dòng lệnh thân thiện với người dùng
- Lưu trữ dữ liệu bằng SQLite

## Yêu cầu hệ thống

- Python 3.6 trở lên
- Các thư viện Python được liệt kê trong file requirements.txt

## Cài đặt

1. Clone repository này về máy của bạn
2. Tạo môi trường ảo Python (khuyến nghị):
```
python -m venv .venv
```

3. Kích hoạt môi trường ảo:
- Windows:
```
.venv\Scripts\activate
```
- Linux/Mac:
```
source .venv/bin/activate
```

4. Cài đặt các thư viện cần thiết:
```
pip install -r requirements.txt
```

## Sử dụng

1. Chạy chương trình:
```
python main.py
```

2. Sử dụng menu để điều hướng:
- Chọn 1 để quản lý sinh viên
- Chọn 2 để quản lý môn học
- Chọn 3 để quản lý điểm
- Chọn 0 để thoát

## Cấu trúc dự án

- `main.py`: File chính để chạy chương trình
- `src/`
  - `models.py`: Định nghĩa các model database
  - `managers.py`: Các class quản lý chức năng
  - `interface.py`: Giao diện người dùng
- `requirements.txt`: Danh sách các thư viện cần thiết
- `student_management.db`: File database SQLite (sẽ được tạo tự động)

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Hãy tạo issue hoặc pull request nếu bạn muốn cải thiện dự án.

## Giấy phép

[MIT License](https://opensource.org/licenses/MIT)