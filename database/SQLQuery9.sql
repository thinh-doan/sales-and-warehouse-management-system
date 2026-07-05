# Database - Hệ thống quản lý bán hàng và kho hàng

## 1. Mô tả
Thư mục này chứa các file SQL dùng để tạo, thiết lập ràng buộc, nhập dữ liệu mẫu và truy vấn cơ sở dữ liệu cho hệ thống quản lý bán hàng và kho hàng cho doanh nghiệp quy mô vừa kinh doanh đồ gia dụng.

## 2. Công cụ sử dụng
- Microsoft SQL Server
- SQL Server Management Studio 2022

## 3. Cấu trúc các file SQL

- 01_create_database.sql: Tạo cơ sở dữ liệu QL_BANHANG_KHOHANG.
- 02_create_table.sql: Tạo các bảng trong cơ sở dữ liệu.
- 03_primary_key.sql: Tạo ràng buộc khóa chính cho các bảng.
- 04_foreign_key.sql: Tạo ràng buộc khóa ngoại giữa các bảng.
- 05_unique.sql: Tạo ràng buộc UNIQUE cho các thuộc tính không được trùng.
- 06_check.sql: Tạo ràng buộc CHECK để kiểm soát dữ liệu hợp lệ.
- 07_insert_sample_data.sql: Nhập dữ liệu mẫu cho hệ thống.
- 08_queries.sql: Chứa các câu truy vấn dữ liệu phục vụ báo cáo.

## 4. Thứ tự chạy file

Khi cài đặt cơ sở dữ liệu trên SQL Server Management Studio, cần chạy các file theo đúng thứ tự sau:

1. 01_create_database.sql
2. 02_create_table.sql
3. 03_primary_key.sql
4. 04_foreign_key.sql
5. 05_unique.sql
6. 06_check.sql
7. 07_insert_sample_data.sql
8. 08_queries.sql

## 5. Lưu ý khi chạy

- Bảng Order được viết là [Order] vì ORDER là từ khóa trong SQL Server.
- Bảng Role được viết là [Role] để tránh lỗi cú pháp.
- Cần chạy file tạo database trước khi tạo bảng.
- Cần chạy file tạo bảng trước khi tạo khóa chính, khóa ngoại và các ràng buộc khác.
- Dữ liệu mẫu trong hệ thống được xây dựng theo bối cảnh doanh nghiệp kinh doanh đồ gia dụng.