---NHẬP DỮ LIỆU BẢNG Customer
INSERT INTO Customer (CustomerID, CusPhone, CusEmail, CusAddress, CusCreatedDate, CusType)
VALUES
(1, '0901000001', 'khach1@gmail.com', N'Quận 1, TP.HCM', '2026-06-01', N'Cá nhân'),
(2, '0901000002', 'khach2@gmail.com', N'Quận 3, TP.HCM', '2026-06-02', N'Cá nhân'),
(3, '0901000003', 'khach3@gmail.com', N'Quận 7, TP.HCM', '2026-06-03', N'Cá nhân'),
(4, '0901000004', 'khach4@gmail.com', N'Thủ Đức, TP.HCM', '2026-06-04', N'Cá nhân'),
(5, '0901000005', 'khach5@gmail.com', N'Bình Tân, TP.HCM', '2026-06-05', N'Cá nhân'),
(6, '0902000001', 'ctyminhphat@gmail.com', N'Tân Bình, TP.HCM', '2026-06-06', N'Doanh nghiệp'),
(7, '0902000002', 'ctyanphu@gmail.com', N'Gò Vấp, TP.HCM', '2026-06-07', N'Doanh nghiệp'),
(8, '0902000003', 'ctygiahung@gmail.com', N'Quận 10, TP.HCM', '2026-06-08', N'Doanh nghiệp');
GO

---NHẬP DỮ LIỆU BẢNG Individual_Customer
INSERT INTO Individual_Customer (ICustomerID, FullName, CusDateOfBirth)
VALUES
(1, N'Nguyễn Văn An', '1998-03-12'),
(2, N'Lê Thị Bình', '1999-07-20'),
(3, N'Trần Minh Khang', '1995-11-05'),
(4, N'Phạm Hoàng Nam', '2000-01-15'),
(5, N'Võ Ngọc Lan', '1997-09-22');
GO

---NHẬP DỮ LIỆU BẢNG Business_Customer
INSERT INTO Business_Customer (BCustomerID, CompanyName, TaxCode)
VALUES
(6, N'Công ty Minh Phát', '0310000001'),
(7, N'Công ty An Phú', '0310000002'),
(8, N'Công ty Gia Hưng', '0310000003');
GO

---NHẬP DỮ LIỆU BẢNG Category
INSERT INTO Category (CategoryID, CategoryName, CategoryDescription)
VALUES
(1, N'Nồi cơm điện', N'Các loại nồi cơm điện gia dụng'),
(2, N'Máy xay sinh tố', N'Thiết bị xay thực phẩm gia đình'),
(3, N'Quạt điện', N'Các loại quạt điện gia dụng'),
(4, N'Bếp điện', N'Bếp từ, bếp điện dùng trong gia đình'),
(5, N'Ấm siêu tốc', N'Ấm đun nước nhanh'),
(6, N'Máy hút bụi', N'Thiết bị vệ sinh gia đình');
GO

---NHẬP DỮ LIỆU BẢNG Product
INSERT INTO Product (ProductID, ProductName, ProductUnitPrice, Unit, ProductDescription, ProductStatus, CategoryID)
VALUES
(1, N'Nồi cơm điện Sharp 1.8L', 1250000, N'Cái', N'Nồi cơm điện dung tích 1.8 lít', N'Đang bán', 1),
(2, N'Nồi cơm điện Toshiba 1L', 980000, N'Cái', N'Nồi cơm điện nhỏ dùng cho gia đình', N'Đang bán', 1),
(3, N'Máy xay sinh tố Panasonic', 850000, N'Cái', N'Máy xay sinh tố 2 cối', N'Đang bán', 2),
(4, N'Máy xay sinh tố Philips', 1200000, N'Cái', N'Máy xay công suất cao', N'Đang bán', 2),
(5, N'Quạt đứng Senko', 450000, N'Cái', N'Quạt đứng 3 tốc độ', N'Đang bán', 3),
(6, N'Quạt đứng Asia', 620000, N'Cái', N'Quạt đứng tiết kiệm điện', N'Đang bán', 3),
(7, N'Bếp từ đơn Sunhouse', 1350000, N'Cái', N'Bếp từ đơn cho gia đình', N'Đang bán', 4),
(8, N'Bếp điện Kangaroo', 1800000, N'Cái', N'Bếp điện hồng ngoại', N'Đang bán', 4),
(9, N'Ấm siêu tốc Philips', 650000, N'Cái', N'Ấm đun nước dung tích 1.7L', N'Đang bán', 5),
(10, N'Máy hút bụi Electrolux', 2450000, N'Cái', N'Máy hút bụi gia đình', N'Đang bán', 6);
GO

---NHẬP DỮ LIỆU BẢNG Warehouse
INSERT INTO Warehouse (WarehouseID, WarehouseName, Address, Capacity)
VALUES
(1, N'Kho Tân Bình', N'Tân Bình, TP.HCM', 5000),
(2, N'Kho Thủ Đức', N'Thủ Đức, TP.HCM', 7000),
(3, N'Kho Bình Tân', N'Bình Tân, TP.HCM', 6000);
GO

---NHẬP DỮ LIỆU BẢNG Inventory
INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated)
VALUES
(1, 1, 30, '2026-06-25'),
(1, 2, 18, '2026-06-25'),
(1, 3, 45, '2026-06-25'),
(1, 4, 12, '2026-06-25'),
(1, 5, 80, '2026-06-25'),
(2, 1, 25, '2026-06-25'),
(2, 3, 10, '2026-06-25'),
(2, 6, 35, '2026-06-25'),
(2, 7, 20, '2026-06-25'),
(2, 8, 8, '2026-06-25'),
(3, 2, 22, '2026-06-25'),
(3, 4, 16, '2026-06-25'),
(3, 5, 60, '2026-06-25'),
(3, 9, 14, '2026-06-25'),
(3, 10, 6, '2026-06-25');
GO

---NHẬP DỮ LIỆU BẢNG Employee
INSERT INTO Employee (EmployeeID, EmpName, EmpGender, EmpDateOfBirth, EmpPhone, EmpEmail, Department, Position, HireDate)
VALUES
(1, N'Nguyễn Hoàng Minh', N'Nam', '1992-05-10', '0911000001', 'minh@company.com', N'Quản trị', N'Quản lý hệ thống', '2024-01-10'),
(2, N'Lê Thanh Huyền', N'Nữ', '1996-08-12', '0911000002', 'huyen@company.com', N'Kinh doanh', N'Nhân viên xử lý đơn hàng', '2024-03-15'),
(3, N'Trần Quốc Bảo', N'Nam', '1995-02-18', '0911000003', 'bao@company.com', N'Kho vận', N'Nhân viên kho', '2024-04-01'),
(4, N'Phạm Anh Thư', N'Nữ', '1997-09-25', '0911000004', 'thu@company.com', N'Giao hàng', N'Điều phối giao hàng', '2024-05-20'),
(5, N'Võ Minh Đức', N'Nam', '1994-12-03', '0911000005', 'duc@company.com', N'Kế toán', N'Kế toán thanh toán', '2024-06-10'),
(6, N'Đặng Ngọc Mai', N'Nữ', '1998-04-09', '0911000006', 'mai@company.com', N'Chăm sóc khách hàng', N'Nhân viên CSKH', '2024-07-01');
GO

---NHẬP DỮ LIỆU BẢNG Role
INSERT INTO [Role] (RoleID, RoleName, RoleDescription)
VALUES
(1, N'Quản trị hệ thống', N'Quản lý toàn bộ hệ thống'),
(2, N'Nhân viên xử lý đơn hàng', N'Tạo và cập nhật đơn hàng'),
(3, N'Nhân viên kho', N'Quản lý sản phẩm và tồn kho'),
(4, N'Nhân viên điều phối giao hàng', N'Tạo và theo dõi shipment'),
(5, N'Kế toán', N'Quản lý thanh toán'),
(6, N'Chăm sóc khách hàng', N'Tra cứu đơn hàng và hỗ trợ khách hàng');
GO

---NHẬP DỮ LIỆU BẢNG Account
INSERT INTO Account (AccountID, Username, PasswordHash, AccountStatus, EmployeeID, RoleID)
VALUES
(1, 'admin', 'hash_admin_123', N'Đang hoạt động', 1, 1),
(2, 'order01', 'hash_order_123', N'Đang hoạt động', 2, 2),
(3, 'warehouse01', 'hash_warehouse_123', N'Đang hoạt động', 3, 3),
(4, 'ship01', 'hash_ship_123', N'Đang hoạt động', 4, 4),
(5, 'accountant01', 'hash_acc_123', N'Đang hoạt động', 5, 5),
(6, 'cskh01', 'hash_cskh_123', N'Đang hoạt động', 6, 6);
GO

---NHẬP DỮ LIỆU BẢNG Order
INSERT INTO [Order] (OrderID, OrderDate, TotalAmount, OrderStatus, ShippingAddress, CustomerID, EmployeeID)
VALUES
(1, '2026-06-10', 2100000, N'Hoàn thành', N'Quận 1, TP.HCM', 1, 2),
(2, '2026-06-11', 450000, N'Hoàn thành', N'Quận 3, TP.HCM', 2, 2),
(3, '2026-06-12', 1350000, N'Đang giao', N'Quận 7, TP.HCM', 3, 2),
(4, '2026-06-13', 1800000, N'Chờ xác nhận', N'Thủ Đức, TP.HCM', 4, 2),
(5, '2026-06-14', 1300000, N'Hoàn thành', N'Bình Tân, TP.HCM', 5, 2),
(6, '2026-06-15', 2450000, N'Đang xử lý', N'Tân Bình, TP.HCM', 6, 2),
(7, '2026-06-16', 980000, N'Đã hủy', N'Gò Vấp, TP.HCM', 7, 2),
(8, '2026-06-17', 1070000, N'Đang giao', N'Quận 10, TP.HCM', 8, 2),
(9, '2026-06-18', 2400000, N'Hoàn thành', N'Quận 1, TP.HCM', 1, 2),
(10, '2026-06-19', 650000, N'Chờ xác nhận', N'Quận 3, TP.HCM', 2, 2);
GO

---NHẬP DỮ LIỆU BẢNG Order_Detail
INSERT INTO Order_Detail (OrderID, ProductID, Quantity, OrderDetailUnitPrice)
VALUES
(1, 1, 1, 1250000),
(1, 3, 1, 850000),
(2, 5, 1, 450000),
(3, 7, 1, 1350000),
(4, 8, 1, 1800000),
(5, 9, 2, 650000),
(6, 10, 1, 2450000),
(7, 2, 1, 980000),
(8, 5, 1, 450000),
(8, 6, 1, 620000),
(9, 4, 2, 1200000),
(10, 9, 1, 650000);
GO

---NHẬP DỮ LIỆU BẢNG Delivery_Partner
INSERT INTO Delivery_Partner (PartnerID, PrtName, PrtPhone, PrtEmail, PrtAddress)
VALUES
(1, N'Giao Hàng Nhanh', '1900636677', 'contact@ghn.vn', N'TP.HCM'),
(2, N'Giao Hàng Tiết Kiệm', '19006092', 'contact@ghtk.vn', N'TP.HCM'),
(3, N'Viettel Post', '19008095', 'contact@viettelpost.vn', N'TP.HCM');
GO

---NHẬP DỮ LIỆU BẢNG Payment
INSERT INTO Payment (PaymentID, PaymentDate, Amount, PaymentMethod, PaymentStatus, OrderID)
VALUES
(1, '2026-06-10', 2100000, N'Chuyển khoản', N'Đã thanh toán', 1),
(2, '2026-06-11', 450000, N'Thanh toán khi nhận hàng', N'Đã thanh toán', 2),
(3, NULL, 1350000, N'Thanh toán khi nhận hàng', N'Chưa thanh toán', 3),
(4, NULL, 1800000, N'Chuyển khoản', N'Chưa thanh toán', 4),
(5, '2026-06-14', 1300000, N'Thanh toán điện tử', N'Đã thanh toán', 5),
(6, NULL, 2450000, N'Chuyển khoản', N'Chưa thanh toán', 6),
(7, NULL, 1070000, N'Thanh toán khi nhận hàng', N'Chưa thanh toán', 8),
(8, '2026-06-18', 2400000, N'Thanh toán điện tử', N'Đã thanh toán', 9),
(9, NULL, 650000, N'Chuyển khoản', N'Chưa thanh toán', 10);
GO

---NHẬP DỮ LIỆU BẢNG Shipment
INSERT INTO Shipment (ShipmentID, ShipmentDate, ExpectedDeliveryDate, ActualDeliveryDate, ShippingFee, ShipmentStatus, ShipmentMethod, OrderID, PartnerID, EmployeeID)
VALUES
(1, '2026-06-10', '2026-06-12', '2026-06-12', 30000, N'Giao thành công', N'Tiêu chuẩn', 1, 1, 4),
(2, '2026-06-11', '2026-06-13', '2026-06-13', 25000, N'Giao thành công', N'Tiêu chuẩn', 2, 2, 4),
(3, '2026-06-12', '2026-06-15', NULL, 35000, N'Đang vận chuyển', N'Tiêu chuẩn', 3, 1, 4),
(4, '2026-06-14', '2026-06-16', '2026-06-16', 28000, N'Giao thành công', N'Tiêu chuẩn', 5, 3, 4),
(5, '2026-06-15', '2026-06-18', NULL, 40000, N'Chờ lấy hàng', N'Tiêu chuẩn', 6, 2, 4),
(6, '2026-06-17', '2026-06-20', NULL, 32000, N'Đang vận chuyển', N'Tiêu chuẩn', 8, 1, 4),
(7, '2026-06-18', '2026-06-20', '2026-06-20', 30000, N'Giao thành công', N'Tiêu chuẩn', 9, 3, 4);
GO
