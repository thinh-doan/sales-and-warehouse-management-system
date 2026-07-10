import pyodbc
from datetime import date

from PyQt6.QtWidgets import QAbstractItemView, QDialog, QMessageBox, QTableWidgetItem

from connect import Database
from modules.product.product_add_ui import Ui_hopThoaiMacDinh
from modules.product.product_detail_ui import Ui_khungMacDinh


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


def _ensure_inventory_change_log(db):
    db.execute(
        """
        IF OBJECT_ID(N'dbo.Inventory_Change_Log', N'U') IS NULL
        BEGIN
            CREATE TABLE dbo.Inventory_Change_Log (
                LogID INT IDENTITY(1,1) PRIMARY KEY,
                ProductID INT NOT NULL,
                WarehouseID INT NULL,
                ChangeType NVARCHAR(10) NOT NULL,
                ChangeQuantity INT NOT NULL,
                EmployeeName NVARCHAR(100) NOT NULL,
                Note NVARCHAR(255) NULL,
                ChangedAt DATETIME2 NOT NULL CONSTRAINT DF_Inventory_ChangeLog_ChangedAt DEFAULT SYSDATETIME()
            );
        END
        """
    )


def _populate_warehouse_combo(combo):
    db = Database()
    try:
        rows = db.execute("SELECT WarehouseID, WarehouseName FROM Warehouse ORDER BY WarehouseID").fetchall()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Chọn kho", None)
        for row in rows:
            combo.addItem(str(row[1] or ""), row[0])
    except Exception:
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Chọn kho", None)
    finally:
        combo.blockSignals(False)
        db.close()


def _populate_category_combo(combo):
    db = Database()
    try:
        rows = db.execute("SELECT CategoryID, CategoryName FROM Category ORDER BY CategoryName").fetchall()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Tất cả", None)
        for row in rows:
            combo.addItem(str(row[1] or ""), row[0])
    except Exception:
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Tất cả", None)
    finally:
        combo.blockSignals(False)
        db.close()


def _populate_status_combo(combo):
    combo.blockSignals(True)
    combo.clear()
    combo.addItem("Tất cả", None)
    combo.addItem("Đang bán", "Đang bán")
    combo.addItem("Ngừng bán", "Ngừng bán")
    combo.blockSignals(False)


class ProductFormDialog(QDialog, Ui_hopThoaiMacDinh):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setupUi(self)
        self.product = product
        self._original_warehouse_id = None
        self._connect_signals()
        _populate_warehouse_combo(self.cbbKhoSP)
        self._prepare_form()

    def _connect_signals(self):
        self.btnLuuSP.clicked.connect(self._save_product)
        self.btnHuySP.clicked.connect(self.reject)

    def _prepare_form(self):
        if self.product:
            self.setWindowTitle("Cập nhật sản phẩm")
            self.txtMaSP.setText(str(self.product[0] if self.product[0] is not None else ""))
            self.txtTenSP.setText(str(self.product[1] if self.product[1] is not None else ""))
            self.txtDanhMuc.setText(str(self.product[6] if self.product[6] is not None else ""))
            self.txtDonGia.setText(str(self.product[2] if self.product[2] is not None else ""))
            self.txtTonKho.setText(str(self.product[7] if self.product[7] is not None else "0"))
            self.txtDonVi.setText(str(self.product[3] if self.product[3] is not None else ""))
            self.txtMoTaSP.setText(str(self.product[4] if self.product[4] is not None else ""))
            self._original_warehouse_id = self.product[9] if len(self.product) > 9 else None
            self._set_warehouse_selection(self._original_warehouse_id)
            self.cbbKhoSP.setEnabled(False)
            self.txtMaSP.setReadOnly(True)
        else:
            self.setWindowTitle("Thêm sản phẩm")
            self.txtMaSP.clear()
            self.txtTenSP.clear()
            self.txtDanhMuc.clear()
            self.txtDonGia.clear()
            self.txtTonKho.clear()
            self.txtDonVi.clear()
            self.txtMoTaSP.clear()
            self.cbbKhoSP.setCurrentIndex(0)
            self.cbbKhoSP.setEnabled(True)
            self.txtMaSP.setReadOnly(False)

        self.txtTenSP.setReadOnly(False)
        self.txtDanhMuc.setReadOnly(False)
        self.txtDonGia.setReadOnly(False)
        self.txtTonKho.setReadOnly(False)
        self.txtDonVi.setReadOnly(False)

    def _set_warehouse_selection(self, warehouse_id):
        if warehouse_id is None:
            self.cbbKhoSP.setCurrentIndex(0)
            return
        index = self.cbbKhoSP.findData(int(warehouse_id))
        self.cbbKhoSP.setCurrentIndex(index if index >= 0 else 0)

    def _resolve_category_id(self, category_name):
        db = Database()
        try:
            row = db.execute("SELECT CategoryID FROM Category WHERE CategoryName = ?", (category_name,)).fetchone()
            return row[0] if row else None
        finally:
            db.close()

    def _save_inventory_history(self, db, product_id, warehouse_id, old_quantity, new_quantity):
        delta = int(new_quantity) - int(old_quantity)
        if delta == 0:
            return

        change_type = "Tăng" if delta > 0 else "Giảm"
        note = f"Cập nhật tồn kho từ {old_quantity} sang {new_quantity}"
        db.execute(
            """
            INSERT INTO Inventory_Change_Log (ProductID, WarehouseID, ChangeType, ChangeQuantity, EmployeeName, Note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (int(product_id), int(warehouse_id), change_type, abs(int(delta)), "Hệ thống", note),
        )

    def _save_product(self):
        product_id_text = self.txtMaSP.text().strip()
        product_name = self.txtTenSP.text().strip()
        category_name = self.txtDanhMuc.text().strip()
        unit_price_text = self.txtDonGia.text().strip()
        quantity_text = self.txtTonKho.text().strip()
        unit = self.txtDonVi.text().strip()
        description = self.txtMoTaSP.text().strip()
        warehouse_id = self._original_warehouse_id if self.product else self.cbbKhoSP.currentData()
        status = self.product[5] if self.product and len(self.product) > 5 and self.product[5] else "Đang bán"

        if not product_id_text or not product_name or not category_name or not unit_price_text or not quantity_text or not unit:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ dữ liệu sản phẩm.")
            return

        if warehouse_id is None:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn kho hợp lệ.")
            return

        try:
            product_id = int(product_id_text)
        except ValueError:
            QMessageBox.warning(self, "Thông báo", "Mã sản phẩm phải là số nguyên.")
            return

        try:
            unit_price = float(unit_price_text)
        except ValueError:
            QMessageBox.warning(self, "Thông báo", "Đơn giá phải là số hợp lệ.")
            return

        try:
            quantity = int(quantity_text)
        except ValueError:
            QMessageBox.warning(self, "Thông báo", "Tồn kho phải là số nguyên.")
            return

        category_id = self._resolve_category_id(category_name)
        if category_id is None:
            QMessageBox.warning(self, "Thông báo", "Danh mục không tồn tại. Vui lòng nhập đúng tên danh mục.")
            return

        today_str = date.today().strftime("%Y-%m-%d")
        db = Database()
        try:
            _ensure_inventory_change_log(db)

            if self.product:
                current_row = db.execute(
                    "SELECT QuantityInStock FROM Inventory WHERE ProductID = ? AND WarehouseID = ?",
                    (product_id, int(warehouse_id)),
                ).fetchone()
                old_quantity = int(current_row[0] if current_row else 0)

                db.execute(
                    """
                    UPDATE Product
                    SET ProductName = ?, ProductUnitPrice = ?, Unit = ?, ProductDescription = ?, ProductStatus = ?, CategoryID = ?
                    WHERE ProductID = ?
                    """,
                    (product_name, unit_price, unit, description if description else None, status, category_id, product_id),
                )

                if current_row:
                    db.execute(
                        """
                        UPDATE Inventory
                        SET QuantityInStock = ?, LastUpdated = ?
                        WHERE ProductID = ? AND WarehouseID = ?
                        """,
                        (quantity, today_str, product_id, int(warehouse_id)),
                    )
                else:
                    db.execute(
                        """
                        INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated)
                        VALUES (?, ?, ?, ?)
                        """,
                        (int(warehouse_id), product_id, quantity, today_str),
                    )

                self._save_inventory_history(db, product_id, int(warehouse_id), old_quantity, quantity)
            else:
                exists = db.execute("SELECT COUNT(1) FROM Product WHERE ProductID = ?", (product_id,)).fetchone()[0]
                if exists:
                    QMessageBox.warning(self, "Thông báo", "Mã sản phẩm đã tồn tại. Vui lòng dùng mã khác.")
                    return

                db.execute(
                    """
                    INSERT INTO Product (ProductID, ProductName, ProductUnitPrice, Unit, ProductDescription, ProductStatus, CategoryID)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (product_id, product_name, unit_price, unit, description if description else None, status, category_id),
                )
                db.execute(
                    """
                    INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated)
                    VALUES (?, ?, ?, ?)
                    """,
                    (int(warehouse_id), product_id, quantity, today_str),
                )
                db.execute(
                    """
                    INSERT INTO Inventory_Change_Log (ProductID, WarehouseID, ChangeType, ChangeQuantity, EmployeeName, Note)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        product_id,
                        int(warehouse_id),
                        "Tăng",
                        quantity,
                        "Hệ thống",
                        "Khởi tạo tồn kho sản phẩm mới",
                    ),
                )

            db.commit()
            QMessageBox.information(self, "Thành công", "Lưu sản phẩm thành công.")
            self.accept()
        except Exception as exc:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu sản phẩm.\nChi tiết: {exc}")
        finally:
            db.close()


class ProductDetailDialog(QDialog, Ui_khungMacDinh):
    def __init__(self, parent=None, product=None, editable=False):
        super().__init__(parent)
        self.setupUi(self)
        self.product = product
        self.editable = editable
        self.action_requested = None
        _populate_warehouse_combo(self.cbbKhoSP)
        self._connect_signals()
        self._prepare_ui_mode()
        self._fill_detail()

    def _connect_signals(self):
        self.btnCapNhatSP.clicked.connect(self._request_update)
        self.btnXoaSP.clicked.connect(self._request_delete)

    def _prepare_ui_mode(self):
        self.setWindowTitle("Cập nhật sản phẩm" if self.editable else "Chi tiết sản phẩm")
        self.txtMaSP.setEnabled(False)
        self.txtTenSP.setEnabled(self.editable)
        self.txtDanhMuc.setEnabled(self.editable)
        self.txtDonGia.setEnabled(self.editable)
        self.txtTonKho.setEnabled(self.editable)
        self.txtDonVi.setEnabled(self.editable)
        self.txtMoTaSP.setReadOnly(not self.editable)
        self.cbbKhoSP.setEnabled(self.editable)
        self.txtNgayTaoSP.setEnabled(False)
        self.txtTrangThaiSP.setEnabled(False)

    def _fill_detail(self):
        if not self.product:
            return

        self.txtMaSP.setText(str(self.product[0] if self.product[0] is not None else ""))
        self.txtTenSP.setText(str(self.product[1] if self.product[1] is not None else ""))
        self.txtDanhMuc.setText(str(self.product[6] if self.product[6] is not None else ""))
        self.txtDonGia.setText(str(self.product[2] if self.product[2] is not None else ""))
        self.txtTonKho.setText(str(self.product[7] if self.product[7] is not None else "0"))
        self.txtDonVi.setText(str(self.product[3] if self.product[3] is not None else ""))
        self.txtMoTaSP.setPlainText(str(self.product[4] if self.product[4] is not None else ""))
        self.txtTrangThaiSP.setText(str(self.product[5] if self.product[5] is not None else ""))
        self._set_warehouse_selection(self.product[9] if len(self.product) > 9 else None)

        created_date = self.product[10] if len(self.product) > 10 else (self.product[8] if len(self.product) > 8 else None)
        self.txtNgayTaoSP.setText(_format_date(created_date))

        self._load_sales_history()
        self._load_stock_history()

    def _set_warehouse_selection(self, warehouse_id):
        if warehouse_id is None:
            self.cbbKhoSP.setCurrentIndex(0)
            return
        index = self.cbbKhoSP.findData(int(warehouse_id))
        self.cbbKhoSP.setCurrentIndex(index if index >= 0 else 0)

    def _load_sales_history(self):
        self.tblLichSuBan.setRowCount(0)
        db = Database()
        try:
            rows = db.execute(
                """
                SELECT o.OrderID, o.OrderDate, c.CusName, od.Quantity, od.Quantity * od.OrderDetailUnitPrice
                FROM Order_Detail od
                JOIN [Order] o ON o.OrderID = od.OrderID
                LEFT JOIN Customer c ON c.CustomerID = o.CustomerID
                WHERE od.ProductID = ?
                ORDER BY o.OrderDate DESC, o.OrderID DESC
                """,
                (int(self.product[0]),),
            ).fetchall()
            self.tblLichSuBan.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                self.tblLichSuBan.setItem(row_idx, 0, QTableWidgetItem(str(row[0] or "")))
                self.tblLichSuBan.setItem(row_idx, 1, QTableWidgetItem(_format_date(row[1])))
                self.tblLichSuBan.setItem(row_idx, 2, QTableWidgetItem(str(row[2] or "")))
                self.tblLichSuBan.setItem(row_idx, 3, QTableWidgetItem(str(row[3] or 0)))
                self.tblLichSuBan.setItem(row_idx, 4, QTableWidgetItem(_format_currency(row[4])))
        except Exception:
            pass
        finally:
            db.close()

    def _load_stock_history(self):
        self.tblLichSuTonKho.setRowCount(0)
        db = Database()
        try:
            rows = db.execute(
                """
                SELECT h.EventDate, h.ChangeType, h.ChangeQty, h.Note
                FROM (
                    SELECT l.ChangedAt AS EventDate,
                           l.ChangeType,
                           ABS(l.ChangeQuantity) AS ChangeQty,
                           ISNULL(NULLIF(l.Note, N''), N'') AS Note
                    FROM Inventory_Change_Log l
                    WHERE l.ProductID = ?

                    UNION ALL

                    SELECT CAST(o.OrderDate AS DATETIME2) AS EventDate,
                           N'Giảm' AS ChangeType,
                           ABS(od.Quantity) AS ChangeQty,
                           N'Xuất kho theo đơn #' + CAST(o.OrderID AS NVARCHAR(20)) AS Note
                    FROM Order_Detail od
                    JOIN [Order] o ON o.OrderID = od.OrderID
                    WHERE od.ProductID = ?
                ) h
                ORDER BY h.EventDate DESC
                """,
                (int(self.product[0]), int(self.product[0])),
            ).fetchall()
            self.tblLichSuTonKho.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                self.tblLichSuTonKho.setItem(row_idx, 0, QTableWidgetItem(_format_date(row[0])))
                self.tblLichSuTonKho.setItem(row_idx, 1, QTableWidgetItem(str(row[1] or "")))
                self.tblLichSuTonKho.setItem(row_idx, 2, QTableWidgetItem(str(int(row[2] or 0))))
                self.tblLichSuTonKho.setItem(row_idx, 3, QTableWidgetItem(str(row[3] or "")))
        except Exception:
            pass
        finally:
            db.close()

    def _request_update(self):
        self.action_requested = "update"
        self.accept()

    def _request_delete(self):
        answer = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa sản phẩm này không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.action_requested = "delete"
            self.accept()


class ProductPageController:
    def __init__(self, window):
        self.window = window
        self._prepare_table()
        self._ensure_support_tables()
        self._populate_filters()
        self._connect_signals()
        self.load_product_table()

    @staticmethod
    def _show_error(parent, title, exc):
        QMessageBox.critical(parent, title, f"Đã xảy ra lỗi trong chức năng Sản phẩm.\n{exc}")

    def _create_db(self):
        return Database()

    def _ensure_support_tables(self):
        db = self._create_db()
        try:
            _ensure_inventory_change_log(db)
            db.commit()
        finally:
            db.close()

    def _prepare_table(self):
        self.window.bangSanPham.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.window.bangSanPham.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.window.bangSanPham.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def _connect_signals(self):
        self.window.btnThemSP.clicked.connect(self.open_add_product_dialog)
        self.window.btnChiTietSP.clicked.connect(self.open_product_detail_dialog)
        self.window.btnCapNhatSP.clicked.connect(self.open_update_product_dialog)
        self.window.btnXoaSP.clicked.connect(self.delete_product)
        self.window.btnRefreshSP.clicked.connect(self.refresh_product_table)
        self.window.btnTimKiemSP.clicked.connect(self.search_product)

        if hasattr(self.window, "txtTimKiemSP"):
            self.window.txtTimKiemSP.returnPressed.connect(self.search_product)

        if hasattr(self.window, "cbbDanhMuc"):
            self.window.cbbDanhMuc.currentIndexChanged.connect(lambda _: self.load_product_table())

        if hasattr(self.window, "cbbTrangThai"):
            self.window.cbbTrangThai.currentIndexChanged.connect(lambda _: self.load_product_table())

        self.window.bangSanPham.itemSelectionChanged.connect(self._update_action_buttons_state)
        self._update_action_buttons_state()

    def _populate_filters(self):
        if hasattr(self.window, "cbbDanhMuc"):
            _populate_category_combo(self.window.cbbDanhMuc)
        if hasattr(self.window, "cbbTrangThai"):
            _populate_status_combo(self.window.cbbTrangThai)

    def _get_selected_row_data(self):
        selected = self.window.bangSanPham.selectedItems()
        if not selected:
            return None, None
        row_idx = selected[0].row()
        product_item = self.window.bangSanPham.item(row_idx, 0)
        warehouse_item = self.window.bangSanPham.item(row_idx, 3)
        product_id = product_item.text().strip() if product_item else None
        warehouse_id = warehouse_item.text().strip() if warehouse_item else None
        return product_id, warehouse_id

    def _update_action_buttons_state(self):
        selected = bool(self.window.bangSanPham.selectedItems())
        self.window.btnChiTietSP.setEnabled(selected)
        self.window.btnCapNhatSP.setEnabled(selected)
        self.window.btnXoaSP.setEnabled(selected)

    def load_product_table(self):
        db = self._create_db()
        try:
            search_text = self.window.txtTimKiemSP.text().strip() if hasattr(self.window, "txtTimKiemSP") else ""
            category_id = self.window.cbbDanhMuc.currentData() if hasattr(self.window, "cbbDanhMuc") else None
            status_value = self.window.cbbTrangThai.currentData() if hasattr(self.window, "cbbTrangThai") else None

            query = """
                SELECT p.ProductID,
                       p.ProductName,
                       c.CategoryName,
                       i.WarehouseID,
                       COALESCE(i.QuantityInStock, 0) AS QuantityInStock,
                       p.ProductUnitPrice,
                       p.ProductStatus
                FROM Product p
                LEFT JOIN Category c ON p.CategoryID = c.CategoryID
                LEFT JOIN Inventory i ON p.ProductID = i.ProductID
                WHERE 1 = 1
            """
            params = []

            if search_text:
                if search_text.isdigit():
                    query += " AND p.ProductID = ?"
                    params.append(int(search_text))
                else:
                    query += " AND p.ProductName LIKE ?"
                    params.append(f"%{search_text}%")

            if category_id is not None:
                query += " AND p.CategoryID = ?"
                params.append(category_id)

            if status_value:
                query += " AND p.ProductStatus = ?"
                params.append(status_value)

            query += " ORDER BY p.ProductID, ISNULL(i.WarehouseID, 0)"

            rows = db.execute(query, tuple(params)).fetchall()
            self._render_product_table(rows)
        except Exception as exc:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải danh sách sản phẩm.\n{exc}")
        finally:
            db.close()

    def refresh_product_table(self):
        self.load_product_table()

    def _render_product_table(self, rows):
        self.window.bangSanPham.setRowCount(len(rows))
        self.window.bangSanPham.setColumnCount(7)

        for row_index, row in enumerate(rows):
            self.window.bangSanPham.setItem(row_index, 0, QTableWidgetItem(str(row[0] or "")))
            self.window.bangSanPham.setItem(row_index, 1, QTableWidgetItem(str(row[1] or "")))
            self.window.bangSanPham.setItem(row_index, 2, QTableWidgetItem(str(row[2] or "")))
            self.window.bangSanPham.setItem(row_index, 3, QTableWidgetItem(str(row[3] or "")))
            self.window.bangSanPham.setItem(row_index, 4, QTableWidgetItem(str(int(row[4] or 0))))
            self.window.bangSanPham.setItem(row_index, 5, QTableWidgetItem(_format_currency(row[5])))
            self.window.bangSanPham.setItem(row_index, 6, QTableWidgetItem(str(row[6] or "")))

        self._update_action_buttons_state()

    def _load_product_record(self, product_id, warehouse_id=None):
        if not product_id:
            return None

        db = self._create_db()
        try:
            if warehouse_id and str(warehouse_id).isdigit():
                row = db.execute(
                    """
                    SELECT p.ProductID,
                           p.ProductName,
                           p.ProductUnitPrice,
                           p.Unit,
                           p.ProductDescription,
                           p.ProductStatus,
                           c.CategoryName,
                           COALESCE(i.QuantityInStock, 0) AS QuantityInStock,
                           i.LastUpdated,
                           i.WarehouseID,
                           (SELECT MIN(i2.LastUpdated) FROM Inventory i2 WHERE i2.ProductID = p.ProductID) AS CreatedDate
                    FROM Product p
                    LEFT JOIN Category c ON p.CategoryID = c.CategoryID
                    LEFT JOIN Inventory i ON p.ProductID = i.ProductID AND i.WarehouseID = ?
                    WHERE p.ProductID = ?
                    """,
                    (int(warehouse_id), int(product_id)),
                ).fetchone()
            else:
                row = db.execute(
                    """
                    SELECT TOP 1
                           p.ProductID,
                           p.ProductName,
                           p.ProductUnitPrice,
                           p.Unit,
                           p.ProductDescription,
                           p.ProductStatus,
                           c.CategoryName,
                           COALESCE(i.QuantityInStock, 0) AS QuantityInStock,
                           i.LastUpdated,
                           i.WarehouseID,
                           (SELECT MIN(i2.LastUpdated) FROM Inventory i2 WHERE i2.ProductID = p.ProductID) AS CreatedDate
                    FROM Product p
                    LEFT JOIN Category c ON p.CategoryID = c.CategoryID
                    LEFT JOIN Inventory i ON p.ProductID = i.ProductID
                    WHERE p.ProductID = ?
                    ORDER BY ISNULL(i.WarehouseID, 0)
                    """,
                    (int(product_id),),
                ).fetchone()

            return row
        except Exception as exc:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải sản phẩm.\n{exc}")
            return None
        finally:
            db.close()

    def open_add_product_dialog(self):
        try:
            dialog = ProductFormDialog(self.window)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_product_table()
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)

    def open_product_detail_dialog(self):
        try:
            product_id, warehouse_id = self._get_selected_row_data()
            if not product_id:
                QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn sản phẩm để xem chi tiết.")
                return

            product = self._load_product_record(product_id, warehouse_id)
            if not product:
                return

            dialog = ProductDetailDialog(self.window, product=product, editable=False)
            dialog.exec()

            if dialog.action_requested == "update":
                self.open_update_product_dialog(product_id, warehouse_id)
            elif dialog.action_requested == "delete":
                self._confirm_delete_product(product_id)
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)

    def open_update_product_dialog(self, product_id=None, warehouse_id=None):
        try:
            if not product_id:
                product_id, warehouse_id = self._get_selected_row_data()

            if not product_id:
                QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn sản phẩm để cập nhật.")
                return

            product = self._load_product_record(product_id, warehouse_id)
            if not product:
                return

            dialog = ProductFormDialog(self.window, product=product)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_product_table()
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)

    def delete_product(self):
        try:
            product_id, _ = self._get_selected_row_data()
            if not product_id:
                QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn sản phẩm để xóa.")
                return
            self._confirm_delete_product(product_id)
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)

    def _confirm_delete_product(self, product_id):
        db = self._create_db()
        try:
            row = db.execute("SELECT ProductName FROM Product WHERE ProductID = ?", (int(product_id),)).fetchone()
            product_name = row[0] if row else ""
        except Exception as exc:
            self._show_error(self.window, "Lỗi xóa sản phẩm", exc)
            return
        finally:
            db.close()

        answer = QMessageBox.question(
            self.window,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa sản phẩm {product_name} ({product_id}) không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        db = self._create_db()
        try:
            _ensure_inventory_change_log(db)
            db.execute("DELETE FROM Inventory_Change_Log WHERE ProductID = ?", (int(product_id),))
            db.execute("DELETE FROM Inventory WHERE ProductID = ?", (int(product_id),))
            db.execute("DELETE FROM Order_Detail WHERE ProductID = ?", (int(product_id),))
            db.execute("DELETE FROM Product WHERE ProductID = ?", (int(product_id),))
            db.commit()
            QMessageBox.information(self.window, "Thành công", "Sản phẩm đã được xóa.")
            self.refresh_product_table()
        except pyodbc.Error as exc:
            db.rollback()
            QMessageBox.critical(self.window, "Lỗi xóa", f"Không thể xóa sản phẩm.\n{exc}")
        finally:
            db.close()

    def search_product(self):
        try:
            self.load_product_table()
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)