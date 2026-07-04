use [QL_BANHANG_KHOHANG]

---RÀNG BUỘC CHECK CHO BẢNG Customer
---ĐẢM BẢO LOẠI KHÁCH HÀNG HỢP LỆ
ALTER TABLE Customer ADD CONSTRAINT CK_Customer_Type
CHECK (CusType IN (N'Cá nhân', N'Doanh nghiệp'))

---RÀNG BUỘC CHECK CHO BẢNG Employee
---ĐẢM BẢO GIỚI TÍNH NHÂN VIÊN HỢP LỆ
ALTER TABLE Employee ADD CONSTRAINT CK_Employee_Gender
CHECK (EmpGender IN (N'Nam', N'Nữ') OR EmpGender IS NULL)

---RÀNG BUỘC CHECK CHO BẢNG Employee
---ĐẢM BẢO NGÀY SINH NHÂN VIÊN NHỎ HƠN NGÀY VÀO LÀM NẾU CÓ NHẬP NGÀY SINH
ALTER TABLE Employee ADD CONSTRAINT CK_Employee_DateOfBirth
CHECK (EmpDateOfBirth IS NULL OR EmpDateOfBirth < HireDate)

---RÀNG BUỘC CHECK CHO BẢNG Product
---ĐẢM BẢO GIÁ BÁN SẢN PHẨM KHÔNG ÂM
ALTER TABLE Product ADD CONSTRAINT CK_Product_UnitPrice
CHECK (ProductUnitPrice >= 0)

---RÀNG BUỘC CHECK CHO BẢNG Product
---ĐẢM BẢO TRẠNG THÁI SẢN PHẨM HỢP LỆ
ALTER TABLE Product ADD CONSTRAINT CK_Product_Status
CHECK (ProductStatus IN (N'Đang bán', N'Ngừng bán'))

---RÀNG BUỘC CHECK CHO BẢNG Warehouse
---ĐẢM BẢO SỨC CHỨA KHO KHÔNG ÂM NẾU CÓ NHẬP
ALTER TABLE Warehouse ADD CONSTRAINT CK_Warehouse_Capacity
CHECK (Capacity IS NULL OR Capacity >= 0)

---RÀNG BUỘC CHECK CHO BẢNG Inventory
---ĐẢM BẢO SỐ LƯỢNG TỒN KHO KHÔNG ÂM
ALTER TABLE Inventory ADD CONSTRAINT CK_Inventory_Quantity
CHECK (QuantityInStock >= 0)

---RÀNG BUỘC CHECK CHO BẢNG Order
---ĐẢM BẢO TỔNG TIỀN ĐƠN HÀNG KHÔNG ÂM
ALTER TABLE [Order] ADD CONSTRAINT CK_Order_TotalAmount
CHECK (TotalAmount >= 0)

---RÀNG BUỘC CHECK CHO BẢNG Order
---ĐẢM BẢO TRẠNG THÁI ĐƠN HÀNG HỢP LỆ
ALTER TABLE [Order] ADD CONSTRAINT CK_Order_Status
CHECK (OrderStatus IN (N'Chờ xác nhận', N'Đang xử lý', N'Đang giao', N'Hoàn thành', N'Đã hủy'))

---RÀNG BUỘC CHECK CHO BẢNG Order_Detail
---ĐẢM BẢO SỐ LƯỢNG SẢN PHẨM TRONG CHI TIẾT ĐƠN HÀNG LỚN HƠN 0
ALTER TABLE Order_Detail ADD CONSTRAINT CK_Order_Detail_Quantity
CHECK (Quantity > 0)

---RÀNG BUỘC CHECK CHO BẢNG Order_Detail
---ĐẢM BẢO ĐƠN GIÁ TẠI THỜI ĐIỂM ĐẶT HÀNG KHÔNG ÂM
ALTER TABLE Order_Detail ADD CONSTRAINT CK_Order_Detail_UnitPrice
CHECK (OrderDetailUnitPrice >= 0)

---RÀNG BUỘC CHECK CHO BẢNG Payment
---ĐẢM BẢO SỐ TIỀN THANH TOÁN KHÔNG ÂM
ALTER TABLE Payment ADD CONSTRAINT CK_Payment_Amount
CHECK (Amount >= 0)

---RÀNG BUỘC CHECK CHO BẢNG Payment
---ĐẢM BẢO PHƯƠNG THỨC THANH TOÁN HỢP LỆ
ALTER TABLE Payment ADD CONSTRAINT CK_Payment_Method
CHECK (PaymentMethod IN (N'Thanh toán khi nhận hàng', N'Chuyển khoản', N'Thanh toán điện tử'))

---RÀNG BUỘC CHECK CHO BẢNG Payment
---ĐẢM BẢO TRẠNG THÁI THANH TOÁN HỢP LỆ
ALTER TABLE Payment ADD CONSTRAINT CK_Payment_Status
CHECK (PaymentStatus IN (N'Chưa thanh toán', N'Đã thanh toán'))

---RÀNG BUỘC CHECK CHO BẢNG Shipment
---ĐẢM BẢO PHÍ GIAO HÀNG KHÔNG ÂM NẾU CÓ NHẬP
ALTER TABLE Shipment ADD CONSTRAINT CK_Shipment_Fee
CHECK (ShippingFee IS NULL OR ShippingFee >= 0)

---RÀNG BUỘC CHECK CHO BẢNG Shipment
---ĐẢM BẢO TRẠNG THÁI GIAO HÀNG HỢP LỆ
ALTER TABLE Shipment ADD CONSTRAINT CK_Shipment_Status
CHECK (ShipmentStatus IN(N'Chờ lấy hàng', N'Đang vận chuyển', N'Giao thành công', N'Giao thất bại', N'Hoàn trả'))

---RÀNG BUỘC CHECK CHO BẢNG Shipment
---ĐẢM BẢO NGÀY GIAO DỰ KIẾN KHÔNG NHỎ HƠN NGÀY TẠO SHIPMENT NẾU CÓ NHẬP
ALTER TABLE Shipment ADD CONSTRAINT CK_Shipment_ExpectedDate
CHECK (ExpectedDeliveryDate IS NULL OR ExpectedDeliveryDate >= ShipmentDate)

---RÀNG BUỘC CHECK CHO BẢNG Shipment
---ĐẢM BẢO NGÀY GIAO THỰC TẾ KHÔNG NHỎ HƠN NGÀY TẠO SHIPMENT NẾU CÓ NHẬP
ALTER TABLE Shipment ADD CONSTRAINT CK_Shipment_ActualDate
CHECK (ActualDeliveryDate IS NULL OR ActualDeliveryDate >= ShipmentDate)

---RÀNG BUỘC CHECK CHO BẢNG Account
---ĐẢM BẢO TRẠNG THÁI TÀI KHOẢN HỢP LỆ
ALTER TABLE Account ADD CONSTRAINT CK_Account_Status
CHECK (AccountStatus IN (N'Đang hoạt động', N'Đã khóa'))
