# Sales and Warehouse Management System

Ứng dụng quản lý bán hàng và kho hàng được xây dựng bằng Python, PyQt6 và SQL Server. Dự án cung cấp giao diện desktop để quản lý các nghiệp vụ cốt lõi như đăng nhập, phân quyền, sản phẩm, khách hàng, đơn hàng, vận chuyển, thanh toán, tồn kho, nhân viên và báo cáo.

## Tính năng chính

- Đăng nhập và phân quyền theo vai trò người dùng.
- Dashboard tổng quan cho hoạt động hệ thống.
- Quản lý nhân viên, đối tác, khách hàng và danh mục.
- Quản lý sản phẩm, tồn kho và cập nhật thông tin chi tiết.
- Quản lý đơn hàng, chi tiết đơn, thanh toán và vận chuyển.
- Xem báo cáo nghiệp vụ theo dữ liệu trong hệ thống.

## Công nghệ sử dụng

- Python
- PyQt6
- SQL Server
- pyodbc

## Yêu cầu cài đặt

- Python 3.10 trở lên.
- SQL Server đang chạy cục bộ hoặc trên máy chủ có thể truy cập được.
- ODBC Driver 17 for SQL Server.
- Các thư viện Python được liệt kê trong `requirements.txt`.

## Cấu trúc dự án

- `main.py`: điểm khởi chạy ứng dụng.
- `connect.py`: lớp kết nối cơ sở dữ liệu.
- `modules/`: toàn bộ logic các màn hình và controller theo từng phân hệ.
- `ui/`: file giao diện `.ui` được tạo từ Qt Designer.
- `resources/`: stylesheet, biểu tượng và hình ảnh.
- `database/`: các script SQL tạo CSDL, bảng, ràng buộc, dữ liệu mẫu, truy vấn và trigger.

## Thiết lập cơ sở dữ liệu

Các script trong thư mục `database/` được sắp xếp theo thứ tự thực thi:

1. `01_create_database.sql`
2. `02_create_table.sql`
3. `03_primary_key.sql`
4. `04_foreign_key.sql`
5. `05_unique.sql`
6. `06_check.sql`
7. `07_insert_sample_data.sql`
8. `08_queries.sql`
9. `09_trigger.sql`

Tên cơ sở dữ liệu được ứng dụng sử dụng là `QL_BANHANG_KHOHANG`.

## Cài đặt và chạy ứng dụng

### 1. Tạo và kích hoạt môi trường ảo

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Cài thư viện cần thiết

```powershell
pip install -r requirements.txt
```

### 3. Tạo cơ sở dữ liệu

Mở SQL Server Management Studio hoặc công cụ SQL tương tự và chạy các file trong thư mục `database/` theo đúng thứ tự ở trên.

### 4. Chạy ứng dụng

```powershell
python main.py
```

## Ghi chú

- Ứng dụng tự nạp stylesheet từ `resources/styles.qss` khi khởi động.
- Trên Windows, chương trình tự cấu hình thư mục font hệ thống nếu phát hiện `C:\Windows\Fonts`.
- Nếu thay đổi cấu trúc database hoặc tên server, hãy cập nhật chuỗi kết nối trong `connect.py`.

## Cửa sổ đăng nhập
Tên tài khoản và Mật khẩu được lưu trong database/07_insert_sample_data.sql
## Màn hình chính

Sau khi đăng nhập thành công, ứng dụng mở cửa sổ chính và điều hướng đến các phân hệ thông qua thanh menu bên trái.

## Đóng góp

Nếu bạn muốn mở rộng README này, có thể bổ sung thêm ảnh chụp màn hình, hướng dẫn cấu hình dữ liệu mẫu, hoặc mô tả chi tiết từng phân hệ.