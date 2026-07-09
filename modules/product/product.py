import pyodbc
from datetime import date

from PyQt6 import QtCore
from PyQt6.QtWidgets import QAbstractItemView, QDialog, QMessageBox, QTableWidgetItem

from connect import Database
from modules.product.product_add_ui import Ui_hopThoaiMacDinh
from modules.product.product_detail_ui import Ui_khungMacDinh


class ProductFormDialog(QDialog, Ui_hopThoaiMacDinh):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setupUi(self)
        self.product = product
        self._connect_signals()
        self._prepare_form()

    def _connect_signals(self):
        self.btnLuuSP.clicked.connect(self._save_product)
        self.btnHuySP.clicked.connect(self.reject)

    def _prepare_form(self):
        if self.product:
            self.setWindowTitle("Cập nhật sản phẩm")
            self.txtMaSP.setText(str(self.product[0] or ""))
            self.txtTenSP.setText(str(self.product[1] or ""))
            # Mapping to columns returned by _load_product_record():
            # 0:ProductID,1:ProductName,2:ProductUnitPrice,3:Unit,4:ProductDescription,
            # 5:ProductStatus,6:CategoryName,7:QuantityInStock,8:LastUpdated
            self.txtDanhMuc.setText(str(self.product[6] or ""))
            self.txtDonGia.setText(str(self.product[2] or ""))
            self.txtTonKho.setText(str(self.product[7] or ""))
            self.txtDonVi.setText(str(self.product[3] or ""))
            self.txtMoTaSP.setText(str(self.product[4] or ""))
            # For update: only ProductID should be readonly; other fields editable
            self.txtMaSP.setReadOnly(True)
            self.txtTenSP.setReadOnly(False)
            self.txtDanhMuc.setReadOnly(False)
            self.txtDonGia.setReadOnly(False)
            self.txtTonKho.setReadOnly(False)
            self.txtDonVi.setReadOnly(False)
        else:
            self.setWindowTitle("Thêm sản phẩm")
            self.txtMaSP.setText("")
            self.txtTenSP.setText("")
            self.txtDanhMuc.setText("")
            self.txtDonGia.setText("")
            self.txtTonKho.setText("")
            self.txtDonVi.setText("")
            self.txtMoTaSP.setText("")
            # Make fields editable when adding
            self.txtMaSP.setReadOnly(False)
            self.txtTenSP.setReadOnly(False)
            self.txtDanhMuc.setReadOnly(False)
            self.txtDonGia.setReadOnly(False)
            self.txtTonKho.setReadOnly(False)
            self.txtDonVi.setReadOnly(False)

    def _save_product(self):
        product_id = self.txtMaSP.text().strip()
        product_name = self.txtTenSP.text().strip()
        category_name = self.txtDanhMuc.text().strip()
        unit_price = self.txtDonGia.text().strip()
        quantity = self.txtTonKho.text().strip()
        unit = self.txtDonVi.text().strip()
        description = self.txtMoTaSP.text().strip()
        status = "Đang bán"

        if not product_id or not product_name or not category_name or not unit_price or not quantity or not unit:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ dữ liệu sản phẩm.")
            return

        try:
            product_id_int = int(product_id)
        except ValueError:
            QMessageBox.warning(self, "Thông báo", "Mã sản phẩm phải là số nguyên.")
            return

        try:
            unit_price_val = float(unit_price)
        except ValueError:
            QMessageBox.warning(self, "Thông báo", "Đơn giá phải là số.")
            return

        try:
            quantity_int = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Thông báo", "Tồn kho phải là số nguyên.")
            return

        db = Database()
        try:
            # Resolve category id by name, fallback to NULL if not found
            cursor = db.execute("SELECT CategoryID FROM Category WHERE CategoryName = ?", (category_name,))
            category_row = cursor.fetchone()
            if category_row:
                category_id = category_row[0]
            else:
                QMessageBox.warning(self, "Thông báo", "Danh mục không tồn tại. Vui lòng chọn danh mục hợp lệ.")
                db.close()
                return

            if self.product:
                db.execute(
                    "UPDATE Product SET ProductName = ?, ProductUnitPrice = ?, Unit = ?, ProductDescription = ?, ProductStatus = ?, CategoryID = ? WHERE ProductID = ?",
                    (product_name, unit_price_val, unit, description if description else None, status, category_id, product_id_int),
                )
                cursor = db.execute("SELECT COUNT(1) FROM Inventory WHERE ProductID = ?", (product_id_int,))
                if cursor.fetchone()[0] > 0:
                    db.execute(
                        "UPDATE Inventory SET QuantityInStock = ?, LastUpdated = ? WHERE ProductID = ?",
                        (quantity_int, date.today(), product_id_int),
                    )
                else:
                    db.execute(
                        "INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated) VALUES (?, ?, ?, ?)",
                        (1, product_id_int, quantity_int, date.today()),
                    )
            else:
                cursor = db.execute("SELECT COUNT(1) FROM Product WHERE ProductID = ?", (product_id_int,))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Thông báo", "Mã sản phẩm đã tồn tại. Vui lòng dùng mã khác.")
                    db.close()
                    return

                db.execute(
                    "INSERT INTO Product (ProductID, ProductName, ProductUnitPrice, Unit, ProductDescription, ProductStatus, CategoryID) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (product_id_int, product_name, unit_price_val, unit, description if description else None, status, category_id),
                )
                cursor = db.execute("SELECT COUNT(1) FROM Inventory WHERE ProductID = ?", (product_id_int,))
                if cursor.fetchone()[0] == 0:
                    db.execute(
                        "INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated) VALUES (?, ?, ?, ?)",
                        (1, product_id_int, quantity_int, date.today()),
                    )
            db.commit()
            QMessageBox.information(self, "Thành công", "Lưu sản phẩm thành công.")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu sản phẩm.\nChi tiết: {e}")
        finally:
            db.close()


class ProductDetailDialog(QDialog, Ui_khungMacDinh):
    def __init__(self, parent=None, product=None, editable=False):
        super().__init__(parent)
        self.setupUi(self)
        self.product = product
        self.editable = editable
        self.action_requested = None
        self._prepare_ui_mode()
        # adjust stock history table to 3 columns (no Ghi chú)
        try:
            self.tblLichSuTonKho.setColumnCount(4)
            hdr0 = self.tblLichSuTonKho.horizontalHeaderItem(0)
            if hdr0:
                hdr0.setText("Ngày")
            hdr1 = self.tblLichSuTonKho.horizontalHeaderItem(1)
            if hdr1:
                hdr1.setText("Loại")
            hdr2 = self.tblLichSuTonKho.horizontalHeaderItem(2)
            if hdr2:
                hdr2.setText("Số lượng")
            hdr3 = self.tblLichSuTonKho.horizontalHeaderItem(3)
            if hdr3:
                hdr3.setText("Nhân viên")
        except Exception:
            pass

        self._fill_detail()
        self._connect_signals()

    def _prepare_ui_mode(self):
        if self.editable:
            self.setWindowTitle("Cập nhật sản phẩm")
        else:
            self.setWindowTitle("Chi tiết sản phẩm")

        self.txtMaSP.setEnabled(False)
        self.txtTenSP.setEnabled(self.editable)
        self.txtDanhMuc.setEnabled(self.editable)
        self.txtDonGia.setEnabled(self.editable)
        self.txtTonKho.setEnabled(self.editable)
        self.txtDonVi.setEnabled(self.editable)
        self.txtMoTaSP.setReadOnly(not self.editable)
        self.txtNgayTaoSP.setEnabled(False)
        self.txtTrangThaiSP.setEnabled(False)

    def _connect_signals(self):
        self.btnCapNhatSP.clicked.connect(self._request_update)
        self.btnXoaSP.clicked.connect(self._request_delete)

    def _fill_detail(self):
        if not self.product:
            return

        self.txtMaSP.setText(str(self.product[0] or ""))
        self.txtTenSP.setText(str(self.product[1] or ""))
        self.txtDanhMuc.setText(str(self.product[6] or ""))
        self.txtDonGia.setText(str(self.product[2] or ""))
        self.txtTonKho.setText(str(self.product[7] or ""))
        self.txtDonVi.setText(str(self.product[3] or ""))
        self.txtMoTaSP.setPlainText(str(self.product[4] or ""))
        self.txtNgayTaoSP.setText(str(self.product[8] or ""))
        self.txtTrangThaiSP.setText(str(self.product[5] or ""))

        self._load_sales_history()
        self._load_stock_history()

    def _load_sales_history(self):
        self.tblLichSuBan.setRowCount(0)
        db = Database()
        try:
            query = """
                SELECT o.OrderID, o.OrderDate, c.CusName, od.Quantity, od.Quantity * od.OrderDetailUnitPrice
                FROM [Order] o
                JOIN Order_Detail od ON o.OrderID = od.OrderID
                LEFT JOIN Customer c ON o.CustomerID = c.CustomerID
                WHERE od.ProductID = ?
                ORDER BY o.OrderDate DESC, o.OrderID DESC
            """
            cursor = db.execute(query, (self.product[0],))
            rows = cursor.fetchall()
            self.tblLichSuBan.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                self.tblLichSuBan.setItem(row_idx, 0, QTableWidgetItem(str(row[0] or "")))
                self.tblLichSuBan.setItem(row_idx, 1, QTableWidgetItem(row[1].strftime("%d/%m/%Y") if row[1] else ""))
                self.tblLichSuBan.setItem(row_idx, 2, QTableWidgetItem(str(row[2] or "")))
                self.tblLichSuBan.setItem(row_idx, 3, QTableWidgetItem(str(row[3] or "")))
                self.tblLichSuBan.setItem(row_idx, 4, QTableWidgetItem(f"{row[4]:,.0f}" if row[4] is not None else ""))
        except Exception:
            pass
        finally:
            db.close()

    def _load_stock_history(self):
        self.tblLichSuTonKho.setRowCount(0)
        db = Database()
        try:
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
                        ChangedAt DATETIME2 NOT NULL CONSTRAINT DF_InventoryChangeLog_ChangedAt DEFAULT SYSDATETIME()
                    );
                END
                """
            )
            db.commit()

            query = """
                SELECT h.EventDate,
                       h.ChangeType,
                       h.ChangeQty,
                       h.EmployeeName
                FROM (
                    SELECT l.ChangedAt AS EventDate,
                           l.ChangeType,
                          ABS(l.ChangeQuantity) AS ChangeQty,
                          ISNULL(NULLIF(l.EmployeeName, N''), N'Không rõ') AS EmployeeName
                    FROM Inventory_Change_Log l
                    WHERE l.ProductID = ?

                    UNION ALL

                    SELECT CAST(o.OrderDate AS DATETIME2) AS EventDate,
                           N'Giảm' AS ChangeType,
                          ABS(od.Quantity) AS ChangeQty,
                          ISNULL(e.EmpName, N'Không rõ') AS EmployeeName
                    FROM Order_Detail od
                    JOIN [Order] o ON o.OrderID = od.OrderID
                    LEFT JOIN Employee e ON e.EmployeeID = o.EmployeeID
                    WHERE od.ProductID = ?
                ) h
                ORDER BY h.EventDate DESC
            """
            cursor = db.execute(query, (self.product[0], self.product[0]))
            rows = cursor.fetchall()
            self.tblLichSuTonKho.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                self.tblLichSuTonKho.setItem(row_idx, 0, QTableWidgetItem(row[0].strftime("%d/%m/%Y") if row[0] else ""))
                self.tblLichSuTonKho.setItem(row_idx, 1, QTableWidgetItem(str(row[1] or "")))
                self.tblLichSuTonKho.setItem(row_idx, 2, QTableWidgetItem(str(int(row[2] or 0))))
                self.tblLichSuTonKho.setItem(row_idx, 3, QTableWidgetItem(str(row[3] or "Không rõ")))
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
        self._connect_signals()
        self._prepare_table()
        self._populate_filters()
        self.load_product_table()

    def _connect_signals(self):
        self.window.btnThemSP.clicked.connect(self.open_add_product_dialog)
        self.window.btnChiTietSP.clicked.connect(self.open_product_detail_dialog)
        self.window.btnCapNhatSP.clicked.connect(self.open_update_product_dialog)
        self.window.btnXoaSP.clicked.connect(self.delete_product)
        self.window.btnRefreshSP.clicked.connect(self.load_product_table)
        self.window.btnTimKiemSP.clicked.connect(self.search_product)
        if hasattr(self.window, 'txtTimKiemSP'):
            self.window.txtTimKiemSP.returnPressed.connect(self.search_product)
        if hasattr(self.window, 'cbbDanhMuc'):
            try:
                self.window.cbbDanhMuc.currentIndexChanged.connect(lambda _: self.load_product_table())
            except Exception:
                pass
        if hasattr(self.window, 'cbbTrangThai'):
            try:
                self.window.cbbTrangThai.currentIndexChanged.connect(lambda _: self.load_product_table())
            except Exception:
                pass
        self.window.bangSanPham.itemSelectionChanged.connect(self._update_action_buttons_state)
        self._update_action_buttons_state()

    def _prepare_table(self):
        self.window.bangSanPham.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.window.bangSanPham.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _create_db(self):
        return Database()

    def _get_selected_product_id(self):
        selected = self.window.bangSanPham.selectedItems()
        if not selected:
            return None
        item = self.window.bangSanPham.item(selected[0].row(), 0)
        return item.text().strip() if item else None

    def _update_action_buttons_state(self):
        selected = bool(self.window.bangSanPham.selectedItems())
        self.window.btnChiTietSP.setEnabled(selected)
        self.window.btnCapNhatSP.setEnabled(selected)
        self.window.btnXoaSP.setEnabled(selected)

    def load_product_table(self, product_id=None, product_name=None):
        db = self._create_db()
        try:
            # Aggregate inventory across warehouses to avoid duplicate product rows
            query = """
                SELECT p.ProductID, p.ProductName, c.CategoryName, p.ProductUnitPrice,
                       SUM(ISNULL(i.QuantityInStock, 0)) AS QuantityInStock, p.ProductStatus
                FROM Product p
                LEFT JOIN Inventory i ON p.ProductID = i.ProductID
                LEFT JOIN Category c ON p.CategoryID = c.CategoryID
                WHERE 1 = 1
            """
            params = []
            if product_id:
                query += " AND p.ProductID = ?"
                params.append(product_id)
            if product_name:
                query += " AND p.ProductName LIKE ?"
                params.append(f"%{product_name}%")
            # Apply category filter if selected
            try:
                cat_data = None
                if hasattr(self.window, 'cbbDanhMuc'):
                    cat_data = self.window.cbbDanhMuc.currentData()
                if cat_data:
                    query += " AND p.CategoryID = ?"
                    params.append(cat_data)
            except Exception:
                pass
            # Apply status filter if selected and not 'Tất cả'
            try:
                if hasattr(self.window, 'cbbTrangThai'):
                    status_txt = self.window.cbbTrangThai.currentText().strip()
                    if status_txt and status_txt != "Tất cả":
                        query += " AND p.ProductStatus = ?"
                        params.append(status_txt)
            except Exception:
                pass
            query += " GROUP BY p.ProductID, p.ProductName, c.CategoryName, p.ProductUnitPrice, p.ProductStatus"
            query += " ORDER BY p.ProductID"
            cursor = db.execute(query, params if params else None)
            rows = cursor.fetchall()
            self._render_product_table(rows)
        except Exception as e:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải danh sách sản phẩm.\n{e}")
        finally:
            db.close()

    def _render_product_table(self, rows):
        self.window.bangSanPham.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.window.bangSanPham.setItem(row_index, 0, QTableWidgetItem(str(row[0] or "")))
            self.window.bangSanPham.setItem(row_index, 1, QTableWidgetItem(str(row[1] or "")))
            self.window.bangSanPham.setItem(row_index, 2, QTableWidgetItem(str(row[2] or "")))
            self.window.bangSanPham.setItem(row_index, 3, QTableWidgetItem(str(row[3] or "")))
            self.window.bangSanPham.setItem(row_index, 4, QTableWidgetItem(str(row[4] or "")))
            self.window.bangSanPham.setItem(row_index, 5, QTableWidgetItem(str(row[5] or "")))
        self.window.bangSanPham.resizeColumnsToContents()
        self._update_action_buttons_state()

    def _populate_filters(self):
        # Fill category combobox with CategoryName and store CategoryID as data
        if not hasattr(self.window, 'cbbDanhMuc'):
            return
        db = self._create_db()
        try:
            cursor = db.execute("SELECT CategoryID, CategoryName FROM Category ORDER BY CategoryName")
            rows = cursor.fetchall()
            self.window.cbbDanhMuc.clear()
            self.window.cbbDanhMuc.addItem("Tất cả", None)
            for r in rows:
                self.window.cbbDanhMuc.addItem(str(r[1] or ""), r[0])
        except Exception:
            pass
        finally:
            db.close()

        # Fill status combobox
        try:
            self.window.cbbTrangThai.clear()
            self.window.cbbTrangThai.addItem("Tất cả")
            # Example statuses, adapt to actual values in Product.ProductStatus
            self.window.cbbTrangThai.addItem("Đang bán")
            self.window.cbbTrangThai.addItem("Ngừng bán")
        except Exception:
            pass

    def _load_product_record(self, product_id):
        if not product_id:
            return None
        db = self._create_db()
        try:
            # Aggregate inventory quantities for the product to present a single record
            cursor = db.execute(
                "SELECT p.ProductID, p.ProductName, p.ProductUnitPrice, p.Unit, p.ProductDescription, p.ProductStatus, c.CategoryName, ISNULL(SUM(i.QuantityInStock),0) AS QuantityInStock, MAX(i.LastUpdated) AS LastUpdated "
                "FROM Product p "
                "LEFT JOIN Inventory i ON p.ProductID = i.ProductID "
                "LEFT JOIN Category c ON p.CategoryID = c.CategoryID "
                "WHERE p.ProductID = ? "
                "GROUP BY p.ProductID, p.ProductName, p.ProductUnitPrice, p.Unit, p.ProductDescription, p.ProductStatus, c.CategoryName",
                (product_id,),
            )
            return cursor.fetchone()
        except Exception as e:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải sản phẩm.\n{e}")
            return None
        finally:
            db.close()

    def open_add_product_dialog(self):
        dialog = ProductFormDialog(self.window)
        if dialog.exec():
            self.load_product_table()

    def open_product_detail_dialog(self):
        product_id = self._get_selected_product_id()
        if not product_id:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn sản phẩm để xem chi tiết.")
            return
        product = self._load_product_record(product_id)
        if not product:
            return

        dialog = ProductDetailDialog(self.window, product=product, editable=False)
        dialog.exec()
        if dialog.action_requested == "delete":
            self._confirm_delete_product(product_id)
        elif dialog.action_requested == "update":
            self.open_update_product_dialog()

    def open_update_product_dialog(self):
        product_id = self._get_selected_product_id()
        if not product_id:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn sản phẩm để cập nhật.")
            return
        product = self._load_product_record(product_id)
        if not product:
            return

        dialog = ProductFormDialog(self.window, product=product)
        if dialog.exec():
            self.load_product_table()

    def delete_product(self):
        product_id = self._get_selected_product_id()
        if not product_id:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn sản phẩm để xóa.")
            return
        self._confirm_delete_product(product_id)

    def _confirm_delete_product(self, product_id):
        db = self._create_db()
        try:
            cursor = db.execute("SELECT ProductName FROM Product WHERE ProductID = ?", (product_id,))
            row = cursor.fetchone()
            name = row[0] if row else ""
        finally:
            db.close()

        answer = QMessageBox.question(
            self.window,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa sản phẩm {name} ({product_id}) không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        db = self._create_db()
        try:
            db.execute("DELETE FROM Inventory WHERE ProductID = ?", (product_id,))
            db.execute("DELETE FROM Order_Detail WHERE ProductID = ?", (product_id,))
            db.execute("DELETE FROM Product WHERE ProductID = ?", (product_id,))
            db.commit()
            QMessageBox.information(self.window, "Thành công", "Sản phẩm đã được xóa.")
            self.load_product_table()
        except pyodbc.Error as e:
            db.rollback()
            QMessageBox.critical(self.window, "Lỗi xóa", f"Không thể xóa sản phẩm.\n{e}")
        finally:
            db.close()

    def search_product(self):
        search_text = self.window.txtTimKiemSP.text().strip()
        if not search_text:
            self.load_product_table()
            return

        if search_text.isdigit():
            self.load_product_table(product_id=search_text)
        else:
            self.load_product_table(product_name=search_text)