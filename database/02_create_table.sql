USE QL_BANHANG_KHOHANG;


---TẠO BẢNG CUSTOMER
create table Customer
(
	CustomerID int not null,
	CusName nvarchar(50) not null,
	CusPhone varchar(15) not null,
	CusEmail varchar(100),
	CusAddress nvarchar(200) not null,
	CusCreatedDate date not null,
	CusType nvarchar(30) not null
)

---TẠO BẢNG INDIVIDUAL_CUSTOMER
create table Individual_Customer
(
	ICustomerID int not null,
	Gender nvarchar(3) not null,
	CusDateOfBirth date
)

---TẠO BẢNG BUSINESS_CUSTOMER
create table Business_Customer
(
	BCustomerID int not null,
	TaxCode varchar(20) not null
)

---TẠO BẢNG CATEGORY
create table Category
(
	CategoryID int not null,
	CategoryName nvarchar(100) not null,
	CategoryDescription nvarchar(255)
)

---TẠO BẢNG PRODUCT
create table Product
(
	ProductID int not null,
	ProductName nvarchar(150) not null,
	ProductUnitPrice decimal(18,2) not null,
	Unit nvarchar(30),
	ProductDescription nvarchar(255),
	ProductStatus nvarchar(30) not null,
	CategoryID int not null
)

---TẠO BẢNG WAREHOUSE
create table Warehouse
(
	WarehouseID int not null,
	WarehouseName nvarchar(100) not null,
	Address nvarchar(200) not null,
	Capacity int not null
)

---TẠO BẢNG INVENTORY
create table Inventory
(
	WarehouseID int not null,
	ProductID int not null,
	QuantityInStock int not null,
	LastUpdated date not null
)

---TẠO BẢNG EMPLOYEE
create table Employee
(
	EmployeeID int not null,
	EmpName nvarchar(100) not null,
	EmpGender nvarchar(10) not null,
	EmpDateOfBirth date not null,
	EmpPhone varchar(15) not null,
	EmpEmail varchar(100),
	Department nvarchar(100),
	Position nvarchar(100),
	HireDate date not null
)

---TẠO BẢNG ROLE
create table [Role]
(
	RoleID int not null,
	RoleName nvarchar(100) not null,
	RoleDescription nvarchar(255)
)

---TẠO BẢNG ACCOUNT
create table Account
(
	AccountID int not null,
	Username varchar(50) not null,
	PasswordHash varchar(255) not null,
	AccountStatus nvarchar(30) not null,
	EmployeeID int not null,
	RoleID int not null
)

---TẠO BẢNG ORDER
create table [Order]
(
	OrderID int not null,
	OrderDate date not null,
	TotalAmount decimal(18,2) not null,
	OrderStatus nvarchar(30) not null,
	ShippingAddress nvarchar(200) not null,
	CustomerID int not null,
	EmployeeID int not null
)

---TẠO BẢNG ORDER_DETAIL
create table Order_Detail
(
	OrderID int not null,
	ProductID int not null,
	Quantity int not null,
	OrderDetailUnitPrice decimal(18,2) not null
)

---TẠO BẢNG PAYMENT
create table Payment
(
	PaymentID int not null,
	PaymentDate date,
	Amount decimal(18,2) not null,
	PaymentMethod nvarchar(50) not null,
	PaymentStatus nvarchar(30) not null,
	OrderID int not null
)

---TẠO BẢNG DELIVERY_PARTNER
create table Delivery_Partner
(
	PartnerID int not null,
	PrtName nvarchar(100) not null,
	PrtPhone varchar(15),
	PrtEmail varchar(100),
	PrtAddress nvarchar(200)
)

--TẠO BẢNG PRT_SHIPPING_METHODS
create table Prt_Shipping_Methods
(
	PartnerID int not null,
	Prt_Shipping_Methods nvarchar (50) not null
)

---TẠO BẢNG SHIPMENT
create table Shipment
(
	ShipmentID int not null,
	ShipmentDate date not null,
	ExpectedDeliveryDate date,
	ActualDeliveryDate date,
	ShippingFee decimal(18,2),
	ShipmentStatus nvarchar(30) not null,
	ShipmentMethod nvarchar(50),
	OrderID int not null,
	PartnerID int not null,
	EmployeeID int not null
)
