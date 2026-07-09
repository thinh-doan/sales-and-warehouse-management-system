use [QL_BANHANG_KHOHANG]

---NHẬP DỮ LIỆU BẢNG Customer
INSERT INTO Customer (CustomerID, CusName, CusPhone, CusEmail, CusAddress, CusCreatedDate, CusType)
VALUES
(1, N'Nguyễn Văn An', '0901000001', 'khach1@gmail.com', N'Quận 1, TP.HCM', '2026-06-01', N'Cá nhân'),
(2, N'Lê Thị Bình', '0901000002', 'khach2@gmail.com', N'Quận 3, TP.HCM', '2026-06-02', N'Cá nhân'),
(3, N'Trần Minh Khang', '0901000003', 'khach3@gmail.com', N'Quận 7, TP.HCM', '2026-06-03', N'Cá nhân'),
(4, N'Phạm Hoàng Nam', '0901000004', 'khach4@gmail.com', N'Thủ Đức, TP.HCM', '2026-06-04', N'Cá nhân'),
(5, N'Võ Ngọc Lan', '0901000005', 'khach5@gmail.com', N'Bình Tân, TP.HCM', '2026-06-05', N'Cá nhân'),
(6, N'Công ty Minh Phát', '0902000001', 'ctyminhphat@gmail.com', N'Tân Bình, TP.HCM', '2026-06-06', N'Doanh nghiệp'),
(7, N'Công ty An Phú', '0902000002', 'ctyanphu@gmail.com', N'Gò Vấp, TP.HCM', '2026-06-07', N'Doanh nghiệp'),
(8, N'Công ty Gia Hưng', '0902000003', 'ctygiahung@gmail.com', N'Quận 10, TP.HCM', '2026-06-08', N'Doanh nghiệp')
GO

---NHẬP DỮ LIỆU BẢNG Individual_Customer
INSERT INTO Individual_Customer (ICustomerID, Gender, CusDateOfBirth)
VALUES
(1, N'Nam', '1998-03-12'),
(2, N'Nữ', '1999-07-20'),
(3, N'Nam', '1995-11-05'),
(4, N'Nam', '2000-01-15'),
(5, N'Nữ', '1997-09-22');
GO

---NHẬP DỮ LIỆU BẢNG Business_Customer
INSERT INTO Business_Customer (BCustomerID, TaxCode)
VALUES
(6, '0310000001'),
(7, '0310000002'),
(8,'0310000003');
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
(2, N'Lê Thanh Huyền', N'Nữ', '1996-08-12', '0911000002', 'huyen@company.com', N'Kinh doanh', N'Nhân viên bán hàng', '2024-03-15'),
(3, N'Trần Quốc Bảo', N'Nam', '1995-02-18', '0911000003', 'bao@company.com', N'Kho vận', N'Nhân viên kho', '2024-04-01'),
(4, N'Phạm Anh Thư', N'Nữ', '1997-09-25', '0911000004', 'thu@company.com', N'Quản lý sản phẩm', N'Nhân viên quản lý sản phẩm', '2024-05-20'),
(5, N'Võ Minh Đức', N'Nam', '1994-12-03', '0911000005', 'duc@company.com', N'Kế toán', N'Kế toán thanh toán', '2024-06-10'),
(7, N'Trịnh Đình Quang', N'Nam', '1993-11-20', '0911000007', 'quang@company.com', N'Kho vận', N'Nhân viên kho', '2026-01-15'),
(8, N'Nguyễn Thu Thủy', N'Nữ', '1999-02-14', '0911000008', 'thuy@company.com', N'Kinh doanh', N'Nhân viên bán hàng', '2026-02-01');
GO

---NHẬP DỮ LIỆU BẢNG Role
INSERT INTO [Role] (RoleID, RoleName, RoleDescription)
VALUES
(1, N'Quản trị hệ thống', N'Quản lý toàn bộ hệ thống'),
(2, N'Nhân viên bán hàng', N'Tạo khách hàng và đơn hàng'),
(3, N'Nhân viên kho', N'Cập nhật trạng thái giao hàng và tồn kho '),
(4, N'Nhân viên quản lý sản phẩm', N'Tạo sản phẩm và tồn kho mới'),
(5, N'Kế toán', N'Quản lý thanh toán')
GO

---NHẬP DỮ LIỆU BẢNG Account
INSERT INTO Account (AccountID, Username, PasswordHash, AccountStatus, EmployeeID, RoleID)
VALUES
(1, 'admin', 'hash_admin_123', N'Đang hoạt động', 1, 1),
(2, 'sales01', 'hash_order_123', N'Đang hoạt động', 2, 2),
(3, 'warehouse01', 'hash_warehouse_123', N'Đang hoạt động', 3, 3),
(4, 'product01', 'hash_ship_123', N'Đang hoạt động', 4, 4),
(5, 'accountant01', 'hash_acc_123', N'Đang hoạt động', 5, 5),
(7, 'warehouse02', 'hash_warehouse_456', N'Đang hoạt động', 7, 3),
(8, 'sales02', 'hash_order_456', N'Đang hoạt động', 8, 2);
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

---NHẬP DỮ LIỆU BẢNG Prt_Shipping_Methods
INSERT INTO Prt_Shipping_Methods (PartnerID, ShippingMethodName)
VALUES
-- Đối tác 1
(1, N'Tiêu chuẩn'),
(1, N'Hỏa tốc'),

-- Đối tác 2
(2, N'Tiêu chuẩn'),
(2, N'Tiết kiệm'),

-- Đối tác 3 
(3, N'Tiêu chuẩn'),
(3, N'Tiết kiệm'),
(3, N'Hỏa tốc')
GO


---NHẬP DỮ LIỆU BẢNG Shipment
INSERT INTO Shipment (ShipmentID, ShipmentDate, ExpectedDeliveryDate, ActualDeliveryDate, ShippingFee, ShipmentStatus, ShipmentMethod, OrderID, PartnerID, EmployeeID)
VALUES
(1, '2026-06-10', Null, '2026-06-12', 30000, N'Giao thành công', N'Tiêu chuẩn', 1, 1, 4),
(2, '2026-06-11', Null, '2026-06-13', 25000, N'Giao thành công', N'Tiêu chuẩn', 2, 2, 4),
(3, '2026-06-12', Null, NULL, 35000, N'Đang vận chuyển', N'Tiêu chuẩn', 3, 1, 4),
(4, '2026-06-14', Null, '2026-06-16', 28000, N'Giao thành công', N'Tiêu chuẩn', 5, 3, 4),
(5, '2026-06-15', Null, NULL, 32000, N'Đang vận chuyển', N'Tiêu chuẩn', 8, 1, 4),
(7, '2026-06-18', Null, '2026-06-20', 30000, N'Giao thành công', N'Tiêu chuẩn', 9, 3, 4);
GO

INSERT INTO Prt_Shipping_Methods (PartnerID, ShippingMethodName)
VALUES
(1, N'Tiêu chuẩn'),
(1, N'Hỏa tốc'),
(1, N'Tiết kiệm'),
(2, N'Tiêu chuẩn'),
(2, N'Hỏa tốc'),
(3, N'Tiêu chuẩn'),
(3, N'Tiết kiệm')
Go

--------------------------BỔ SUNG SAMPLE------------------------------
--- 1. BỔ SUNG BẢNG CUSTOMER (ID từ 9 đến 14)
INSERT INTO Customer (CustomerID, CusName, CusPhone, CusEmail, CusAddress, CusCreatedDate, CusType)
VALUES
(9, N'Trần Thị Hoàng Yến', '0901000009', 'yen.tran@gmail.com', N'Quận 5, TP.HCM', '2026-06-20', N'Cá nhân'),
(10, N'Phan Văn Tài', '0901000010', 'tai.phan@gmail.com', N'Phú Nhuận, TP.HCM', '2026-06-21', N'Cá nhân'),
(11, N'Bùi Minh Tuấn', '0901000011', 'tuan.bui@gmail.com', N'Quận 11, TP.HCM', '2026-06-22', N'Cá nhân'),
(12, N'Công ty Bách Hóa Xanh', '0902000012', 'contact@bhx.com', N'Bình Thạnh, TP.HCM', '2026-06-23', N'Doanh nghiệp'),
(13, N'Tổng Công ty Việt Tiến', '0902000013', 'info@viettien.com.vn', N'Tân Phú, TP.HCM', '2026-06-24', N'Doanh nghiệp'),
(14, N'Công ty Điện máy Chợ Lớn', '0902000014', 'online@dmcl.com.vn', N'Quận 4, TP.HCM', '2026-06-25', N'Doanh nghiệp')
GO

--- 2. BỔ SUNG BẢNG INDIVIDUAL_CUSTOMER
INSERT INTO Individual_Customer (ICustomerID, Gender, CusDateOfBirth)
VALUES
(9, N'Nữ', '1993-10-15'),
(10, N'Nam', '1991-04-25'),
(11, N'Nam', '1988-12-30')
GO

--- 3. BỔ SUNG BẢNG BUSINESS_CUSTOMER
INSERT INTO Business_Customer (BCustomerID, TaxCode)
VALUES
(12, '0310000012'),
(13, '0310000013'),
(14, '0310000014')
GO

--- 4. BỔ SUNG BẢNG CATEGORY (Mở rộng thêm ngành hàng điện tử gia dụng)
INSERT INTO Category (CategoryID, CategoryName, CategoryDescription)
VALUES
(7, N'Lò vi sóng', N'Lò vi sóng, lò nướng thùng'),
(8, N'Máy lọc nước', N'Thiết bị lọc nước uống gia đình')
GO

--- 5. BỔ SUNG BẢNG PRODUCT (ID từ 11 đến 15)
INSERT INTO Product (ProductID, ProductName, ProductUnitPrice, Unit, ProductDescription, ProductStatus, CategoryID)
VALUES
(11, N'Lò vi sóng Sharp 20L', 1850000, N'Cái', N'Lò vi sóng có nướng cơ bản', N'Đang bán', 7),
(12, N'Lò vi sóng Panasonic 23L', 3200000, N'Cái', N'Lò vi sóng inverter tiết kiệm điện', N'Đang bán', 7),
(13, N'Máy lọc nước Karofi 9 lõi', 4800000, N'Cái', N'Máy lọc nước RO khoáng chất', N'Đang bán', 8),
(14, N'Máy lọc nước Sunhouse 10 lõi', 5200000, N'Cái', N'Máy lọc nước nóng lạnh RO', N'Đang bán', 8),
(15, N'Quạt lửng Asia A16001', 380000, N'Cái', N'Quạt lửng nhựa cao cấp', N'Ngừng bán', 3)
GO

--- 6. BỔ SUNG BẢNG WAREHOUSE
INSERT INTO Warehouse (WarehouseID, WarehouseName, Address, Capacity)
VALUES
(4, N'Kho Tổng Củ Chi', N'Củ Chi, TP.HCM', 15000)
GO

--- 7. BỔ SUNG BẢNG INVENTORY (Nạp tồn kho cho sản phẩm mới và kho mới)
INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated)
VALUES
(1, 11, 15, '2026-07-01'),
(1, 12, 8, '2026-07-01'),
(2, 13, 12, '2026-07-01'),
(3, 14, 10, '2026-07-01'),
(4, 1, 100, '2026-07-01'),
(4, 7, 50, '2026-07-01'),
(4, 11, 40, '2026-07-01'),
(4, 13, 30, '2026-07-01')
GO

--- 8. BỔ SUNG BẢNG EMPLOYEE (Nhân sự mới bổ sung cho Kho 4 và vận hành đơn)

--- 9. BỔ SUNG BẢNG ROLE (Không cần vì hệ thống phân quyền đã đủ 6 phòng ban)

--- 10. BỔ SUNG BẢNG ACCOUNT
INSERT INTO Account (AccountID, Username, PasswordHash, AccountStatus, EmployeeID, RoleID)
VALUES
(7, 'warehouse02', 'hash_warehouse_456', N'Đang hoạt động', 7, 3),
(8, 'order02', 'hash_order_456', N'Đang hoạt động', 8, 2)
GO

--- 11. BỔ SUNG BẢNG ORDER (Đơn hàng từ ID 11 đến 15)
INSERT INTO [Order] (OrderID, OrderDate, TotalAmount, OrderStatus, ShippingAddress, CustomerID, EmployeeID)
VALUES
(11, '2026-06-25', 1850000, N'Hoàn thành', N'Quận 5, TP.HCM', 9, 8),
(12, '2026-06-26', 9600000, N'Hoàn thành', N'Bình Thạnh, TP.HCM', 12, 8),
(13, '2026-06-27', 3200000, N'Đang xử lý', N'Phú Nhuận, TP.HCM', 10, 2),
(14, '2026-06-28', 5200000, N'Chờ xác nhận', N'Quận 4, TP.HCM', 14, 8),
(15, '2026-06-29', 2450000, N'Hoàn thành', N'Quận 11, TP.HCM', 11, 2)
GO

--- 12. BỔ SUNG BẢNG ORDER_DETAIL
INSERT INTO Order_Detail (OrderID, ProductID, Quantity, OrderDetailUnitPrice)
VALUES
(11, 11, 1, 1850000),
(12, 13, 2, 4800000), -- Tổng đơn 12: 9,600,000
(13, 12, 1, 3200000),
(14, 14, 1, 5200000),
(15, 10, 1, 2450000)
GO

--- 13. BỔ SUNG BẢNG PAYMENT
INSERT INTO Payment (PaymentID, PaymentDate, Amount, PaymentMethod, PaymentStatus, OrderID)
VALUES
(10, '2026-06-25', 1850000, N'Thanh toán điện tử', N'Đã thanh toán', 11),
(11, '2026-06-26', 9600000, N'Chuyển khoản', N'Đã thanh toán', 12),
(12, NULL, 3200000, N'Chuyển khoản', N'Chưa thanh toán', 13),
(13, '2026-06-29', 2450000, N'Thanh toán khi nhận hàng', N'Đã thanh toán', 15)
GO

--- 14. BỔ SUNG BẢNG DELIVERY_PARTNER
INSERT INTO Delivery_Partner (PartnerID, PrtName, PrtPhone, PrtEmail, PrtAddress)
VALUES
(4, N'Ninja Van', '19006118', 'support@ninjavan.co', N'TP.HCM')
GO

--- 15. BỔ SUNG BẢNG PRT_SHIPPING_METHODS (Thêm phương thức cho đối tác mới)
INSERT INTO Prt_Shipping_Methods (PartnerID, ShippingMethodName)
VALUES
(4, N'Tiêu chuẩn'),
(4, N'Hỏa tốc')
GO

--- 16. BỔ SUNG BẢNG SHIPMENT (ShipmentID từ 8 đến 11)
INSERT INTO Shipment (ShipmentID, ShipmentDate, ExpectedDeliveryDate, ActualDeliveryDate, ShippingFee, ShipmentStatus, ShipmentMethod, OrderID, PartnerID, EmployeeID)
VALUES
(8, '2026-06-25', Null, '2026-06-27', 22000, N'Giao thành công', N'Tiêu chuẩn', 11, 1, 4),
(9, '2026-06-26', Null, '2026-06-28', 0, N'Giao thành công', N'Tiêu chuẩn', 12, 4, 4), -- Đối tác 4 giao
(10, '2026-06-28', Null, NULL, 45000, N'Chờ lấy hàng', N'Tiêu chuẩn', 13, 2, 4),
(11, '2026-06-29', Null, '2026-07-01', 18000, N'Giao thành công', N'Hỏa tốc', 15, 4, 4)
GO

