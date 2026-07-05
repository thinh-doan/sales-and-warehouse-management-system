------RÀNG BUỘC UNIQUE CHO BẢNG Customer
---ĐẢM BẢO SĐT KHÁCH HÀNG KHÔNG BỊ TRÙNG
ALTER TABLE Customer ADD CONSTRAINT UQ_Customer_Phone UNIQUE (CusPhone)

---RÀNG BUỘC UNIQUE CHO BẢNG Business_Customer
---ĐẢM BẢO MÃ SỐ THUẾ DOANH NGHIỆP KHÔNG BỊ TRÙNG
ALTER TABLE Business_Customer ADD CONSTRAINT UQ_Business_Customer_TaxCode UNIQUE (TaxCode)

---RÀNG BUỘC UNIQUE CHO BẢNG Category
---ĐẢM BẢO TÊN DANH MỤC KHÔNG BỊ TRÙNG
ALTER TABLE Category ADD CONSTRAINT UQ_Category_Name UNIQUE (CategoryName)

---RÀNG BUỘC UNIQUE CHO BẢNG Product
---ĐẢM BẢO TÊN SẢN PHẨM KHÔNG BỊ TRÙNG
ALTER TABLE Product ADD CONSTRAINT UQ_Product_Name UNIQUE (ProductName)

---RÀNG BUỘC UNIQUE CHO BẢNG Employee
---ĐẢM BẢO SĐT NHÂN VIÊN KHÔNG BỊ TRÙNG
ALTER TABLE Employee ADD CONSTRAINT UQ_Employee_Phone UNIQUE (EmpPhone)

---RÀNG BUỘC UNIQUE CHO BẢNG Account
---ĐẢM BẢO 01 NHÂN VIÊN CHỈ CÓ TỐI ĐA 01 TÀI KHOẢN
ALTER TABLE Account ADD CONSTRAINT UQ_Account_EmployeeID UNIQUE (EmployeeID)

---RÀNG BUỘC UNIQUE CHO BẢNG Account
---ĐẢM BẢO TÊN ĐĂNG NHẬP KHÔNG BỊ TRÙNG
ALTER TABLE Account ADD CONSTRAINT UQ_Account_Username UNIQUE (Username)

---RÀNG BUỘC UNIQUE CHO BẢNG Role
---ĐẢM BẢO TÊN VAI TRÒ KHÔNG BỊ TRÙNG
ALTER TABLE [Role] ADD CONSTRAINT UQ_Role_Name UNIQUE (RoleName)

---RÀNG BUỘC UNIQUE CHO BẢNG Payment
---ĐẢM BẢO 01 ĐƠN HÀNG CHỈ CÓ TỐI ĐA 01 THÔNG TIN THANH TOÁN
ALTER TABLE Payment ADD CONSTRAINT UQ_Payment_OrderID UNIQUE (OrderID)

---RÀNG BUỘC UNIQUE CHO BẢNG Shipment
---ĐẢM BẢO 01 ĐƠN HÀNG CHỈ CÓ TỐI ĐA 01 SHIPMENT
ALTER TABLE Shipment ADD CONSTRAINT UQ_Shipment_OrderID UNIQUE (OrderID)