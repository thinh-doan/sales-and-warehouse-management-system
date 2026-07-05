"""Category module handler: encapsulates category DB operations and utilities."""
from typing import Optional
from database.database import Database


class CategoryHandler:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def list_categories(self):
        return self.db.get_categories()

    def generate_category_code(self):
        """Generate next category code like DM001, DM002, ..."""
        cats = self.list_categories()
        max_num = 0
        for c in cats:
            ma = c.get("maDM", "")
            if ma.startswith("DM"):
                try:
                    n = int(ma[2:])
                    if n > max_num:
                        max_num = n
                except Exception:
                    continue
        next_num = max_num + 1
        return f"DM{next_num:03d}"

    def add_category(self, category: dict):
        self.db.add_category(category)

    def update_category(self, category: dict):
        self.db.update_category(category)

    def delete_category(self, maDM: str):
        self.db.delete_category(maDM)


from PyQt6 import QtWidgets
from .category_add_ui import Ui_hopThoaiMacDinh
from .category_detail_ui import Ui_hopThoaiDanhMucChiTiet


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
        if self.category is None:
            self.handler.add_category(data)
        else:
            self.handler.update_category(data)
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
                # refresh not strictly necessary, but we can reload categories
                pass
        self.accept()

    def on_delete(self):
        if self.category is not None:
            self.handler.delete_category(self.category.get("maDM"))
        self.accept()
