from datetime import date
from decimal import Decimal

from PyQt6 import QtCore
from PyQt6.QtWidgets import QAbstractItemView, QDialog, QMessageBox, QTableWidgetItem

from connect import Database
from modules.order.order_add_ord_detail_ui import Ui_hopThoaiDonHangMuc
from modules.order.order_detail_ui import Ui_hopThoaiDonHang


ORDER_STATUSES = ["Chờ xử lý", "Đang chuẩn bị", "Đang giao", "Hoàn thành", "Đã hủy"]
PAYMENT_METHODS = ["Thanh toán khi nhận hàng", "Chuyển khoản", "Thanh toán điện tử"]
PAYMENT_STATUSES = ["Chưa thanh toán", "Đã thanh toán"]
SHIPMENT_METHODS = ["Tiêu chuẩn", "Tiết kiệm", "Hỏa tốc"]


def _format_date(value):
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y")
    return str(value)


def _format_currency(value):
    try:
        return f"{float(value or 0):,.0f}"
    except Exception:
        return str(value or "")


def _parse_float(text):
    try:
        return float(str(text).replace(",", "").strip() or 0)
    except ValueError:
        return None


def _ensure_support_tables(db):
    db.execute(
        """
        IF OBJECT_ID(N'dbo.OrderDetailInventoryMap', N'U') IS NULL
        BEGIN
            CREATE TABLE dbo.OrderDetailInventoryMap (
                OrderID INT NOT NULL,
                ProductID INT NOT NULL,
                WarehouseID INT NOT NULL,
                Quantity INT NOT NULL,
                CONSTRAINT PK_OrderDetailInventoryMap PRIMARY KEY (OrderID, ProductID)
            );
        END
        """
    )


def _set_combo_to_value(combo, value):
    if value is None:
        combo.setCurrentIndex(0)
        return
    for index in range(combo.count()):
        if combo.itemData(index) == value or combo.itemText(index) == str(value):
            combo.setCurrentIndex(index)
            return
    combo.setCurrentIndex(0)


def _inventory_stock(db, product_id, warehouse_id):
    row = db.execute(
        "SELECT QuantityInStock FROM Inventory WHERE ProductID = ? AND WarehouseID = ?",
        (int(product_id), int(warehouse_id)),
    ).fetchone()
    return int(row[0] if row else 0)


def _best_warehouse(db, product_id, quantity, preferred_warehouse_id=None):
    if preferred_warehouse_id is not None:
        preferred_stock = _inventory_stock(db, product_id, preferred_warehouse_id)
        if preferred_stock >= quantity:
            return int(preferred_warehouse_id), preferred_stock

    rows = db.execute(
        """
        SELECT i.WarehouseID, i.QuantityInStock
        FROM Inventory i
        WHERE i.ProductID = ? AND i.QuantityInStock >= ?
        ORDER BY i.QuantityInStock DESC, i.WarehouseID ASC
        """,
        (int(product_id), int(quantity)),
    ).fetchall()
    if not rows:
        return None, 0
    return int(rows[0][0]), int(rows[0][1] or 0)


def _adjust_inventory(db, product_id, warehouse_id, delta):
    current_stock = _inventory_stock(db, product_id, warehouse_id)
    new_stock = current_stock + int(delta)
    if new_stock < 0:
        return False

    exists = db.execute(
        "SELECT 1 FROM Inventory WHERE ProductID = ? AND WarehouseID = ?",
        (int(product_id), int(warehouse_id)),
    ).fetchone()
    if exists:
        db.execute(
            "UPDATE Inventory SET QuantityInStock = ?, LastUpdated = CAST(GETDATE() AS DATE) WHERE ProductID = ? AND WarehouseID = ?",
            (new_stock, int(product_id), int(warehouse_id)),
        )
    else:
        db.execute(
            "INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated) VALUES (?, ?, ?, CAST(GETDATE() AS DATE))",
            (int(warehouse_id), int(product_id), new_stock),
        )
    return True


class OrderItemDialog(QDialog, Ui_hopThoaiDonHangMuc):
    def __init__(self, parent=None, order_id=None, detail=None):
        super().__init__(parent)
        self.setupUi(self)
        self.order_id = order_id
        self.detail = detail  # Dữ liệu truyền vào dạng: (ProductID, Quantity, WarehouseID)
        self.products = []
        self._connect_signals()
        self._load_products()
        self._populate_form()

    def _connect_signals(self):
        self.btnLuu_Order_detail.clicked.connect(self._save_item)
        self.btnHuyOrder_Detail.clicked.connect(self.reject)
        self.cbbSanPham.currentIndexChanged.connect(self._on_product_changed)

    def _load_products(self):
        db = Database()
        try:
            rows = db.execute(
                "SELECT ProductID, ProductName, ProductUnitPrice FROM Product ORDER BY ProductName, ProductID"
            ).fetchall()
            self.cbbSanPham.blockSignals(True)
            self.cbbSanPham.clear()
            self.products = []
            for row in rows:
                self.products.append((int(row[0]), str(row[1] or ""), float(row[2] or 0)))
                self.cbbSanPham.addItem(str(row[1] or ""), int(row[0]))
        finally:
            self.cbbSanPham.blockSignals(False)
            db.close()

    def _load_warehouses(self, product_id, preferred_warehouse_id=None):
        db = Database()
        try:
            rows = db.execute(
                """
                SELECT w.WarehouseID, w.WarehouseName, i.QuantityInStock
                FROM Inventory i
                JOIN Warehouse w ON w.WarehouseID = i.WarehouseID
                WHERE i.ProductID = ?
                ORDER BY i.QuantityInStock DESC, w.WarehouseID ASC
                """,
                (int(product_id),),
            ).fetchall()

            self.cbbKhoSP.blockSignals(True)
            self.cbbKhoSP.clear()
            if not rows:
                self.cbbKhoSP.addItem("Không có kho phù hợp", None)
                self.cbbKhoSP.setEnabled(False)
                self.txtTonKho.setText(str(product_id))
                return None

            self.cbbKhoSP.setEnabled(True)
            for row in rows:
                warehouse_id = int(row[0])
                warehouse_name = str(row[1] or "")
                stock = int(row[2] or 0)
                self.cbbKhoSP.addItem(f"{warehouse_name} ({stock})", warehouse_id)

            if preferred_warehouse_id is not None:
                _set_combo_to_value(self.cbbKhoSP, int(preferred_warehouse_id))
            else:
                self.cbbKhoSP.setCurrentIndex(0)

            self.txtTonKho.setText(str(product_id))
            current_warehouse_id = self.cbbKhoSP.currentData()
            return int(current_warehouse_id) if current_warehouse_id is not None else int(rows[0][0])
        finally:
            self.cbbKhoSP.blockSignals(False)
            db.close()

    def _populate_form(self):
        if self.detail:
            product_id = self.detail[0]
            quantity = self.detail[1]
            warehouse_id = self.detail[2] if len(self.detail) > 2 else None
            self._set_selected_product(product_id)
            self.spinSpinSoLuong.setValue(int(quantity or 1))
            self._load_warehouses(product_id, warehouse_id)
            self.cbbSanPham.setEnabled(False)
            self.setWindowTitle("Cập nhật sản phẩm trong đơn hàng")
        else:
            self.setWindowTitle("Thêm sản phẩm vào đơn hàng")
            self.cbbSanPham.setEnabled(True)
            if self.products:
                self._on_product_changed()

    def _set_selected_product(self, product_id):
        for index in range(self.cbbSanPham.count()):
            if self.cbbSanPham.itemData(index) == product_id:
                self.cbbSanPham.setCurrentIndex(index)
                return

    def _current_product_row(self):
        product_id = self.cbbSanPham.currentData()
        for item in self.products:
            if item[0] == product_id:
                return item
        return None

    def _on_product_changed(self):
        product_row = self._current_product_row()
        if not product_row:
            self.txtTonKho.clear()
            self.cbbKhoSP.clear()
            self.cbbKhoSP.addItem("", None)
            return

        self.txtTonKho.setText(str(product_row[0]))
        preferred_warehouse_id = None
        if self.detail and len(self.detail) > 2:
            preferred_warehouse_id = self.detail[2]
        self._load_warehouses(product_row[0], preferred_warehouse_id)

    def _save_item(self):
        product_id = self.cbbSanPham.currentData()
        quantity = self.spinSpinSoLuong.value()
        warehouse_id = self.cbbKhoSP.currentData()

        if product_id is None:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn sản phẩm.")
            return

        product_row = self._current_product_row()
        if not product_row:
            QMessageBox.warning(self, "Thông báo", "Không tìm thấy thông tin sản phẩm.")
            return

        db = Database()
        try:
            if warehouse_id is None:
                warehouse_id, _ = _best_warehouse(db, product_id, quantity)
            if warehouse_id is None:
                QMessageBox.warning(self, "Thông báo", "Không có kho nào đủ số lượng tồn cho sản phẩm này.")
                return

            available = _inventory_stock(db, product_id, warehouse_id)
            
            # Nếu đang cập nhật đơn cũ, cần cộng trả lại lượng cũ để kiểm tra tồn kho chính xác
            old_qty = 0
            if self.detail and self.order_id:
                current_row = db.execute(
                    "SELECT Quantity FROM OrderDetailInventoryMap WHERE OrderID = ? AND ProductID = ?",
                    (self.order_id, product_id),
                ).fetchone()
                if current_row:
                    old_qty = int(current_row[0])
            
            if (available + old_qty) < quantity:
                QMessageBox.warning(self, "Thông báo", f"Tồn kho không đủ. Hiện tại chỉ còn {available + old_qty} sản phẩm.")
                return

            # Lưu thông tin tạm vào chính đối tượng dialog để parent window đọc ra
            self.result_detail = {
                "product_id": product_id,
                "product_name": product_row[1],
                "quantity": quantity,
                "price": product_row[2],
                "warehouse_id": warehouse_id,
                "total_stock": available + old_qty
            }
            self.accept()
        finally:
            db.close()


class OrderDetailDialog(QDialog, Ui_hopThoaiDonHang):
    def __init__(self, parent=None, order=None):
        super().__init__(parent)
        self.setupUi(self)
        self.order = order
        self.order_id = order[0] if order else None
        
        # Danh sách tạm lưu trữ các item: chứa dict {"product_id", "product_name", "quantity", "price", "warehouse_id"}
        self.temp_details = [] 
        
        self._prepare_detail_table()
        self._connect_signals()
        self._load_lookup_data()
        self._populate_form()

    def _prepare_detail_table(self):
        self.tblOrderDetail.setColumnCount(6)
        self.tblOrderDetail.setHorizontalHeaderLabels(["Mã SP", "Tên SP", "Số lượng", "Đơn giá", "Thành tiền", "Tồn kho"])
        self.tblOrderDetail.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblOrderDetail.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblOrderDetail.setAlternatingRowColors(True)

    def _connect_signals(self):
        self.btnLuuDH.clicked.connect(self._save_order)
        self.btnHuyDH.clicked.connect(self.reject)
        self.btnThemSP.clicked.connect(self._open_add_detail_dialog)
        self.btnCapNhatSP.clicked.connect(self._open_update_detail_dialog)
        self.btnXoaSP.clicked.connect(self._delete_selected_detail)

    def _load_lookup_data(self):
        db = Database()
        try:
            self.cboKhachHang.setEditable(False)
            self.cboNhanVien.setEditable(False)

            customer_rows = db.execute("SELECT CustomerID, CusName, CusPhone FROM Customer ORDER BY CusName, CustomerID").fetchall()
            self.cboKhachHang.clear()
            for row in customer_rows:
                text = f"{row[1] or 'Không tên'} ({row[2] or ''})".strip()
                self.cboKhachHang.addItem(text, int(row[0]))

            employee_rows = db.execute("SELECT EmployeeID, EmpName FROM Employee ORDER BY EmpName, EmployeeID").fetchall()
            self.cboNhanVien.clear()
            for row in employee_rows:
                self.cboNhanVien.addItem(str(row[1] or f"NV {row[0]}"), int(row[0]))

            self.cboTrangThai.clear()
            for status in ORDER_STATUSES:
                self.cboTrangThai.addItem(status, status)

            self.cboPhuongThucTT.clear()
            for method in PAYMENT_METHODS:
                self.cboPhuongThucTT.addItem(method, method)

            self.cboTrangThaiTT.clear()
            for status in PAYMENT_STATUSES:
                self.cboTrangThaiTT.addItem(status, status)

            partner_rows = db.execute("SELECT PartnerID, PrtName FROM Delivery_Partner ORDER BY PrtName, PartnerID").fetchall()
            self.cboDoiTac.clear()
            for row in partner_rows:
                self.cboDoiTac.addItem(str(row[1] or f"ĐT {row[0]}"), int(row[0]))

            self.cboPhuongThucVanChuyen.clear()
            for method in SHIPMENT_METHODS:
                self.cboPhuongThucVanChuyen.addItem(method, method)
        finally:
            db.close()

    def _populate_form(self):
        if self.order:
            self.setWindowTitle("Cập nhật đơn hàng")
            self._load_order_header()
            self._fetch_details_from_db()
        else:
            self.setWindowTitle("Tạo đơn hàng")
            today = date.today()
            self.txtNgayDatHang.setDate(QtCore.QDate(today.year, today.month, today.day))
            _set_combo_to_value(self.cboTrangThai, "Chờ xử lý")
            _set_combo_to_value(self.cboPhuongThucTT, "Thanh toán khi nhận hàng")
            _set_combo_to_value(self.cboTrangThaiTT, "Chưa thanh toán")
            _set_combo_to_value(self.cboPhuongThucVanChuyen, "Tiêu chuẩn")
            if self.cboDoiTac.count() > 0:
                self.cboDoiTac.setCurrentIndex(0)
            self.txtTamTinh.setText("0")
            self.txtTongTT.setText("0")
            self.txtPhiVanChuyen.setText("0")
            self._render_table_from_temp()

    def _load_order_header(self):
        if not self.order_id:
            return
        db = Database()
        try:
            row = db.execute(
                """
                SELECT o.OrderID, o.OrderDate, o.TotalAmount, o.OrderStatus, o.ShippingAddress, o.CustomerID, o.EmployeeID,
                       p.PaymentMethod, p.PaymentStatus, s.PartnerID, s.ShipmentMethod, s.ShippingFee
                FROM [Order] o
                LEFT JOIN Payment p ON p.OrderID = o.OrderID
                LEFT JOIN Shipment s ON s.OrderID = o.OrderID
                WHERE o.OrderID = ?
                """,
                (self.order_id,),
            ).fetchone()
            if not row:
                return

            order_date = row[1]
            if order_date is not None:
                if isinstance(order_date, str):
                    qdate = QtCore.QDate.fromString(order_date, "yyyy-MM-dd")
                    if qdate.isValid():
                        self.txtNgayDatHang.setDate(qdate)
                else:
                    self.txtNgayDatHang.setDate(QtCore.QDate(order_date.year, order_date.month, order_date.day))

            self.txtDiaChiGH.setText(str(row[4] or ""))
            subtotal = row[2] or Decimal('0')
            self.txtTamTinh.setText(_format_currency(subtotal))
            self.txtTongTT.setText(_format_currency(float(subtotal) + (_parse_float(self.txtPhiVanChuyen.text()) or 0)))
            _set_combo_to_value(self.cboKhachHang, row[5])
            _set_combo_to_value(self.cboNhanVien, row[6])
            _set_combo_to_value(self.cboTrangThai, row[3])
            _set_combo_to_value(self.cboPhuongThucTT, row[7])
            _set_combo_to_value(self.cboTrangThaiTT, row[8])
            _set_combo_to_value(self.cboDoiTac, row[9])
            _set_combo_to_value(self.cboPhuongThucVanChuyen, row[10])
            self.txtPhiVanChuyen.setText(_format_currency(row[11] or 0))
        finally:
            db.close()

    def _fetch_details_from_db(self):
        self.temp_details = []
        if not self.order_id:
            return
        db = Database()
        try:
            rows = db.execute(
                """
                SELECT od.ProductID, p.ProductName, od.Quantity, od.OrderDetailUnitPrice, map.WarehouseID,
                       COALESCE((SELECT SUM(QuantityInStock) FROM Inventory WHERE ProductID = od.ProductID), 0)
                FROM Order_Detail od
                JOIN Product p ON p.ProductID = od.ProductID
                LEFT JOIN OrderDetailInventoryMap map ON map.OrderID = od.OrderID AND map.ProductID = od.ProductID
                WHERE od.OrderID = ?
                ORDER BY od.ProductID
                """,
                (self.order_id,),
            ).fetchall()
            for r in rows:
                self.temp_details.append({
                    "product_id": int(r[0]),
                    "product_name": str(r[1]),
                    "quantity": int(r[2]),
                    "price": float(r[3]),
                    "warehouse_id": int(r[4]) if r[4] is not None else None,
                    "total_stock": int(r[5])
                })
            self._render_table_from_temp()
        finally:
            db.close()

    def _render_table_from_temp(self):
        self.tblOrderDetail.setRowCount(0)
        self.tblOrderDetail.setRowCount(len(self.temp_details))
        
        subtotal = 0.0
        for idx, item in enumerate(self.temp_details):
            total_price = item["quantity"] * item["price"]
            subtotal += total_price
            
            self.tblOrderDetail.setItem(idx, 0, QTableWidgetItem(f"SP{item['product_id']:03d}"))
            self.tblOrderDetail.setItem(idx, 1, QTableWidgetItem(item["product_name"]))
            self.tblOrderDetail.setItem(idx, 2, QTableWidgetItem(str(item["quantity"])))
            self.tblOrderDetail.setItem(idx, 3, QTableWidgetItem(_format_currency(item["price"])))
            self.tblOrderDetail.setItem(idx, 4, QTableWidgetItem(_format_currency(total_price)))
            self.tblOrderDetail.setItem(idx, 5, QTableWidgetItem(str(item["total_stock"])))

        self.txtTamTinh.setText(_format_currency(subtotal))
        shipping_fee = _parse_float(self.txtPhiVanChuyen.text()) or 0.0
        self.txtTongTT.setText(_format_currency(subtotal + shipping_fee))

    def _open_add_detail_dialog(self):
        dialog = OrderItemDialog(self, order_id=self.order_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_item = dialog.result_detail
            
            # Kiểm tra xem sản phẩm đã tồn tại trong danh sách tạm hay chưa
            for item in self.temp_details:
                if item["product_id"] == new_item["product_id"]:
                    QMessageBox.warning(self, "Thông báo", "Sản phẩm này đã có trong đơn hàng. Vui lòng chọn cập nhật số lượng.")
                    return
                    
            self.temp_details.append(new_item)
            self._render_table_from_temp()

    def _open_update_detail_dialog(self):
        selected_rows = self.tblOrderDetail.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một dòng sản phẩm để cập nhật.")
            return

        row_idx = selected_rows[0].row()
        target_item = self.temp_details[row_idx]
        
        detail = (target_item["product_id"], target_item["quantity"], target_item["warehouse_id"])
        dialog = OrderItemDialog(self, order_id=self.order_id, detail=detail)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.temp_details[row_idx] = dialog.result_detail
            self._render_table_from_temp()

    def _delete_selected_detail(self):
        selected_rows = self.tblOrderDetail.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một dòng sản phẩm để xóa.")
            return
            
        answer = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn xóa sản phẩm này khỏi danh sách không?")
        if answer != QMessageBox.StandardButton.Yes:
            return

        row_idx = selected_rows[0].row()
        self.temp_details.pop(row_idx)
        self._render_table_from_temp()

    def _save_order(self):
        customer_id = self.cboKhachHang.currentData()
        employee_id = self.cboNhanVien.currentData()
        order_date = self.txtNgayDatHang.date().toPyDate()
        order_status = self.cboTrangThai.currentData() or self.cboTrangThai.currentText()
        shipping_address = self.txtDiaChiGH.text().strip()
        payment_method = self.cboPhuongThucTT.currentData() or self.cboPhuongThucTT.currentText()
        payment_status = self.cboTrangThaiTT.currentData() or self.cboTrangThaiTT.currentText()
        shipment_method = self.cboPhuongThucVanChuyen.currentData() or self.cboPhuongThucVanChuyen.currentText()
        partner_id = self.cboDoiTac.currentData()
        shipping_fee = _parse_float(self.txtPhiVanChuyen.text())

        if shipping_fee is None:
            QMessageBox.warning(self, "Thông báo", "Phí vận chuyển phải là số hợp lệ.")
            return

        if not customer_id or not employee_id or not shipping_address:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ thông tin khách hàng, nhân viên và địa chỉ giao hàng.")
            return

        if not self.temp_details:
            QMessageBox.warning(self, "Thông báo", "Đơn hàng phải có ít nhất một sản phẩm.")
            return

        db = Database()
        try:
            _ensure_support_tables(db)
            
            # 1. Khôi phục lại kho nếu đây là đơn hàng cũ đang chỉnh sửa
            if self.order_id:
                # Trả lại kho theo cấu hình cũ trong DB trước khi cập nhật mới
                old_details = db.execute(
                    "SELECT ProductID, Quantity FROM Order_Detail WHERE OrderID = ?", (self.order_id,)
                ).fetchall()
                for old_p in old_details:
                    map_row = db.execute(
                        "SELECT WarehouseID FROM OrderDetailInventoryMap WHERE OrderID = ? AND ProductID = ?",
                        (self.order_id, int(old_p[0])),
                    ).fetchone()
                    w_id = int(map_row[0]) if map_row else None
                    if w_id is not None:
                        _adjust_inventory(db, int(old_p[0]), w_id, int(old_p[1]))
                
                # Xóa sạch các liên kết cũ trong Database
                db.execute("DELETE FROM Order_Detail WHERE OrderID = ?", (self.order_id,))
                db.execute("DELETE FROM OrderDetailInventoryMap WHERE OrderID = ?", (self.order_id,))
                
                # Cập nhật thông tin Header
                db.execute(
                    "UPDATE [Order] SET OrderDate = ?, OrderStatus = ?, ShippingAddress = ?, CustomerID = ?, EmployeeID = ? WHERE OrderID = ?",
                    (order_date, order_status, shipping_address, customer_id, employee_id, self.order_id),
                )
            else:
                # Tạo mới hoàn toàn Đơn hàng
                self.order_id = self._get_next_id(db, "[Order]", "OrderID")
                db.execute(
                    "INSERT INTO [Order] (OrderID, OrderDate, TotalAmount, OrderStatus, ShippingAddress, CustomerID, EmployeeID) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (self.order_id, order_date, 0, order_status, shipping_address, customer_id, employee_id),
                )

            # 2. Lưu đồng loạt danh sách sản phẩm tạm thời vào Database & Trừ kho hàng thực tế
            subtotal = 0.0
            for item in self.temp_details:
                p_id = item["product_id"]
                qty = item["quantity"]
                price = item["price"]
                w_id = item["warehouse_id"]
                
                # Thực hiện trừ kho
                if not _adjust_inventory(db, p_id, w_id, -qty):
                    raise ValueError(f"Không thể trừ tồn kho sản phẩm ID {p_id} tại kho {w_id}.")
                
                # Thêm vào bảng Order_Detail & Bản đồ kho hàng
                db.execute(
                    "INSERT INTO Order_Detail (OrderID, ProductID, Quantity, OrderDetailUnitPrice) VALUES (?, ?, ?, ?)",
                    (self.order_id, p_id, qty, price),
                )
                db.execute(
                    "INSERT INTO OrderDetailInventoryMap (OrderID, ProductID, WarehouseID, Quantity) VALUES (?, ?, ?, ?)",
                    (self.order_id, p_id, w_id, qty),
                )
                subtotal += (qty * price)

            # 3. Cập nhật lại tổng tiền chính thức
            db.execute("UPDATE [Order] SET TotalAmount = ? WHERE OrderID = ?", (subtotal, self.order_id))
            
            # 4. Đồng bộ Thanh toán & Vận chuyển
            self._upsert_payment(db, self.order_id, order_date, payment_method, payment_status, subtotal + shipping_fee)
            self._upsert_shipment(db, self.order_id, order_date, shipment_method, partner_id, shipping_fee, employee_id)
            
            db.commit()
            QMessageBox.information(self, "Thành công", "Lưu đơn hàng thành công.")
            self.accept()
        except Exception as exc:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu đơn hàng.\nChi tiết: {exc}")
        finally:
            db.close()

    def _upsert_payment(self, db, order_id, order_date, payment_method, payment_status, total_payment):
        payment_row = db.execute("SELECT PaymentID FROM Payment WHERE OrderID = ?", (order_id,)).fetchone()
        if payment_row:
            db.execute(
                "UPDATE Payment SET PaymentDate = ?, Amount = ?, PaymentMethod = ?, PaymentStatus = ? WHERE OrderID = ?",
                (order_date, total_payment, payment_method, payment_status, order_id),
            )
        else:
            payment_id = self._get_next_id(db, "Payment", "PaymentID")
            db.execute(
                "INSERT INTO Payment (PaymentID, PaymentDate, Amount, PaymentMethod, PaymentStatus, OrderID) VALUES (?, ?, ?, ?, ?, ?)",
                (payment_id, order_date, total_payment, payment_method, payment_status, order_id),
            )

    def _upsert_shipment(self, db, order_id, order_date, shipment_method, partner_id, shipping_fee, employee_id):
        shipment_row = db.execute("SELECT ShipmentID FROM Shipment WHERE OrderID = ?", (order_id,)).fetchone()
        if shipment_row:
            db.execute(
                """
                UPDATE Shipment
                SET ShipmentDate = ?, ShippingFee = ?, ShipmentMethod = ?, PartnerID = ?, EmployeeID = ?
                WHERE OrderID = ?
                """,
                (order_date, shipping_fee, shipment_method, partner_id or 1, employee_id, order_id),
            )
        else:
            shipment_id = self._get_next_id(db, "Shipment", "ShipmentID")
            db.execute(
                """
                INSERT INTO Shipment (ShipmentID, ShipmentDate, ExpectedDeliveryDate, ActualDeliveryDate, ShippingFee, ShipmentStatus, ShipmentMethod, OrderID, PartnerID, EmployeeID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (shipment_id, order_date, None, None, shipping_fee, "Chờ lấy hàng", shipment_method, order_id, partner_id or 1, employee_id),
            )

    def _get_next_id(self, db, table_name, column_name):
        row = db.execute(f"SELECT COALESCE(MAX({column_name}), 0) FROM {table_name}").fetchone()
        return int(row[0] or 0) + 1


class OrderPageController:
    def __init__(self, window):
        self.window = window
        self._connect_signals()
        self._prepare_table()
        self._prepare_search_defaults()
        self.load_order_table()

    @staticmethod
    def _show_error(parent, title, exc):
        QMessageBox.critical(parent, title, f"Đã xảy ra lỗi trong chức năng Đơn hàng.\n{exc}")

    def _prepare_search_defaults(self):
        if hasattr(self.window, "txtTuNgayDH"):
            self.window.txtTuNgayDH.setDate(QtCore.QDate(2000, 1, 1))
        if hasattr(self.window, "txtDenNgayDH"):
            today = date.today()
            self.window.txtDenNgayDH.setDate(QtCore.QDate(today.year, today.month, today.day))

    def _connect_signals(self):
        self.window.btnThemDH.clicked.connect(self.open_add_order_dialog)
        self.window.btnCapNhatDH.clicked.connect(self.open_update_order_dialog)
        self.window.btnXoaDH.clicked.connect(self.delete_order)
        self.window.btnRefreshDH.clicked.connect(self.load_order_table)
        self.window.btnTimKiemDH.clicked.connect(self.search_orders)

        if hasattr(self.window, "txtTimKiemDH"):
            self.window.txtTimKiemDH.returnPressed.connect(self.search_orders)
        if hasattr(self.window, "txtTuNgayDH"):
            self.window.txtTuNgayDH.dateChanged.connect(lambda _: self.search_orders())
        if hasattr(self.window, "txtDenNgayDH"):
            self.window.txtDenNgayDH.dateChanged.connect(lambda _: self.search_orders())

        self.window.tblDonHang.itemSelectionChanged.connect(self._update_button_state)

    def _prepare_table(self):
        table = self.window.tblDonHang
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Mã ĐH", "Ngày tạo", "Khách hàng", "Địa chỉ", "Tổng tiền", "Trạng thái"])
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)

    def _update_button_state(self):
        has_selection = bool(self.window.tblDonHang.selectedItems())
        self.window.btnCapNhatDH.setEnabled(has_selection)
        self.window.btnXoaDH.setEnabled(has_selection)

    def load_order_table(self):
        db = Database()
        try:
            rows = db.execute(
                """
                SELECT o.OrderID, o.OrderDate, c.CusName, o.ShippingAddress, o.TotalAmount, o.OrderStatus
                FROM [Order] o
                LEFT JOIN Customer c ON c.CustomerID = o.CustomerID
                ORDER BY o.OrderDate DESC, o.OrderID DESC
                """
            ).fetchall()
            self._fill_table(rows)
        finally:
            db.close()

    def search_orders(self):
        keyword = self.window.txtTimKiemDH.text().strip() if hasattr(self.window, "txtTimKiemDH") else ""
        start_date = self.window.txtTuNgayDH.date().toPyDate() if hasattr(self.window, "txtTuNgayDH") else None
        end_date = self.window.txtDenNgayDH.date().toPyDate() if hasattr(self.window, "txtDenNgayDH") else None

        db = Database()
        try:
            query = """
                SELECT o.OrderID, o.OrderDate, c.CusName, o.ShippingAddress, o.TotalAmount, o.OrderStatus
                FROM [Order] o
                LEFT JOIN Customer c ON c.CustomerID = o.CustomerID
                WHERE 1 = 1
            """
            params = []

            if keyword:
                like_value = f"%{keyword}%"
                query += " AND (CAST(o.OrderID AS NVARCHAR(50)) LIKE ? OR c.CusName LIKE ? OR c.CusPhone LIKE ? OR o.ShippingAddress LIKE ? OR o.OrderStatus LIKE ?)"
                params.extend([like_value, like_value, like_value, like_value, like_value])

            if start_date:
                query += " AND o.OrderDate >= ?"
                params.append(start_date)

            if end_date:
                query += " AND o.OrderDate <= ?"
                params.append(end_date)

            query += " ORDER BY o.OrderDate DESC, o.OrderID DESC"
            rows = db.execute(query, tuple(params)).fetchall()
            self._fill_table(rows)
        finally:
            db.close()

    def _fill_table(self, rows):
        table = self.window.tblDonHang
        table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            table.setItem(row_idx, 0, QTableWidgetItem(str(row[0] or "")))
            table.setItem(row_idx, 1, QTableWidgetItem(_format_date(row[1])))
            table.setItem(row_idx, 2, QTableWidgetItem(str(row[2] or "")))
            table.setItem(row_idx, 3, QTableWidgetItem(str(row[3] or "")))
            table.setItem(row_idx, 4, QTableWidgetItem(_format_currency(row[4])))
            table.setItem(row_idx, 5, QTableWidgetItem(str(row[5] or "")))
        self._update_button_state()

    def _selected_order_id(self):
        selected_rows = self.window.tblDonHang.selectionModel().selectedRows()
        if not selected_rows:
            return None
        item = self.window.tblDonHang.item(selected_rows[0].row(), 0)
        return int(item.text()) if item and item.text().strip().isdigit() else None

    def _restore_inventory_for_order(self, db, order_id):
        detail_rows = db.execute(
            "SELECT ProductID, Quantity FROM Order_Detail WHERE OrderID = ? ORDER BY ProductID",
            (int(order_id),),
        ).fetchall()
        for detail_row in detail_rows:
            product_id = int(detail_row[0])
            quantity = int(detail_row[1])
            map_row = db.execute(
                "SELECT WarehouseID FROM OrderDetailInventoryMap WHERE OrderID = ? AND ProductID = ?",
                (int(order_id), product_id),
            ).fetchone()
            warehouse_id = int(map_row[0]) if map_row else None
            if warehouse_id is None:
                warehouse_id, _ = _best_warehouse(db, product_id, 1)
            if warehouse_id is not None:
                _adjust_inventory(db, product_id, warehouse_id, quantity)
            db.execute("DELETE FROM OrderDetailInventoryMap WHERE OrderID = ? AND ProductID = ?", (int(order_id), product_id))

    def open_add_order_dialog(self):
        try:
            dialog = OrderDetailDialog(self.window)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_order_table()
        except Exception as exc:
            self._show_error(self.window, "Lỗi đơn hàng", exc)

    def open_update_order_dialog(self):
        try:
            order_id = self._selected_order_id()
            if order_id is None:
                QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một đơn hàng để cập nhật.")
                return

            db = Database()
            try:
                order = db.execute(
                    "SELECT OrderID, OrderDate, TotalAmount, OrderStatus, ShippingAddress, CustomerID, EmployeeID FROM [Order] WHERE OrderID = ?",
                    (order_id,),
                ).fetchone()
            finally:
                db.close()

            if not order:
                QMessageBox.warning(self.window, "Thông báo", "Đơn hàng không tồn tại.")
                return

            dialog = OrderDetailDialog(self.window, order=order)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_order_table()
        except Exception as exc:
            self._show_error(self.window, "Lỗi đơn hàng", exc)

    def delete_order(self):
        try:
            order_id = self._selected_order_id()
            if order_id is None:
                QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một đơn hàng để xóa.")
                return

            answer = QMessageBox.question(
                self.window,
                "Xác nhận xóa",
                "Bạn có chắc chắn muốn xóa đơn hàng này không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

            db = Database()
            try:
                _ensure_support_tables(db)
                self._restore_inventory_for_order(db, order_id)
                db.execute("DELETE FROM Order_Detail WHERE OrderID = ?", (order_id,))
                db.execute("DELETE FROM Payment WHERE OrderID = ?", (order_id,))
                db.execute("DELETE FROM Shipment WHERE OrderID = ?", (order_id,))
                db.execute("DELETE FROM [Order] WHERE OrderID = ?", (order_id,))
                db.commit()
            except Exception as exc:
                db.rollback()
                raise exc
            finally:
                db.close()

            QMessageBox.information(self.window, "Thành công", "Đã xóa đơn hàng thành công.")
            self.load_order_table()
        except Exception as exc:
            self._show_error(self.window, "Lỗi đơn hàng", exc)