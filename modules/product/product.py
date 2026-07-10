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
            self.txtMaSP.setText(str(self.product[0] if self.product[0] is not None else ""))
            self.txtTenSP.setText(str(self.product[1] if self.product[1] is not None else ""))
            
            # Index -> 0:ProductID, 1:ProductName, 2:ProductUnitPrice, 3:Unit, 
            # 4:ProductDescription, 5:ProductStatus, 6:CategoryName, 7:QuantityInStock, 
            # 8:LastUpdated, 9:WarehouseID
            self.txtDanhMuc.setText(str(self.product[6] if self.product[6] is not None else ""))
            self.txtDonGia.setText(str(self.product[2] if self.product[2] is not None else ""))
            self.txtTonKho.setText(str(self.product[7] if self.product[7] is not None else "0"))
            self.txtDonVi.setText(str(self.product[3] if self.product[3] is not None else ""))
            self.txtMoTaSP.setText(str(self.product[4] if self.product[4] is not None else ""))
            
            # Fix TypeError by explicitly converting to int, safely handling None
            if len(self.product) > 9 and self.product[9] is not None:
                try:
                    warehouse_index = int(self.product[9])
                    self.cbbKhoSP.setCurrentIndex(warehouse_index)
                except ValueError:
                    self.cbbKhoSP.setCurrentIndex(0)
            else:
                self.cbbKhoSP.setCurrentIndex(0)
            
            # For update: only ProductID should be readonly; other fields editable
            self.txtMaSP.setReadOnly(True)
            self.txtTenSP.setReadOnly(False)
            self.txtDanhMuc.setReadOnly(False)
            self.txtDonGia.setReadOnly(False)
            self.txtTonKho.setReadOnly(False)
            self.txtDonVi.setReadOnly(False)
            self.cbbKhoSP.setEnabled(True)
        else:
            self.setWindowTitle("Thêm sản phẩm")
            self.txtMaSP.setText("")
            self.txtTenSP.setText("")
            self.txtDanhMuc.setText("")
            self.txtDonGia.setText("")
            self.txtTonKho.setText("")
            self.txtDonVi.setText("")
            self.txtMoTaSP.setText("")
            self.cbbKhoSP.setCurrentIndex(0)
            
            # Make fields editable when adding
            self.txtMaSP.setReadOnly(False)
            self.txtTenSP.setReadOnly(False)
            self.txtDanhMuc.setReadOnly(False)
            self.txtDonGia.setReadOnly(False)
            self.txtTonKho.setReadOnly(False)
            self.txtDonVi.setReadOnly(False)
            self.cbbKhoSP.setEnabled(True)

    def _save_product(self):
        product_id = self.txtMaSP.text().strip()
        product_name = self.txtTenSP.text().strip()
        category_name = self.txtDanhMuc.text().strip()
        unit_price = self.txtDonGia.text().strip()
        quantity = self.txtTonKho.text().strip()
        unit = self.txtDonVi.text().strip()
        description = self.txtMoTaSP.text().strip()
        warehouse_idx = self.cbbKhoSP.currentIndex()
        status = "Đang bán"

        if not product_id or not product_name or not category_name or not unit_price or not quantity or not unit:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ dữ liệu sản phẩm.")
            return

        if warehouse_idx <= 0:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn kho hợp lệ.")
            return

        try:
            product_id_int = int(product_id)
        except ValueError:
            QMessageBox.warning(self, "Thông báo", "Mã sản phẩm phải là số nguyên.")
            return

        try:
            unit_price_val = float(unit_price)
        except ValueError:
            QMessageBox.warning(self, "Thông báo", "Đơn giá phải là số hợp lệ.")
            return

        try:
            quantity_int = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Thông báo", "Tồn kho phải là số nguyên.")
            return

        today_str = date.today().strftime('%Y-%m-%d')
        
        db = Database()
        try:
            cursor = db.execute("SELECT CategoryID FROM Category WHERE CategoryName = ?", (category_name,))
            category_row = cursor.fetchone()
            if category_row:
                category_id = category_row[0]
            else:
                QMessageBox.warning(self, "Thông báo", "Danh mục không tồn tại. Vui lòng nhập đúng danh mục.")
                db.close()
                return

            if self.product:
                db.execute(
                    "UPDATE Product SET ProductName = ?, ProductUnitPrice = ?, Unit = ?, ProductDescription = ?, ProductStatus = ?, CategoryID = ? WHERE ProductID = ?",
                    (product_name, unit_price_val, unit, description if description else None, status, category_id, product_id_int),
                )
                cursor = db.execute("SELECT COUNT(1) FROM Inventory WHERE ProductID = ? AND WarehouseID = ?", (product_id_int, warehouse_idx))
                if cursor.fetchone()[0] > 0:
                    db.execute(
                        "UPDATE Inventory SET QuantityInStock = ?, LastUpdated = ? WHERE ProductID = ? AND WarehouseID = ?",
                        (quantity_int, today_str, product_id_int, warehouse_idx),
                    )
                else:
                    db.execute(
                        "INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated) VALUES (?, ?, ?, ?)",
                        (warehouse_idx, product_id_int, quantity_int, today_str),
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
                cursor = db.execute("SELECT COUNT(1) FROM Inventory WHERE ProductID = ? AND WarehouseID = ?", (product_id_int, warehouse_idx))
                if cursor.fetchone()[0] == 0:
                    db.execute(
                        "INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated) VALUES (?, ?, ?, ?)",
                        (warehouse_idx, product_id_int, quantity_int, today_str),
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
        self.cbbKhoSP.setEnabled(self.editable)
        self.txtNgayTaoSP.setEnabled(False)
        self.txtTrangThaiSP.setEnabled(False)

    def _connect_signals(self):
        self.btnCapNhatSP.clicked.connect(self._request_update)
        self.btnXoaSP.clicked.connect(self._request_delete)

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
        self.txtNgayTaoSP.setText(str(self.product[8] if self.product[8] is not None else ""))
        self.txtTrangThaiSP.setText(str(self.product[5] if self.product[5] is not None else ""))
        
        if len(self.product) > 9 and self.product[9] is not None:
            try:
                self.cbbKhoSP.setCurrentIndex(int(self.product[9]))
            except ValueError:
                self.cbbKhoSP.setCurrentIndex(0)

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
            cursor = db.execute(query, (int(self.product[0]),))
            rows = cursor.fetchall()
            self.tblLichSuBan.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                self.tblLichSuBan.setItem(row_idx, 0, QTableWidgetItem(str(row[0] if row[0] is not None else "")))
                self.tblLichSuBan.setItem(row_idx, 1, QTableWidgetItem(row[1].strftime("%d/%m/%Y") if row[1] else ""))
                self.tblLichSuBan.setItem(row_idx, 2, QTableWidgetItem(str(row[2] if row[2] is not None else "")))
                self.tblLichSuBan.setItem(row_idx, 3, QTableWidgetItem(str(row[3] if row[3] is not None else "")))
                self.tblLichSuBan.setItem(row_idx, 4, QTableWidgetItem(f"{row[4]:,.0f}" if row[4] is not None else ""))
        except Exception:
            pass
        finally:
            db.close()

    def _load_stock_history(self):
        self.tblLichSuTonKho.setRowCount(0)
        db = Database()
        try:
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
            cursor = db.execute(query, (int(self.product[0]), int(self.product[0])))
            rows = cursor.fetchall()
            self.tblLichSuTonKho.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                self.tblLichSuTonKho.setItem(row_idx, 0, QTableWidgetItem(row[0].strftime("%d/%m/%Y") if row[0] else ""))
                self.tblLichSuTonKho.setItem(row_idx, 1, QTableWidgetItem(str(row[1] if row[1] is not None else "")))
                self.tblLichSuTonKho.setItem(row_idx, 2, QTableWidgetItem(str(int(row[2] if row[2] is not None else 0))))
                self.tblLichSuTonKho.setItem(row_idx, 3, QTableWidgetItem(str(row[3] if row[3] is not None else "Không rõ")))
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

    @staticmethod
    def _show_error(parent, title, exc):
        QMessageBox.critical(parent, title, f"Đã xảy ra lỗi trong chức năng Sản phẩm.\n{exc}")

    def _connect_signals(self):
        self.window.btnThemSP.clicked.connect(self.open_add_product_dialog)
        self.window.btnChiTietSP.clicked.connect(self.open_product_detail_dialog)
        self.window.btnCapNhatSP.clicked.connect(self.open_update_product_dialog)
        self.window.btnXoaSP.clicked.connect(self.delete_product)
        self.window.btnRefreshSP.clicked.connect(self.load_product_table)
        self.window.btnTimKiemSP.clicked.connect(self.search_product)
        
        if hasattr(self.window, 'btnCapNhatTK'):
            self.window.btnCapNhatTK.clicked.connect(self.open_update_product_dialog)

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
        if hasattr(self.window, 'btnCapNhatTK'):
            self.window.btnCapNhatTK.setEnabled(selected)

    def load_product_table(self, product_id=None, product_name=None):
        db = self._create_db()
        try:
            query = """
                SELECT p.ProductID, p.ProductName, c.CategoryName, i.WarehouseID,
                       SUM(ISNULL(i.QuantityInStock, 0)) AS QuantityInStock, p.ProductUnitPrice, p.ProductStatus
                FROM Product p
                LEFT JOIN Inventory i ON p.ProductID = i.ProductID
                LEFT JOIN Category c ON p.CategoryID = c.CategoryID
                WHERE 1 = 1
            """
            params = []
            if product_id:
                query += " AND p.ProductID = ?"
                params.append(int(product_id))
            if product_name:
                query += " AND p.ProductName LIKE ?"
                params.append(f"%{product_name}%")
                
            try:
                if hasattr(self.window, 'cbbDanhMuc'):
                    cat_data = self.window.cbbDanhMuc.currentData()
                    if cat_data is not None:
                        query += " AND p.CategoryID = ?"
                        params.append(cat_data)
            except Exception:
                pass
                
            try:
                if hasattr(self.window, 'cbbTrangThai'):
                    status_txt = self.window.cbbTrangThai.currentText().strip()
                    if status_txt and status_txt != "Tất cả":
                        query += " AND p.ProductStatus = ?"
                        params.append(status_txt)
            except Exception:
                pass
                
            query += " GROUP BY p.ProductID, p.ProductName, c.CategoryName, i.WarehouseID, p.ProductUnitPrice, p.ProductStatus"
            query += " ORDER BY p.ProductID"
            
            cursor = db.execute(query, params if params else None)
            rows = cursor.fetchall()
            self._render_product_table(rows)
        except Exception as e:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải danh sách sản phẩm.\n{e}")
        finally:
            db.close()

    def _render_product_table(self, rows):
        existing_widths = [self.window.bangSanPham.columnWidth(i) for i in range(self.window.bangSanPham.columnCount())]
        should_autofit = not existing_widths or all(width == 100 for width in existing_widths)

        self.window.bangSanPham.setColumnCount(7)
        self.window.bangSanPham.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.window.bangSanPham.setItem(row_index, 0, QTableWidgetItem(str(row[0] if row[0] is not None else "")))
            self.window.bangSanPham.setItem(row_index, 1, QTableWidgetItem(str(row[1] if row[1] is not None else "")))
            self.window.bangSanPham.setItem(row_index, 2, QTableWidgetItem(str(row[2] if row[2] is not None else "")))
            self.window.bangSanPham.setItem(row_index, 3, QTableWidgetItem(str(row[3] if row[3] is not None else ""))) 
            self.window.bangSanPham.setItem(row_index, 4, QTableWidgetItem(str(row[4] if row[4] is not None else "0")))
            self.window.bangSanPham.setItem(row_index, 5, QTableWidgetItem(str(row[5] if row[5] is not None else "")))
            self.window.bangSanPham.setItem(row_index, 6, QTableWidgetItem(str(row[6] if row[6] is not None else "")))

        if should_autofit:
            self.window.bangSanPham.resizeColumnsToContents()
        else:
            limit = min(len(existing_widths), self.window.bangSanPham.columnCount())
            for column_index in range(limit):
                self.window.bangSanPham.setColumnWidth(column_index, existing_widths[column_index])
        self._update_action_buttons_state()

    def _populate_filters(self):
        if not hasattr(self.window, 'cbbDanhMuc'):
            return
        db = self._create_db()
        try:
            cursor = db.execute("SELECT CategoryID, CategoryName FROM Category ORDER BY CategoryName")
            rows = cursor.fetchall()
            self.window.cbbDanhMuc.clear()
            self.window.cbbDanhMuc.addItem("Tất cả", None)
            for r in rows:
                self.window.cbbDanhMuc.addItem(str(r[1] if r[1] is not None else ""), r[0])
        except Exception:
            pass
        finally:
            db.close()

        try:
            self.window.cbbTrangThai.clear()
            self.window.cbbTrangThai.addItem("Tất cả")
            self.window.cbbTrangThai.addItem("Đang bán")
            self.window.cbbTrangThai.addItem("Ngừng bán")
        except Exception:
            pass

    def _load_product_record(self, product_id):
        if not product_id:
            return None
        db = self._create_db()
        try:
            cursor = db.execute(
                "SELECT p.ProductID, p.ProductName, p.ProductUnitPrice, p.Unit, p.ProductDescription, p.ProductStatus, c.CategoryName, ISNULL(SUM(i.QuantityInStock),0) AS QuantityInStock, MAX(i.LastUpdated) AS LastUpdated, MAX(i.WarehouseID) AS WarehouseID "
                "FROM Product p "
                "LEFT JOIN Inventory i ON p.ProductID = i.ProductID "
                "LEFT JOIN Category c ON p.CategoryID = c.CategoryID "
                "WHERE p.ProductID = ? "
                "GROUP BY p.ProductID, p.ProductName, p.ProductUnitPrice, p.Unit, p.ProductDescription, p.ProductStatus, c.CategoryName",
                (int(product_id),),
            )
            return cursor.fetchone()
        except Exception as e:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải sản phẩm.\n{e}")
            return None
        finally:
            db.close()

    def open_add_product_dialog(self):
        try:
            dialog = ProductFormDialog(self.window)
            if dialog.exec():
                self.load_product_table()
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)

    def open_product_detail_dialog(self):
        try:
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
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)

    def open_update_product_dialog(self):
        try:
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
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)

    def delete_product(self):
        try:
            product_id = self._get_selected_product_id()
            if not product_id:
                QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn sản phẩm để xóa.")
                return
            self._confirm_delete_product(product_id)
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)

    def _confirm_delete_product(self, product_id):
        db = self._create_db()
        try:
            cursor = db.execute("SELECT ProductName FROM Product WHERE ProductID = ?", (int(product_id),))
            row = cursor.fetchone()
            name = row[0] if row else ""
        except Exception as exc:
            self._show_error(self.window, "Lỗi xóa sản phẩm", exc)
            return
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
            db.execute("DELETE FROM Inventory WHERE ProductID = ?", (int(product_id),))
            db.execute("DELETE FROM Order_Detail WHERE ProductID = ?", (int(product_id),))
            db.execute("DELETE FROM Product WHERE ProductID = ?", (int(product_id),))
            db.commit()
            QMessageBox.information(self.window, "Thành công", "Sản phẩm đã được xóa.")
            self.load_product_table()
        except pyodbc.Error as e:
            db.rollback()
            QMessageBox.critical(self.window, "Lỗi xóa", f"Không thể xóa sản phẩm.\n{e}")
        finally:
            db.close()

    def search_product(self):
        try:
            search_text = self.window.txtTimKiemSP.text().strip()
            if not search_text:
                self.load_product_table()
                return

            if search_text.isdigit():
                self.load_product_table(product_id=search_text)
            else:
                self.load_product_table(product_name=search_text)
        except Exception as exc:
            self._show_error(self.window, "Lỗi sản phẩm", exc)