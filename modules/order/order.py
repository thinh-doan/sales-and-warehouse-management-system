from datetime import date

from PyQt6 import QtCore
from PyQt6.QtWidgets import QAbstractItemView, QDialog, QMessageBox, QTableWidgetItem

from connect import Database
from modules.order.order_add_ord_detail_ui import Ui_hopThoaiThemSP
from modules.order.order_detail_ui import Ui_hopThoaiDonHang


class OrderItemDialog(QDialog, Ui_hopThoaiThemSP):
    def __init__(self, parent=None, order_id=None, detail=None):
        super().__init__(parent)
        self.setupUi(self)
        self.order_id = order_id
        self.detail = detail
        self.products = []
        self._connect_signals()
        self._load_products()
        self._populate_form()

    def _connect_signals(self):
        self.buttonBox.accepted.connect(self._save_item)
        self.buttonBox.rejected.connect(self.reject)
        self.cboSanPham.currentIndexChanged.connect(self._on_product_changed)

    def _load_products(self):
        db = Database()
        try:
            cursor = db.execute("SELECT ProductID, ProductName, ProductUnitPrice FROM Product WHERE ProductStatus IS NOT NULL ORDER BY ProductName")
            rows = cursor.fetchall()
            self.cboSanPham.clear()
            self.products = []
            for row in rows:
                self.products.append((row[0], row[1], float(row[2] or 0)))
                self.cboSanPham.addItem(row[1], row[0])
        finally:
            db.close()

    def _populate_form(self):
        if self.detail:
            product_id = self.detail[0]
            quantity = self.detail[2]
            self._set_selected_product(product_id)
            self.txtSoLuong.setValue(int(quantity))
            self.setWindowTitle("Cập nhật sản phẩm trong đơn hàng")
        else:
            self.setWindowTitle("Thêm sản phẩm vào đơn hàng")
            if self.products:
                self._on_product_changed()

    def _set_selected_product(self, product_id):
        for index in range(self.cboSanPham.count()):
            if self.cboSanPham.itemData(index) == product_id:
                self.cboSanPham.setCurrentIndex(index)
                break

    def _on_product_changed(self):
        product_id = self.cboSanPham.currentData()
        for item in self.products:
            if item[0] == product_id:
                self.txtMaSP.setText(str(item[0]))
                break
        else:
            self.txtMaSP.clear()

    def _save_item(self):
        if not self.order_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng lưu đơn hàng trước khi thêm sản phẩm.")
            return

        product_id = self.cboSanPham.currentData()
        quantity = self.txtSoLuong.value()
        if product_id is None:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn sản phẩm.")
            return

        db = Database()
        try:
            product_row = None
            for item in self.products:
                if item[0] == product_id:
                    product_row = item
                    break
            if product_row is None:
                raise ValueError("Không tìm thấy sản phẩm")

            unit_price = product_row[2]
            if self.detail:
                db.execute(
                    "UPDATE Order_Detail SET Quantity = ?, OrderDetailUnitPrice = ? WHERE OrderID = ? AND ProductID = ?",
                    (quantity, unit_price, self.order_id, product_id),
                )
            else:
                db.execute(
                    "INSERT INTO Order_Detail (OrderID, ProductID, Quantity, OrderDetailUnitPrice) VALUES (?, ?, ?, ?)",
                    (self.order_id, product_id, quantity, unit_price),
                )
            self._refresh_order_total(db)
            db.commit()
            self.accept()
        except Exception as exc:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu sản phẩm vào đơn hàng.\nChi tiết: {exc}")
        finally:
            db.close()

    def _refresh_order_total(self, db):
        cursor = db.execute(
            "SELECT COALESCE(SUM(Quantity * OrderDetailUnitPrice), 0) FROM Order_Detail WHERE OrderID = ?",
            (self.order_id,),
        )
        total = cursor.fetchone()[0] or 0
        db.execute("UPDATE [Order] SET TotalAmount = ? WHERE OrderID = ?", (total, self.order_id))


class OrderDetailDialog(QDialog, Ui_hopThoaiDonHang):
    def __init__(self, parent=None, order=None):
        super().__init__(parent)
        self.setupUi(self)
        self.order = order
        self.order_id = order[0] if order else None
        self._connect_signals()
        self._load_lookup_data()
        self._populate_form()

    def _connect_signals(self):
        self.btnLuuDH.clicked.connect(self._save_order)
        self.btnHuyDH.clicked.connect(self.reject)
        if hasattr(self, "btnThemDH"):
            self.btnThemDH.clicked.connect(self._open_add_detail_dialog)
        if hasattr(self, "btnThemSP"):
            self.btnThemSP.clicked.connect(self._open_add_detail_dialog)
        if hasattr(self, "btnCapNhatSP"):
            self.btnCapNhatSP.clicked.connect(self._open_update_detail_dialog)
        if hasattr(self, "btnXoaSP"):
            self.btnXoaSP.clicked.connect(self._delete_selected_detail)
        self.tblOrderDetail.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblOrderDetail.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def _load_lookup_data(self):
        db = Database()
        try:
            customer_cursor = db.execute("SELECT CustomerID, CusPhone FROM Customer ORDER BY CustomerID")
            self.cboKhachHang.clear()
            for row in customer_cursor.fetchall():
                self.cboKhachHang.addItem(str(row[1] or row[0]), row[0])

            employee_cursor = db.execute("SELECT EmployeeID, EmpName FROM Employee ORDER BY EmployeeID")
            self.cboNhanVien.clear()
            for row in employee_cursor.fetchall():
                self.cboNhanVien.addItem(str(row[1] or row[0]), row[0])

            self.cboTrangThai.clear()
            for status in ["Chờ xử lý", "Đang chuẩn bị", "Đang giao", "Hoàn thành", "Đã hủy"]:
                self.cboTrangThai.addItem(status, status)

            self.cboPhuongThucTT.clear()
            for method in ["Tiền mặt", "Chuyển khoản", "Thẻ"]:
                self.cboPhuongThucTT.addItem(method, method)

            self.cboTrangThaiTT.clear()
            for status in ["Chưa thanh toán", "Đã thanh toán", "Đang chờ"]:
                self.cboTrangThaiTT.addItem(status, status)

            partner_cursor = db.execute("SELECT PartnerID, PrtName FROM Delivery_Partner ORDER BY PartnerID")
            self.cboDoiTac.clear()
            for row in partner_cursor.fetchall():
                self.cboDoiTac.addItem(str(row[1] or row[0]), row[0])

            self.cboPhuongThucVanChuyen.clear()
            for method in ["Giao hàng tiêu chuẩn", "Giao hàng nhanh", "Nhận tại cửa hàng"]:
                self.cboPhuongThucVanChuyen.addItem(method, method)
        finally:
            db.close()

    def _populate_form(self):
        if self.order:
            self.setWindowTitle("Cập nhật đơn hàng")
            self._load_order_header()
            self._load_order_details()
        else:
            self.setWindowTitle("Tạo đơn hàng")
            self.txtNgayDatHang.setDate(date.today())
            self.cboTrangThai.setCurrentIndex(0)
            self.cboPhuongThucTT.setCurrentIndex(0)
            self.cboTrangThaiTT.setCurrentIndex(0)
            self.cboPhuongThucVanChuyen.setCurrentIndex(0)
            self.txtTamTinh.setText("0")
            self.txtTongTT.setText("0")
            self.txtPhiVanChuyen.setText("0")
            self._load_order_details()

    def _load_order_header(self):
        if not self.order_id:
            return
        db = Database()
        try:
            cursor = db.execute(
                """
                SELECT o.OrderID, o.OrderDate, o.TotalAmount, o.OrderStatus, o.ShippingAddress, o.CustomerID, o.EmployeeID,
                       p.PaymentMethod, p.PaymentStatus, s.PartnerID, s.ShipmentMethod, s.ShippingFee
                FROM [Order] o
                LEFT JOIN Payment p ON p.OrderID = o.OrderID
                LEFT JOIN Shipment s ON s.OrderID = o.OrderID
                WHERE o.OrderID = ?
                """,
                (self.order_id,),
            )
            row = cursor.fetchone()
            if not row:
                return
            self.txtNgayDatHang.setDate(row[1])
            self.txtDiaChiGH.setText(str(row[4] or ""))
            self.txtTamTinh.setText(f"{row[2] or 0:,.0f}")
            self.txtTongTT.setText(f"{row[2] or 0:,.0f}")
            self._set_combo_value(self.cboKhachHang, row[5])
            self._set_combo_value(self.cboNhanVien, row[6])
            self._set_combo_value(self.cboTrangThai, row[3])
            self._set_combo_value(self.cboPhuongThucTT, row[7])
            self._set_combo_value(self.cboTrangThaiTT, row[8])
            self._set_combo_value(self.cboDoiTac, row[9])
            self._set_combo_value(self.cboPhuongThucVanChuyen, row[10])
            self.txtPhiVanChuyen.setText(str(row[11] or 0))
        finally:
            db.close()

    def _load_order_details(self):
        self.tblOrderDetail.setRowCount(0)
        if not self.order_id:
            return
        db = Database()
        try:
            cursor = db.execute(
                """
                SELECT od.ProductID, p.ProductName, od.Quantity, od.OrderDetailUnitPrice,
                       od.Quantity * od.OrderDetailUnitPrice AS ThanhTien, i.QuantityInStock
                FROM Order_Detail od
                JOIN Product p ON p.ProductID = od.ProductID
                LEFT JOIN Inventory i ON i.ProductID = od.ProductID
                WHERE od.OrderID = ?
                ORDER BY od.ProductID
                """,
                (self.order_id,),
            )
            rows = cursor.fetchall()
            self.tblOrderDetail.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                self.tblOrderDetail.setItem(row_idx, 0, QTableWidgetItem(str(row[0] or "")))
                self.tblOrderDetail.setItem(row_idx, 1, QTableWidgetItem(str(row[1] or "")))
                self.tblOrderDetail.setItem(row_idx, 2, QTableWidgetItem(str(row[2] or "")))
                self.tblOrderDetail.setItem(row_idx, 3, QTableWidgetItem(f"{row[3] or 0:,.0f}"))
                self.tblOrderDetail.setItem(row_idx, 4, QTableWidgetItem(f"{row[4] or 0:,.0f}"))
                self.tblOrderDetail.setItem(row_idx, 5, QTableWidgetItem(str(row[5] or "")))
        finally:
            db.close()

    def _set_combo_value(self, combo, value):
        if value is None:
            return
        for index in range(combo.count()):
            if combo.itemData(index) == value or combo.itemText(index) == str(value):
                combo.setCurrentIndex(index)
                break

    def _open_add_detail_dialog(self):
        if not self.order_id:
            QMessageBox.information(self, "Thông báo", "Vui lòng lưu đơn hàng trước khi thêm sản phẩm.")
            return
        dialog = OrderItemDialog(self, order_id=self.order_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_order_details()
            self._refresh_totals_from_db()

    def _open_update_detail_dialog(self):
        selected_rows = self.tblOrderDetail.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một dòng sản phẩm để cập nhật.")
            return
        row = selected_rows[0].row()
        product_id = self.tblOrderDetail.item(row, 0).text()
        quantity = int(self.tblOrderDetail.item(row, 2).text() or 0)
        detail = (int(product_id), None, quantity)
        dialog = OrderItemDialog(self, order_id=self.order_id, detail=detail)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_order_details()
            self._refresh_totals_from_db()

    def _delete_selected_detail(self):
        selected_rows = self.tblOrderDetail.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một dòng sản phẩm để xóa.")
            return
        answer = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn xóa sản phẩm này khỏi đơn hàng không?")
        if answer != QMessageBox.StandardButton.Yes:
            return

        row = selected_rows[0].row()
        product_id = self.tblOrderDetail.item(row, 0).text()
        db = Database()
        try:
            db.execute("DELETE FROM Order_Detail WHERE OrderID = ? AND ProductID = ?", (self.order_id, int(product_id)))
            self._refresh_order_total(db)
            db.commit()
            self._load_order_details()
            self._refresh_totals_from_db()
        except Exception as exc:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa sản phẩm khỏi đơn hàng.\nChi tiết: {exc}")
        finally:
            db.close()

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
        shipping_fee = float(self.txtPhiVanChuyen.text().replace(",", "") or 0)

        if not customer_id or not employee_id or not shipping_address:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ thông tin khách hàng, nhân viên và địa chỉ giao hàng.")
            return

        db = Database()
        try:
            if self.order_id:
                db.execute(
                    "UPDATE [Order] SET OrderDate = ?, OrderStatus = ?, ShippingAddress = ?, CustomerID = ?, EmployeeID = ? WHERE OrderID = ?",
                    (order_date, order_status, shipping_address, customer_id, employee_id, self.order_id),
                )
            else:
                self.order_id = self._get_next_id(db, "[Order]", "OrderID")
                db.execute(
                    "INSERT INTO [Order] (OrderID, OrderDate, TotalAmount, OrderStatus, ShippingAddress, CustomerID, EmployeeID) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (self.order_id, order_date, 0, order_status, shipping_address, customer_id, employee_id),
                )

            self._refresh_order_total(db)
            self._upsert_payment(db, self.order_id, order_date, payment_method, payment_status)
            self._upsert_shipment(db, self.order_id, order_date, shipment_method, partner_id, shipping_fee, employee_id)
            db.commit()
            QMessageBox.information(self, "Thành công", "Lưu đơn hàng thành công.")
            self.accept()
        except Exception as exc:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu đơn hàng.\nChi tiết: {exc}")
        finally:
            db.close()

    def _refresh_order_total(self, db):
        cursor = db.execute(
            "SELECT COALESCE(SUM(Quantity * OrderDetailUnitPrice), 0) FROM Order_Detail WHERE OrderID = ?",
            (self.order_id,),
        )
        total = cursor.fetchone()[0] or 0
        db.execute("UPDATE [Order] SET TotalAmount = ? WHERE OrderID = ?", (total, self.order_id))
        self.txtTamTinh.setText(f"{total:,.0f}")
        self.txtTongTT.setText(f"{total + float(self.txtPhiVanChuyen.text().replace(',', '') or 0):,.0f}")

    def _refresh_totals_from_db(self):
        db = Database()
        try:
            cursor = db.execute("SELECT TotalAmount FROM [Order] WHERE OrderID = ?", (self.order_id,))
            row = cursor.fetchone()
            if row:
                total = row[0] or 0
                self.txtTamTinh.setText(f"{total:,.0f}")
                self.txtTongTT.setText(f"{float(total) + float(self.txtPhiVanChuyen.text().replace(',', '') or 0):,.0f}")
        finally:
            db.close()

    def _upsert_payment(self, db, order_id, order_date, payment_method, payment_status):
        cursor = db.execute("SELECT PaymentID FROM Payment WHERE OrderID = ?", (order_id,))
        payment_row = cursor.fetchone()
        total_amount = self._read_total_amount()
        if payment_row:
            db.execute(
                "UPDATE Payment SET PaymentDate = ?, Amount = ?, PaymentMethod = ?, PaymentStatus = ? WHERE OrderID = ?",
                (order_date, total_amount, payment_method, payment_status, order_id),
            )
        else:
            payment_id = self._get_next_id(db, "Payment", "PaymentID")
            db.execute(
                "INSERT INTO Payment (PaymentID, PaymentDate, Amount, PaymentMethod, PaymentStatus, OrderID) VALUES (?, ?, ?, ?, ?, ?)",
                (payment_id, order_date, total_amount, payment_method, payment_status, order_id),
            )

    def _upsert_shipment(self, db, order_id, order_date, shipment_method, partner_id, shipping_fee, employee_id):
        cursor = db.execute("SELECT ShipmentID FROM Shipment WHERE OrderID = ?", (order_id,))
        shipment_row = cursor.fetchone()
        if shipment_row:
            db.execute(
                "UPDATE Shipment SET ShipmentDate = ?, ExpectedDeliveryDate = ?, ActualDeliveryDate = ?, ShippingFee = ?, ShipmentStatus = ?, ShipmentMethod = ?, PartnerID = ?, EmployeeID = ? WHERE OrderID = ?",
                (order_date, None, None, shipping_fee, "Đang chuẩn bị", shipment_method, partner_id or 1, employee_id, order_id),
            )
        else:
            shipment_id = self._get_next_id(db, "Shipment", "ShipmentID")
            db.execute(
                "INSERT INTO Shipment (ShipmentID, ShipmentDate, ExpectedDeliveryDate, ActualDeliveryDate, ShippingFee, ShipmentStatus, ShipmentMethod, OrderID, PartnerID, EmployeeID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (shipment_id, order_date, None, None, shipping_fee, "Đang chuẩn bị", shipment_method, order_id, partner_id or 1, employee_id),
            )

    def _read_total_amount(self):
        try:
            return float(self.txtTamTinh.text().replace(",", "") or 0)
        except ValueError:
            return 0.0

    def _get_next_id(self, db, table_name, column_name):
        cursor = db.execute(f"SELECT COALESCE(MAX({column_name}), 0) FROM {table_name}")
        return (cursor.fetchone()[0] or 0) + 1


class OrderPageController:
    def __init__(self, window):
        self.window = window
        self._connect_signals()
        self._prepare_table()
        self.load_order_table()

    def _connect_signals(self):
        self.window.btnThemDH.clicked.connect(self.open_add_order_dialog)
        self.window.btnCapNhatDH.clicked.connect(self.open_update_order_dialog)
        self.window.btnXoaDH.clicked.connect(self.delete_order)
        self.window.btnRefreshDH.clicked.connect(self.load_order_table)
        self.window.btnTimKiemDH.clicked.connect(self.search_orders)
        if hasattr(self.window, "txtTimKiemDH"):
            self.window.txtTimKiemDH.returnPressed.connect(self.search_orders)
        if hasattr(self.window, "txtTuNgayDH") and hasattr(self.window, "txtDenNgayDH"):
            self.window.txtTuNgayDH.dateChanged.connect(lambda _: self.search_orders())
            self.window.txtDenNgayDH.dateChanged.connect(lambda _: self.search_orders())
        self.window.tblDonHang.itemSelectionChanged.connect(self._update_button_state)

    def _prepare_table(self):
        table = self.window.tblDonHang
        table.setColumnCount(6)
        headers = ["Mã ĐH", "Ngày tạo", "Khách hàng", "Địa chỉ", "Tổng tiền", "Trạng thái"]
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setColumnWidth(0, 90)
        table.setColumnWidth(1, 100)
        table.setColumnWidth(2, 160)
        table.setColumnWidth(3, 220)
        table.setColumnWidth(4, 110)
        table.setColumnWidth(5, 140)
        self._update_button_state()

    def _update_button_state(self):
        has_selection = self.window.tblDonHang.selectionModel().hasSelection()
        for button_name in ["btnCapNhatDH", "btnXoaDH"]:
            button = getattr(self.window, button_name, None)
            if button:
                button.setEnabled(has_selection)
        if hasattr(self.window, "btnChiTietDH"):
            self.window.btnChiTietDH.setEnabled(has_selection)

    def load_order_table(self):
        db = Database()
        try:
            query = """
                SELECT o.OrderID, o.OrderDate, c.CusPhone, o.ShippingAddress, o.TotalAmount, o.OrderStatus
                FROM [Order] o
                LEFT JOIN Customer c ON c.CustomerID = o.CustomerID
                ORDER BY o.OrderDate DESC, o.OrderID DESC
            """
            cursor = db.execute(query)
            rows = cursor.fetchall()
            self._fill_table(rows)
        finally:
            db.close()

    def search_orders(self):
        keyword = self.window.txtTimKiemDH.text().strip()
        start_date = self.window.txtTuNgayDH.date().toPyDate()
        end_date = self.window.txtDenNgayDH.date().toPyDate()
        db = Database()
        try:
            base_query = """
                SELECT o.OrderID, o.OrderDate, c.CusPhone, o.ShippingAddress, o.TotalAmount, o.OrderStatus
                FROM [Order] o
                LEFT JOIN Customer c ON c.CustomerID = o.CustomerID
                WHERE 1 = 1
            """
            params = []
            if keyword:
                base_query += " AND CAST(o.OrderID AS NVARCHAR) LIKE ?"
                params.append(f"%{keyword}%")
            if start_date:
                base_query += " AND o.OrderDate >= ?"
                params.append(start_date)
            if end_date:
                base_query += " AND o.OrderDate <= ?"
                params.append(end_date)
            base_query += " ORDER BY o.OrderDate DESC, o.OrderID DESC"
            cursor = db.execute(base_query, tuple(params))
            rows = cursor.fetchall()
            self._fill_table(rows)
        finally:
            db.close()

    def _fill_table(self, rows):
        table = self.window.tblDonHang
        table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            table.setItem(row_idx, 0, QTableWidgetItem(str(row[0] or "")))
            table.setItem(row_idx, 1, QTableWidgetItem(row[1].strftime("%d/%m/%Y") if row[1] else ""))
            table.setItem(row_idx, 2, QTableWidgetItem(str(row[2] or "")))
            table.setItem(row_idx, 3, QTableWidgetItem(str(row[3] or "")))
            table.setItem(row_idx, 4, QTableWidgetItem(f"{row[4] or 0:,.0f}"))
            table.setItem(row_idx, 5, QTableWidgetItem(str(row[5] or "")))
        self._update_button_state()

    def open_add_order_dialog(self):
        dialog = OrderDetailDialog(self.window)
        dialog.exec()
        self.load_order_table()

    def open_update_order_dialog(self):
        selected_rows = self.window.tblDonHang.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một đơn hàng để cập nhật.")
            return
        order_id = int(self.window.tblDonHang.item(selected_rows[0].row(), 0).text())
        db = Database()
        try:
            cursor = db.execute("SELECT OrderID, OrderDate, TotalAmount, OrderStatus, ShippingAddress, CustomerID, EmployeeID FROM [Order] WHERE OrderID = ?", (order_id,))
            order = cursor.fetchone()
        finally:
            db.close()
        if not order:
            QMessageBox.warning(self.window, "Thông báo", "Đơn hàng không tồn tại.")
            return
        dialog = OrderDetailDialog(self.window, order=order)
        dialog.exec()
        self.load_order_table()

    def delete_order(self):
        selected_rows = self.window.tblDonHang.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một đơn hàng để xóa.")
            return
        order_id = int(self.window.tblDonHang.item(selected_rows[0].row(), 0).text())
        answer = QMessageBox.question(self.window, "Xác nhận xóa", "Bạn có chắc chắn muốn xóa đơn hàng này không?")
        if answer != QMessageBox.StandardButton.Yes:
            return

        db = Database()
        try:
            db.execute("DELETE FROM Order_Detail WHERE OrderID = ?", (order_id,))
            db.execute("DELETE FROM Payment WHERE OrderID = ?", (order_id,))
            db.execute("DELETE FROM Shipment WHERE OrderID = ?", (order_id,))
            db.execute("DELETE FROM [Order] WHERE OrderID = ?", (order_id,))
            db.commit()
            QMessageBox.information(self.window, "Thành công", "Đã xóa đơn hàng thành công.")
            self.load_order_table()
        except Exception as exc:
            db.rollback()
            QMessageBox.critical(self.window, "Lỗi", f"Không thể xóa đơn hàng.\nChi tiết: {exc}")
        finally:
            db.close()
