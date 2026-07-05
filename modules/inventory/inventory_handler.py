"""Inventory module handler: business logic for inventory adjustments and queries."""
from typing import Optional
from datetime import datetime
from database.database import Database


class InventoryHandler:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def list_items(self):
        return self.db.get_inventory_items()

    def get_item(self, maSP: str):
        for it in self.list_items():
            if it.get("maSP") == maSP:
                return it
        return None

    def apply_inventory_adjustment(self, item: dict, mode: str, quantity: int, note: str, nhan_vien: str = "Hệ thống"):
        """Apply increase/decrease to inventory and add a history entry.

        mode: "Tăng" or "Giảm"
        """
        if item is None or "maSP" not in item:
            return False
        current = int(item.get("tonKho", 0))
        if mode == "Tăng":
            new_qty = current + int(quantity)
        else:
            new_qty = current - int(quantity)
            if new_qty < 0:
                new_qty = 0

        item["tonKho"] = new_qty
        item["capNhatGanNhat"] = datetime.now().strftime("%d/%m/%Y")
        # persist updated item
        self.db.update_inventory_item(item)

        # add history entry
        entry = {
            "ngay": datetime.now().strftime("%d/%m/%Y"),
            "loai": mode,
            "soLuong": int(quantity),
            "nhanVien": nhan_vien,
            "ghiChu": note or "",
        }
        self.db.add_inventory_history(item["maSP"], entry)
        return True

    def update_item(self, item: dict):
        self.db.update_inventory_item(item)


from PyQt6 import QtWidgets
from .inventory_detail_ui import Ui_pageTonKho
from .inventory_update_ui import Ui_Dialog as Ui_InventoryUpdate


class InventoryDetailDialog(QtWidgets.QDialog, Ui_pageTonKho):
    def __init__(self, handler: InventoryHandler, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.handler = handler
        self.item = None
        self.btnCapNhatTK.clicked.connect(self.on_update)

    def fill_item(self, item):
        self.item = item
        self.txtMaSPTK.setText(item.get("maSP", ""))
        self.txtTenSPTK.setText(item.get("tenSP", ""))
        self.txtDanhMucTK.setText(item.get("danhMuc", ""))
        self.txtDonViTinhTK.setText(item.get("donViTinh", ""))
        self.txtTonKhoTK.setText(str(item.get("tonKho", 0)))
        self.txtTrangThaiTK.setText(item.get("trangThai", ""))
        self.txtCapNhatTK.setText(item.get("capNhatGanNhat", ""))
        self.txtMaSPTK.setReadOnly(True)
        self.txtTenSPTK.setReadOnly(True)
        self.txtDanhMucTK.setReadOnly(True)
        self.txtDonViTinhTK.setReadOnly(True)
        self.txtTonKhoTK.setReadOnly(True)
        self.txtTrangThaiTK.setReadOnly(True)
        self.txtCapNhatTK.setReadOnly(True)
        self.tblLichSuTK.setRowCount(0)
        for history in item.get("history", []):
            row = self.tblLichSuTK.rowCount()
            self.tblLichSuTK.insertRow(row)
            self.tblLichSuTK.setItem(row, 0, QtWidgets.QTableWidgetItem(history.get("ngay", "")))
            self.tblLichSuTK.setItem(row, 1, QtWidgets.QTableWidgetItem(history.get("loai", "")))
            self.tblLichSuTK.setItem(row, 2, QtWidgets.QTableWidgetItem(str(history.get("soLuong", 0))))
            self.tblLichSuTK.setItem(row, 3, QtWidgets.QTableWidgetItem(history.get("nhanVien", "")))
            self.tblLichSuTK.setItem(row, 4, QtWidgets.QTableWidgetItem(history.get("ghiChu", "")))

    def on_update(self):
        if self.item is not None:
            dlg = InventoryUpdateDialog(self.handler, parent=self)
            dlg.prepare_for_update(self.item)
            if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                # refresh item from DB
                updated = self.handler.get_item(self.item.get("maSP"))
                if updated:
                    self.fill_item(updated)
        self.accept()


class InventoryUpdateDialog(QtWidgets.QDialog, Ui_InventoryUpdate):
    def __init__(self, handler: InventoryHandler, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.handler = handler
        self.item = None
        self.rbTangTK.setChecked(True)
        self.btnLuuTK.clicked.connect(self.on_save)
        self.btnHuyTK.clicked.connect(self.reject)

    def prepare_for_update(self, item):
        self.item = item
        self.txtSoLuongTK.clear()
        self.txtGhiChuTK.clear()
        self.rbTangTK.setChecked(True)

    def on_save(self):
        if self.item is None:
            return
        try:
            quantity = int(self.txtSoLuongTK.text().strip())
        except Exception:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Số lượng phải là số nguyên.")
            return
        if quantity <= 0:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Số lượng phải lớn hơn 0.")
            return
        mode = "Tăng" if self.rbTangTK.isChecked() else "Giảm"
        note = self.txtGhiChuTK.toPlainText().strip() or "Không có ghi chú"
        self.handler.apply_inventory_adjustment(self.item, mode, quantity, note)
        self.accept()
