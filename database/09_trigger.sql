use [QL_BANHANG_KHOHANG]

--1. TỰ ĐỘNG TỪ KHO KHI NHÂN VIÊN THÊM SẢN PHẨM VÀO ĐƠN HÀNG
CREATE TRIGGER trg_OrderDetail_Insert_UpdateInventory
ON Order_Detail
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Cập nhật giảm số lượng trong kho (Ưu tiên kho có hàng)
    UPDATE INV
    SET INV.QuantityInStock = INV.QuantityInStock - INS.Quantity,
        INV.LastUpdated = GETDATE()
    FROM Inventory INV
    JOIN inserted INS ON INV.ProductID = INS.ProductID
    WHERE INV.WarehouseID = (
        SELECT TOP 1 WarehouseID 
        FROM Inventory 
        WHERE ProductID = INS.ProductID AND QuantityInStock >= INS.Quantity
        ORDER BY QuantityInStock DESC
    );
END
GO

--TỰ ĐỘNG HOÀN KHO KHI ĐƠN BỊ HỦY
CREATE TRIGGER trg_Order_Update_CancelHoanKho
ON [Order]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Kiểm tra nếu trạng thái chuyển sang 'Đã hủy'
    IF EXISTS (SELECT 1 FROM inserted i JOIN deleted d ON i.OrderID = d.OrderID 
               WHERE i.OrderStatus = N'Đã hủy' AND d.OrderStatus <> N'Đã hủy')
    BEGIN
        -- Cộng lại số lượng vào kho (trả về kho 1 làm kho mặc định hoặc kho gần nhất)
        UPDATE INV
        SET INV.QuantityInStock = INV.QuantityInStock + OD.Quantity,
            INV.LastUpdated = GETDATE()
        FROM Inventory INV
        JOIN Order_Detail OD ON INV.ProductID = OD.ProductID
        JOIN inserted i ON OD.OrderID = i.OrderID
        WHERE INV.WarehouseID = 1; -- Giả định hoàn trả về Kho 1 (Kho Tân Bình)
    END
END
GO

--Tự động tính tổng tiền đơn hàng khi Thêm/Sửa/Xóa chi tiết đơn
CREATE TRIGGER trg_OrderDetail_Change_UpdateTotalAmount
ON Order_Detail
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- Khai báo bảng tạm chứa các OrderID bị ảnh hưởng
    DECLARE @AffectedOrders TABLE (OrderID INT);

    -- Lấy tất cả OrderID từ lượt insert, update hoặc delete
    INSERT INTO @AffectedOrders
    SELECT OrderID FROM inserted
    UNION
    SELECT OrderID FROM deleted;

    -- Cập nhật lại TotalAmount cho các đơn hàng đó
    UPDATE O
    SET O.TotalAmount = ISNULL(DS.NewTotal, 0)
    FROM [Order] O
    LEFT JOIN (
        SELECT OrderID, SUM(Quantity * OrderDetailUnitPrice) AS NewTotal
        FROM Order_Detail
        GROUP BY OrderID
    ) DS ON O.OrderID = DS.OrderID
    WHERE O.OrderID IN (SELECT OrderID FROM @AffectedOrders);
END
GO

--Kiểm tra đồng bộ loại Khách hàng,
--không cho phép một CustomerID vừa khai báo là cá nhân nhưng lại chèn dữ liệu vào bảng Business_Customer
CREATE TRIGGER trg_BusinessCustomer_Insert_CheckType
ON Business_Customer
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (
        SELECT 1 
        FROM inserted i
        JOIN Customer c ON i.BCustomerID = c.CustomerID
        WHERE c.CusType <> N'Doanh nghiệp'
    )
    BEGIN
        RAISERROR (N'Lỗi: Khách hàng này không phải là loại Doanh nghiệp ở bảng Customer!', 16, 1);
        ROLLBACK TRANSACTION;
    END
END
GO

CREATE TRIGGER trg_IndividualCustomer_Insert_CheckType
ON Individual_Customer
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (
        SELECT 1 
        FROM inserted i
        JOIN Customer c ON i.ICustomerID = c.CustomerID
        WHERE c.CusType <> N'Cá nhân'
    )
    BEGIN
        RAISERROR (N'Lỗi: Khách hàng này không phải là loại Cá nhân ở bảng Customer!', 16, 1);
        ROLLBACK TRANSACTION;
    END
END
GO

USE [QL_BANHANG_KHOHANG];
GO

--Tự động tạo ngày giao hàng dự kiến là 3 ngày kể từ ngày đặt đơn hàng.
CREATE TRIGGER Trg_Shipment_Insert_SetExpected3Days
ON Shipment
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Tự động tính toán nếu cột ExpectedDeliveryDate được truyền vào là NULL
    UPDATE s
    SET s.ExpectedDeliveryDate = DATEADD(DAY, 3, i.ShipmentDate)
    FROM Shipment s
         JOIN inserted i ON s.ShipmentID = i.ShipmentID
    WHERE s.ExpectedDeliveryDate IS NULL;
END;
GO