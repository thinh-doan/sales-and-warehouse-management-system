USE QL_BANHANG_KHOHANG;
GO

/* =========================================================
   08_QUERIES.SQL
   Hệ thống quản lý bán hàng và kho hàng cho doanh nghiệp quy mô vừa
   Mảng dữ liệu mẫu: đồ gia dụng
   Ghi chú:
   - Bảng Order được viết là [Order] vì ORDER là từ khóa trong SQL Server.
   - Bảng Role được viết là [Role] để tránh lỗi cú pháp.
========================================================= */


/* 1. Nhân viên chăm sóc khách hàng cần xem danh sách khách hàng trong hệ thống để hỗ trợ tra cứu thông tin liên hệ.
   Thông tin gồm: CustomerID, CusName, CusPhone, CusEmail, CusAddress, CusType. */
SELECT CustomerID, CusName, CusPhone, CusEmail, CusAddress, CusType
FROM Customer;
GO

/* 2. Nhân viên chăm sóc khách hàng cần liệt kê danh sách khách hàng cá nhân để phục vụ chăm sóc khách hàng.
   Thông tin gồm: CustomerID, Cusname, CusDateOfBirth, CusPhone, CusEmail, CusAddress. */
SELECT c.CustomerID, c.CusName, i.CusDateOfBirth, c.CusPhone, c.CusEmail, c.CusAddress
FROM Customer c JOIN Individual_Customer i ON c.CustomerID = i.ICustomerID;
GO

/* 3. Nhân viên kinh doanh cần liệt kê danh sách khách hàng doanh nghiệp để phục vụ giao dịch số lượng lớn.
   Thông tin gồm: CustomerID, CusName, TaxCode, CusPhone, CusEmail, CusAddress. */
SELECT c.CustomerID, c.CusName, b.TaxCode, c.CusPhone, c.CusEmail, c.CusAddress
FROM Customer c JOIN Business_Customer b ON c.CustomerID = b.BCustomerID;
GO

/* 4. Nhân viên chăm sóc khách hàng cần tìm khách hàng theo số điện thoại để hỗ trợ tra cứu nhanh.
   Thông tin gồm: CustomerID, CusPhone, CusEmail, CusAddress, CusType. */
SELECT CustomerID, CusPhone, CusEmail, CusAddress, CusType
FROM Customer
WHERE CusPhone = '0901000001';
GO

/* 5. Nhân viên bán hàng cần xem danh sách sản phẩm theo danh mục để tư vấn cho khách hàng.
   Thông tin gồm: ProductID, ProductName, CategoryName, ProductUnitPrice, ProductStatus. */
SELECT p.ProductID, p.ProductName, c.CategoryName, p.ProductUnitPrice, p.ProductStatus
FROM Product p JOIN Category c ON p.CategoryID = c.CategoryID
ORDER BY c.CategoryName, p.ProductName
GO

/* 6. Nhân viên bán hàng cần liệt kê các sản phẩm có giá từ 1.000.000 trở lên để tư vấn nhóm hàng có giá trị cao.
   Thông tin gồm: ProductID, ProductName, ProductUnitPrice, ProductStatus. */
SELECT ProductID, ProductName, ProductUnitPrice, ProductStatus
FROM Product
WHERE ProductUnitPrice >= 1000000
ORDER BY ProductUnitPrice;
GO

/* 7. Nhân viên kho cần kiểm tra tồn kho của từng sản phẩm tại từng kho để phục vụ xử lý đơn hàng.
   Thông tin gồm: WarehouseName, ProductName, QuantityInStock, LastUpdated. */
SELECT w.WarehouseName, p.ProductName, i.QuantityInStock, i.LastUpdated
FROM Inventory i JOIN Warehouse w ON i.WarehouseID = w.WarehouseID
                 JOIN Product p ON i.ProductID = p.ProductID
ORDER BY w.WarehouseName, p.ProductName;
GO

/* 8. Nhân viên kho cần tính tổng tồn kho của từng sản phẩm trên toàn bộ hệ thống kho.
   Thông tin gồm: ProductID, ProductName, TongTonKho. */
SELECT p.ProductID, p.ProductName, TongTonKho = SUM(i.QuantityInStock)
FROM Product p JOIN Inventory i ON p.ProductID = i.ProductID
GROUP BY p.ProductID, p.ProductName;
GO

/* 9. Quản lý cần tìm danh sách các mặt hàng đang có sẵn trong kho nhưng chưa từng bán được sản phẩm nào để lên kế hoạch xả kho.
   Thông tin gồm: ProductID, ProductName, CategoryName, TongTonKho. */
SELECT p.ProductID, p.ProductName, c.CategoryName, TongTonKho = SUM(i.QuantityInStock)
FROM Product p JOIN Category c ON p.CategoryID = c.CategoryID
               JOIN Inventory i ON p.ProductID = i.ProductID
               LEFT JOIN Order_Detail od ON p.ProductID = od.ProductID
WHERE od.ProductID IS NULL
GROUP BY p.ProductID, p.ProductName, c.CategoryName
HAVING SUM(i.QuantityInStock) > 0;
GO

/* 10. Nhân viên kho cần phân loại tình trạng tồn kho của từng sản phẩm để ưu tiên nhập hàng.
   Thông tin gồm: ProductID, ProductName, TongTonKho, TinhTrangTonKho. */
SELECT p.ProductID, p.ProductName, TongTonKho = SUM(i.QuantityInStock),
       TinhTrangTonKho = CASE
           WHEN SUM(i.QuantityInStock) = 0 THEN N'Hết hàng'
           WHEN SUM(i.QuantityInStock) < 20 THEN N'Sắp hết'
           ELSE N'Còn hàng'
       END
FROM Product p JOIN Inventory i ON p.ProductID = i.ProductID
GROUP BY p.ProductID, p.ProductName;
GO

/* 11. Quản lý cần thống kê số lượng sản phẩm theo từng danh mục để đánh giá cơ cấu hàng hóa.
   Thông tin gồm: CategoryID, CategoryName, SoLuongSanPham. */
SELECT c.CategoryID, c.CategoryName, SoLuongSanPham = COUNT(p.ProductID)
FROM Category c LEFT JOIN Product p ON c.CategoryID = p.CategoryID
GROUP BY c.CategoryID, c.CategoryName;
GO

/* 12. Nhân viên kho cần tính tổng số lượng hàng tồn trong từng kho để đánh giá sức chứa và lượng hàng hiện có.
   Thông tin gồm: WarehouseID, WarehouseName, TongSoLuongTon. */
SELECT w.WarehouseID, w.WarehouseName, TongSoLuongTon = SUM(i.QuantityInStock)
FROM Warehouse w JOIN Inventory i ON w.WarehouseID = i.WarehouseID
GROUP BY w.WarehouseID, w.WarehouseName;
GO

/* 13. Nhân viên xử lý đơn hàng cần liệt kê danh sách đơn hàng kèm thông tin khách hàng để theo dõi tình trạng xử lý.
   Thông tin gồm: OrderID, OrderDate, CustomerID, CusPhone, TotalAmount, OrderStatus. */
SELECT o.OrderID, o.OrderDate, c.CustomerID, c.CusPhone, o.TotalAmount, o.OrderStatus
FROM [Order] o JOIN Customer c ON o.CustomerID = c.CustomerID
ORDER BY o.OrderDate;
GO

/* 14. Quản lý cần xem danh sách đơn hàng kèm nhân viên phụ trách để đánh giá khối lượng xử lý đơn.
   Thông tin gồm: OrderID, OrderDate, EmpName, TotalAmount, OrderStatus. */
SELECT o.OrderID, o.OrderDate, e.EmpName, o.TotalAmount, o.OrderStatus
FROM [Order] o JOIN Employee e ON o.EmployeeID = e.EmployeeID
ORDER BY o.OrderDate;
GO

/* 15. Nhân viên bán hàng cần xem chi tiết một đơn hàng cụ thể để kiểm tra các sản phẩm khách đã đặt.
   Thông tin gồm: OrderID, ProductName, Quantity, OrderDetailUnitPrice, ThanhTien. */
SELECT o.OrderID, p.ProductName, od.Quantity, od.OrderDetailUnitPrice,
       ThanhTien = od.Quantity * od.OrderDetailUnitPrice
FROM [Order] o JOIN Order_Detail od ON o.OrderID = od.OrderID
               JOIN Product p ON od.ProductID = p.ProductID
WHERE o.OrderID = 1;
GO

/* 16. Quản lý cần thống kê số lượng đơn hàng theo từng trạng thái để theo dõi tiến độ xử lý.
   Thông tin gồm: OrderStatus, SoLuongDonHang. */
SELECT OrderStatus, SoLuongDonHang = COUNT(OrderID)
FROM [Order]
GROUP BY OrderStatus;
GO

/* 17. Quản lý cần liệt kê các đơn hàng có tổng tiền trên 1.000.000 để theo dõi các đơn hàng có giá trị cao.
   Thông tin gồm: OrderID, OrderDate, TotalAmount, OrderStatus. */
SELECT OrderID, OrderDate, TotalAmount, OrderStatus
FROM [Order]
WHERE TotalAmount > 1000000;
GO

/* 18. Nhân viên xử lý đơn hàng cần liệt kê các đơn hàng đã hủy để kiểm tra tình trạng đơn không hoàn tất.
   Thông tin gồm: OrderID, OrderDate, TotalAmount, OrderStatus. */
SELECT OrderID, OrderDate, TotalAmount, OrderStatus
FROM [Order]
WHERE OrderStatus = N'Đã hủy';
GO

/* 19. Kế toán cần liệt kê danh sách thanh toán của các đơn hàng để phục vụ đối soát.
   Thông tin gồm: PaymentID, OrderID, OrderDate, Amount, PaymentMethod, PaymentStatus. */
SELECT p.PaymentID, o.OrderID, o.OrderDate, p.Amount, p.PaymentMethod, p.PaymentStatus
FROM Payment p JOIN [Order] o ON p.OrderID = o.OrderID
ORDER BY p.PaymentID;
GO

/* 20. Kế toán cần liệt kê các đơn hàng chưa thanh toán để tiếp tục theo dõi công nợ.
   Thông tin gồm: OrderID, OrderDate, TotalAmount, PaymentStatus. */
SELECT o.OrderID, o.OrderDate, o.TotalAmount, p.PaymentStatus
FROM [Order] o LEFT JOIN Payment p ON o.OrderID = p.OrderID
WHERE p.PaymentStatus = N'Chưa thanh toán' OR p.PaymentID IS NULL;
GO

/* 21. Kế toán cần tính tổng doanh thu từ các đơn hàng đã thanh toán.
   Thông tin gồm: TongDoanhThu. */
SELECT TongDoanhThu = SUM(Amount)
FROM Payment
WHERE PaymentStatus = N'Đã thanh toán';
GO

/* 22. Kế toán cần thống kê doanh thu theo từng phương thức thanh toán để đánh giá xu hướng thanh toán của khách hàng.
   Thông tin gồm: PaymentMethod, TongTien. */
SELECT PaymentMethod, TongTien = SUM(Amount)
FROM Payment
WHERE PaymentStatus = N'Đã thanh toán'
GROUP BY PaymentMethod;
GO

/* 23. Kế toán cần thống kê số lượng thanh toán theo từng trạng thái để kiểm tra tình hình thu tiền.
   Thông tin gồm: PaymentStatus, SoLuong. */
SELECT PaymentStatus, SoLuong = COUNT(PaymentID)
FROM Payment
GROUP BY PaymentStatus;
GO

/* 24. Nhân viên điều phối giao hàng cần liệt kê danh sách shipment kèm đối tác vận chuyển để theo dõi đơn giao.
   Thông tin gồm: ShipmentID, OrderID, ShipmentDate, ExpectedDeliveryDate, ShipmentStatus, PrtName. */
SELECT s.ShipmentID, o.OrderID, s.ShipmentDate, s.ExpectedDeliveryDate,
       s.ShipmentStatus, d.PrtName
FROM Shipment s JOIN [Order] o ON s.OrderID = o.OrderID
                JOIN Delivery_Partner d ON s.PartnerID = d.PartnerID
ORDER BY s.ShipmentID;
GO

/* 25. Nhân viên điều phối giao hàng cần liệt kê các shipment đang vận chuyển để theo dõi tiến độ giao hàng.
   Thông tin gồm: ShipmentID, OrderID, ShipmentDate, ExpectedDeliveryDate, ShipmentStatus, PrtName. */
SELECT s.ShipmentID, o.OrderID, s.ShipmentDate, s.ExpectedDeliveryDate,
       s.ShipmentStatus, d.PrtName
FROM Shipment s JOIN [Order] o ON s.OrderID = o.OrderID
                JOIN Delivery_Partner d ON s.PartnerID = d.PartnerID
WHERE s.ShipmentStatus = N'Đang vận chuyển';
GO

/* 26. Nhân viên điều phối giao hàng cần liệt kê các shipment đã giao thành công để đối chiếu với đơn hoàn thành.
   Thông tin gồm: ShipmentID, OrderID, ActualDeliveryDate, ShipmentStatus, PrtName. */
SELECT s.ShipmentID, o.OrderID, s.ActualDeliveryDate, s.ShipmentStatus, d.PrtName
FROM Shipment s JOIN [Order] o ON s.OrderID = o.OrderID
                JOIN Delivery_Partner d ON s.PartnerID = d.PartnerID
WHERE s.ShipmentStatus = N'Giao thành công';
GO

/* 27. Quản lý cần thống kê số shipment theo từng đối tác vận chuyển để đánh giá khối lượng giao hàng.
   Thông tin gồm: PartnerID, PrtName, SoLuongShipment. */
SELECT d.PartnerID, d.PrtName, SoLuongShipment = COUNT(s.ShipmentID)
FROM Delivery_Partner d LEFT JOIN Shipment s ON d.PartnerID = s.PartnerID
GROUP BY d.PartnerID, d.PrtName;
GO

/* 28. Quản trị viên cần liệt kê tài khoản và vai trò của từng nhân viên để kiểm tra phân quyền hệ thống.
   Thông tin gồm: EmployeeID, EmpName, Username, RoleName, AccountStatus. */
SELECT e.EmployeeID, e.EmpName, a.Username, r.RoleName, a.AccountStatus
FROM Account a JOIN Employee e ON a.EmployeeID = e.EmployeeID
               JOIN [Role] r ON a.RoleID = r.RoleID;
GO

/* 29. Quản lý cần thống kê số đơn hàng do từng nhân viên phụ trách để đánh giá hiệu suất xử lý đơn.
   Thông tin gồm: EmployeeID, EmpName, SoDonPhuTrach. */
SELECT e.EmployeeID, e.EmpName, SoDonPhuTrach = COUNT(o.OrderID)
FROM Employee e LEFT JOIN [Order] o ON e.EmployeeID = o.EmployeeID
GROUP BY e.EmployeeID, e.EmpName
ORDER BY SoDonPhuTrach DESC;
GO

/* 30. Quản lý cần thống kê số shipment do từng nhân viên phụ trách để đánh giá khối lượng điều phối giao hàng.
   Thông tin gồm: EmployeeID, EmpName, SoShipmentPhuTrach. */
SELECT e.EmployeeID, e.EmpName, SoShipmentPhuTrach = COUNT(s.ShipmentID)
FROM Employee e LEFT JOIN Shipment s ON e.EmployeeID = s.EmployeeID
GROUP BY e.EmployeeID, e.EmpName
ORDER BY SoShipmentPhuTrach DESC;
GO

/* 31. Kế toán cần thống kê doanh thu của từng khách hàng đã thanh toán để xác định nhóm khách hàng có giá trị cao.
   Thông tin gồm: CustomerID, CusPhone, TongChiTieu. */
SELECT c.CustomerID, c.CusPhone, TongChiTieu = SUM(p.Amount)
FROM Customer c JOIN [Order] o ON c.CustomerID = o.CustomerID
                JOIN Payment p ON o.OrderID = p.OrderID
WHERE p.PaymentStatus = N'Đã thanh toán'
GROUP BY c.CustomerID, c.CusPhone
ORDER BY TongChiTieu DESC;
GO

/* 32. Quản lý cần thống kê doanh thu theo từng sản phẩm đã bán để đánh giá mặt hàng bán hiệu quả.
   Thông tin gồm: ProductID, ProductName, DoanhThu. */
SELECT p.ProductID, p.ProductName,
       DoanhThu = SUM(od.Quantity * od.OrderDetailUnitPrice)
FROM Product p JOIN Order_Detail od ON p.ProductID = od.ProductID
GROUP BY p.ProductID, p.ProductName
ORDER BY DoanhThu DESC;
GO

/* 33. Nhân viên điều phối giao hàng cần liệt kê các shipment chưa giao xong để tiếp tục theo dõi xử lý.
   Thông tin gồm: ShipmentID, OrderID, ShipmentDate, ExpectedDeliveryDate, ShipmentStatus, PrtName. */
SELECT s.ShipmentID, s.OrderID, s.ShipmentDate, s.ExpectedDeliveryDate,
       s.ShipmentStatus, d.PrtName
FROM Shipment s JOIN Delivery_Partner d ON s.PartnerID = d.PartnerID
WHERE s.ActualDeliveryDate IS NULL;
GO

/* 34. Quản lý cần thống kê số đơn hàng theo từng nhân viên xử lý để theo dõi năng suất làm việc.
   Thông tin gồm: EmployeeID, EmpName, SoDonHang. */
SELECT e.EmployeeID, e.EmpName, SoDonHang = COUNT(o.OrderID)
FROM Employee e LEFT JOIN [Order] o ON e.EmployeeID = o.EmployeeID
GROUP BY e.EmployeeID, e.EmpName
ORDER BY SoDonHang DESC;
GO

/* 35. Kế toán cần liệt kê các đơn hàng thanh toán khi nhận hàng nhưng chưa thanh toán để theo dõi COD.
   Thông tin gồm: OrderID, OrderDate, TotalAmount, PaymentMethod, PaymentStatus. */
SELECT o.OrderID, o.OrderDate, o.TotalAmount,
       p.PaymentMethod, p.PaymentStatus
FROM [Order] o JOIN Payment p ON o.OrderID = p.OrderID
WHERE p.PaymentMethod = N'Thanh toán khi nhận hàng'
  AND p.PaymentStatus = N'Chưa thanh toán';
GO
