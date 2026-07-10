from __future__ import annotations

import os
import sys
from typing import Optional

from PyQt6 import QtWidgets

try:
    from connect import Database
except ModuleNotFoundError:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from connect import Database
from .category_add_ui import Ui_hopThoaiMacDinh
from .category_detail_ui import Ui_hopThoaiDanhMucChiTiet


class CategoryHandler:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    @staticmethod
    def _to_category_code(category_id: int) -> str:
        return f"DM{int(category_id):03d}"

    @staticmethod
    def _parse_category_code(code: str) -> Optional[int]:
        raw = (code or "").strip().upper()
        if raw.startswith("DM") and raw[2:].isdigit():
            return int(raw[2:])
        if raw.isdigit():
            return int(raw)
        return None

    @staticmethod
    def _format_price(value) -> str:
        try:
            return f"{float(value):,.0f}"
        except Exception:
            return "0"

    def _get_next_category_id(self) -> int:
        cursor = self.db.execute(
            "SELECT ISNULL(MAX(CategoryID), 0) + 1 FROM Category"
        )
        row = cursor.fetchone()
        return int(row[0] or 1)

    def list_categories(self) -> list[dict]:
        rows = self.db.execute(
            """
            SELECT c.CategoryID,
                   c.CategoryName,
                   c.CategoryDescription,
                   ISNULL(SUM(i.QuantityInStock), 0) AS TotalQuantity
            FROM Category c
            LEFT JOIN Product p ON p.CategoryID = c.CategoryID
            LEFT JOIN Inventory i ON i.ProductID = p.ProductID
            GROUP BY c.CategoryID, c.CategoryName, c.CategoryDescription
            ORDER BY c.CategoryID
            """
        ).fetchall()
        return [
            {
                "categoryID": int(r[0] or 0),
                "maDM": self._to_category_code(int(r[0] or 0)),
                "tenDM": r[1] or "",
                "moTa": r[2] or "",
                "sl": int(r[3] or 0),
            }
            for r in rows
        ]

    def get_products_by_category(self, category_id: int) -> list[dict]:
        rows = self.db.execute(
            """
            SELECT p.ProductID, p.ProductName, p.ProductUnitPrice,
                   ISNULL(SUM(i.QuantityInStock), 0) AS TonKho,
                   p.ProductStatus
            FROM Product p
            LEFT JOIN Inventory i ON i.ProductID = p.ProductID
            WHERE p.CategoryID = ?
            GROUP BY p.ProductID, p.ProductName, p.ProductUnitPrice, p.ProductStatus
            ORDER BY p.ProductID
            """,
            (int(category_id),),
        ).fetchall()
        return [
            {
                "maSP": f"SP{int(r[0] or 0):03d}",
                "tenSP": r[1] or "",
                "gia": self._format_price(r[2]),
                "tonKho": str(int(r[3] or 0)),
                "trangThai": r[4] or "",
            }
            for r in rows
        ]

    def generate_category_code(self) -> str:
        return self._to_category_code(self._get_next_category_id())

    def add_category(self, category: dict) -> bool:
        category_id = self._parse_category_code(category.get("maDM", "").strip()) or self._get_next_category_id()
        self.db.execute(
            "INSERT INTO Category (CategoryID, CategoryName, CategoryDescription) VALUES (?, ?, ?)",
            (
                int(category_id),
                category.get("tenDM", "").strip(),
                category.get("moTa", "").strip() or None,
            ),
        )
        self.db.commit()
        return True

    def update_category(self, category: dict) -> bool:
        category_id = self._parse_category_code(category.get("maDM", "").strip())
        if category_id is None:
            return False
        self.db.execute(
            "UPDATE Category SET CategoryName = ?, CategoryDescription = ? WHERE CategoryID = ?",
            (
                category.get("tenDM", "").strip(),
                category.get("moTa", "").strip() or None,
                int(category_id),
            ),
        )
        self.db.commit()
        return True

    def delete_category(self, maDM: str) -> bool:
        category_id = self._parse_category_code((maDM or "").strip())
        if category_id is None:
            return False

        used_row = self.db.execute(
            "SELECT COUNT(1) FROM Product WHERE CategoryID = ?",
            (int(category_id),),
        ).fetchone()
        if int(used_row[0] or 0) > 0:
            return False

        self.db.execute("DELETE FROM Category WHERE CategoryID = ?", (int(category_id),))
        self.db.commit()
        return True


class CategoryAddDialog(QtWidgets.QDialog, Ui_hopThoaiMacDinh):
    def __init__(self, handler: CategoryHandler, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.handler = handler
        self.category = None
        self.btnLuu.clicked.connect(self.on_save)
        self.btnHuy.clicked.connect(self.reject)

    def prepare_for_add(self):
        self.category = None
        self.txtMaSP.setReadOnly(True)
        self.txtTenDM.setReadOnly(False)
        self.txtMoTaSP.setReadOnly(False)
        self.txtMaSP.setText(self.handler.generate_category_code())
        self.txtTenDM.clear()
        self.txtMoTaSP.clear()

    def prepare_for_update(self, category):
        self.category = category
        self.txtMaSP.setText(category.get("maDM", ""))
        self.txtMaSP.setReadOnly(True)
        self.txtTenDM.setReadOnly(False)
        self.txtMoTaSP.setReadOnly(False)
        self.txtTenDM.setText(category.get("tenDM", ""))
        self.txtMoTaSP.setPlainText(category.get("moTa", ""))

    def get_data(self):
        return {
            "maDM": self.txtMaSP.text().strip(),
            "tenDM": self.txtTenDM.text().strip(),
            "moTa": self.txtMoTaSP.toPlainText().strip(),
            "sl": self.category.get("sl", 0) if self.category else 0,
        }

    def on_save(self):
        if not self.txtTenDM.text().strip():
            QtWidgets.QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên danh mục.")
            return
        data = self.get_data()
        try:
            if self.category is None:
                self.handler.add_category(data)
            else:
                self.handler.update_category(data)
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, "Lỗi", f"Không thể lưu danh mục: {exc}")
            return
        self.accept()


class CategoryDetailDialog(QtWidgets.QDialog, Ui_hopThoaiDanhMucChiTiet):
    def __init__(self, handler: CategoryHandler, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.handler = handler
        self.category = None
        self.btnCapNhatDM.clicked.connect(self.on_update)
        self.btnXoaDM.clicked.connect(self.on_delete)

    def fill_category(self, category, products):
        self.category = category
        self.txtMaDM.setReadOnly(True)
        self.txtTenDM.setReadOnly(True)
        self.txtMoTaDM.setReadOnly(True)
        self.txtMaDM.setText(category.get("maDM", ""))
        self.txtTenDM.setText(category.get("tenDM", ""))
        self.txtMoTaDM.setPlainText(category.get("moTa", ""))
        self.tblDanhSachSP.setRowCount(0)
        for product in products:
            row = self.tblDanhSachSP.rowCount()
            self.tblDanhSachSP.insertRow(row)
            self.tblDanhSachSP.setItem(row, 0, QtWidgets.QTableWidgetItem(product.get("maSP", "")))
            self.tblDanhSachSP.setItem(row, 1, QtWidgets.QTableWidgetItem(product.get("tenSP", "")))
            self.tblDanhSachSP.setItem(row, 2, QtWidgets.QTableWidgetItem(product.get("gia", "")))
            self.tblDanhSachSP.setItem(row, 3, QtWidgets.QTableWidgetItem(product.get("tonKho", "")))
            self.tblDanhSachSP.setItem(row, 4, QtWidgets.QTableWidgetItem(product.get("trangThai", "")))

    def on_update(self):
        if self.category is not None:
            dlg = CategoryAddDialog(self.handler, parent=self)
            dlg.prepare_for_update(self.category)
            if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                self.accept()

    def on_delete(self):
        if self.category is not None:
            deleted = self.handler.delete_category(self.category.get("maDM", ""))
            if deleted:
                QtWidgets.QMessageBox.information(self, "Thông báo", "Xóa danh mục thành công!")
                self.accept()
                return
            QtWidgets.QMessageBox.warning(
                self,
                "Không thể xóa",
                "Danh mục đang chứa sản phẩm hoặc dữ liệu không hợp lệ.",
            )


class CategoryTabController:
    def __init__(self, window, db: Optional[Database] = None):
        self.window = window
        self.handler = CategoryHandler(db)
        self.categories = []
        self.setup_handlers()
        self.refresh_table()

    def setup_handlers(self):
        self.window.tblDM.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.window.tblDM.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.window.cbbTimKiemDM.setEditable(True)
        self.window.cbbTimKiemDM.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.window.cbbTimKiemDM.lineEdit().setPlaceholderText("Nhập mã hoặc tên danh mục")
        self.window.btnThemDM.clicked.connect(self.open_add)
        self.window.btnChiTietDM.clicked.connect(self.open_detail)
        self.window.btnCapNhatDM.clicked.connect(self.open_update)
        self.window.btnXoaDM.clicked.connect(self.delete_selected)
        self.window.btnRefreshDM.clicked.connect(self.refresh_table)
        self.window.btnTimKiemDM.clicked.connect(self.filter_table)
        self.window.cbbTimKiemDM.currentTextChanged.connect(self.filter_table)

    def refresh_table(self):
        self.categories = self.handler.list_categories()
        current_text = self.window.cbbTimKiemDM.currentText()
        self.window.cbbTimKiemDM.blockSignals(True)
        self.window.cbbTimKiemDM.clear()
        self.window.cbbTimKiemDM.addItem("")
        for item in self.categories:
            self.window.cbbTimKiemDM.addItem(item.get("maDM", ""))
            self.window.cbbTimKiemDM.addItem(item.get("tenDM", ""))
        self.window.cbbTimKiemDM.setCurrentText(current_text)
        self.window.cbbTimKiemDM.blockSignals(False)
        self.populate_table(self.categories)

    def populate_table(self, items):
        self.window.tblDM.setRowCount(0)

        # Map cot theo tieu de de tranh lech du lieu khi UI doi thu tu cot.
        header_to_col = {}
        for col in range(self.window.tblDM.columnCount()):
            header_item = self.window.tblDM.horizontalHeaderItem(col)
            if header_item is not None:
                header_to_col[(header_item.text() or "").strip().lower()] = col

        col_ma_dm = header_to_col.get("mã danh mục", 0)
        col_ten_dm = header_to_col.get("tên danh mục", 1)
        col_mo_ta = header_to_col.get("mô tả", 2)
        col_so_luong = header_to_col.get("số lượng", 3)

        for item in items:
            row = self.window.tblDM.rowCount()
            self.window.tblDM.insertRow(row)
            self.window.tblDM.setItem(row, col_ma_dm, QtWidgets.QTableWidgetItem(item.get("maDM", "")))
            self.window.tblDM.setItem(row, col_ten_dm, QtWidgets.QTableWidgetItem(item.get("tenDM", "")))
            self.window.tblDM.setItem(row, col_mo_ta, QtWidgets.QTableWidgetItem(item.get("moTa", "")))
            self.window.tblDM.setItem(row, col_so_luong, QtWidgets.QTableWidgetItem(str(item.get("sl", 0))))

    def filter_table(self):
        keyword = self.window.cbbTimKiemDM.currentText().strip().lower()
        if not keyword:
            self.populate_table(self.categories)
            return
        filtered = [
            item
            for item in self.categories
            if keyword in item.get("maDM", "").lower() or keyword in item.get("tenDM", "").lower()
        ]
        self.populate_table(filtered)

    def get_selected(self):
        row = self.window.tblDM.currentRow()
        if row < 0:
            return None
        category_id = self.window.tblDM.item(row, 0).text()
        for item in self.categories:
            if item.get("maDM") == category_id:
                return item
        return None

    def open_add(self):
        dialog = CategoryAddDialog(self.handler, self.window)
        dialog.prepare_for_add()
        dialog.setWindowTitle("Thêm danh mục")
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_table()
            QtWidgets.QMessageBox.information(self.window, "Thông báo", "Thêm danh mục thành công!")

    def open_detail(self):
        category = self.get_selected()
        if category is None:
            QtWidgets.QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một danh mục để xem chi tiết.")
            return
        products = self.handler.get_products_by_category(int(category.get("categoryID")))
        dialog = CategoryDetailDialog(self.handler, self.window)
        dialog.fill_category(category, products)
        dialog.setWindowTitle("Chi tiết danh mục")
        result = dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_table()

    def open_update(self):
        category = self.get_selected()
        if category is None:
            QtWidgets.QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một danh mục để cập nhật.")
            return
        dialog = CategoryAddDialog(self.handler, self.window)
        dialog.setWindowTitle("Cập nhật danh mục")
        dialog.prepare_for_update(category)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_table()
            QtWidgets.QMessageBox.information(self.window, "Thông báo", "Cập nhật danh mục thành công!")

    def delete_selected(self):
        category = self.get_selected()
        if category is None:
            QtWidgets.QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một danh mục để xóa.")
            return
        reply = QtWidgets.QMessageBox.question(
            self.window,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa danh mục {category.get('maDM', '')} - {category.get('tenDM', '')}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            deleted = self.handler.delete_category(category.get("maDM", ""))
            if deleted:
                self.refresh_table()
                QtWidgets.QMessageBox.information(self.window, "Thông báo", "Xóa danh mục thành công!")
            else:
                QtWidgets.QMessageBox.warning(
                    self.window,
                    "Không thể xóa",
                    "Danh mục đang chứa sản phẩm hoặc dữ liệu không hợp lệ.",
                )