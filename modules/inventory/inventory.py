from __future__ import annotations

from datetime import date
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
from .inventory_detail_ui import Ui_pageTonKho
from .inventory_update_ui import Ui_Dialog as Ui_InventoryUpdate


class InventoryHandler:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    @staticmethod
    def _to_product_code(product_id: int) -> str:
        return f"SP{int(product_id):03d}"

    @staticmethod
    def _parse_product_code(code: str) -> Optional[int]:
        raw = (code or "").strip().upper()
        if raw.startswith("SP") and raw[2:].isdigit():
            return int(raw[2:])
        if raw.isdigit():
            return int(raw)
        return None

    @staticmethod
    def _format_date(value) -> str:
        if value is None:
            return ""
        try:
            return value.strftime("%d/%m/%Y")
        except Exception:
            return str(value)

    def list_items(self) -> list[dict]:
        rows = self.db.execute(
            """
            SELECT i.WarehouseID, p.ProductID, p.ProductName, c.CategoryName,
                   i.QuantityInStock, p.ProductStatus, i.LastUpdated, p.Unit
            FROM Inventory i
            JOIN Product p ON p.ProductID = i.ProductID
            JOIN Category c ON c.CategoryID = p.CategoryID
            ORDER BY i.WarehouseID, p.ProductID
            """
        ).fetchall()
        return [
            {
                "warehouseID": int(row[0] or 0),
                "maKho": f"KHO{int(row[0] or 0):03d}",
                "productID": int(row[1] or 0),
                "maSP": self._to_product_code(int(row[1] or 0)),
                "tenSP": row[2] or "",
                "danhMuc": row[3] or "",
                "soLuong": int(row[4] or 0),
                "tonKho": int(row[4] or 0),
                "trangThai": row[5] or "",
                "capNhatGanNhat": self._format_date(row[6]),
                "donViTinh": row[7] or "",
            }
            for row in rows
        ]

    def get_item(self, maSP: str):
        target_id = self._parse_product_code(maSP)
        if target_id is None:
            return None
        for item in self.list_items():
            if item.get("productID") == target_id:
                return item
        return None

    def get_item_history(self, product_id: int) -> list[dict]:
        rows = self.db.execute(
            """
            SELECT WarehouseID, QuantityInStock, LastUpdated
            FROM Inventory
            WHERE ProductID = ?
            ORDER BY WarehouseID
            """,
            (int(product_id),),
        ).fetchall()
        return [
            {
                "ngay": self._format_date(row[2]),
                "loai": "Tồn hiện tại",
                "soLuong": int(row[1] or 0),
                "nhanVien": f"Kho {int(row[0] or 0)}",
                "ghiChu": "Dữ liệu theo từng kho",
            }
            for row in rows
        ]

    def apply_inventory_adjustment(self, item: dict, mode: str, quantity: int, note: str, nhan_vien: str = "Hệ thống"):
        if item is None:
            return False

        product_id = self._parse_product_code((item.get("maSP") or "").strip())
        if product_id is None:
            return False

        selected_warehouse_id = item.get("warehouseID")
        if selected_warehouse_id is not None:
            selected_warehouse_id = int(selected_warehouse_id)

        if selected_warehouse_id is not None:
            row = self.db.execute(
                "SELECT WarehouseID, QuantityInStock FROM Inventory WHERE ProductID = ? AND WarehouseID = ?",
                (int(product_id), selected_warehouse_id),
            ).fetchone()
        else:
            row = self.db.execute(
                "SELECT TOP 1 WarehouseID, QuantityInStock FROM Inventory WHERE ProductID = ? ORDER BY WarehouseID",
                (int(product_id),),
            ).fetchone()
        warehouse_id = int(row[0] if row else 1)
        current_stock = int(row[1] if row else 0)

        if mode == "Tăng":
            new_stock = current_stock + int(quantity)
        else:
            new_stock = current_stock - int(quantity)
            if new_stock < 0:
                return False

        if row:
            self.db.execute(
                "UPDATE Inventory SET QuantityInStock = ?, LastUpdated = CAST(GETDATE() AS DATE) WHERE WarehouseID = ? AND ProductID = ?",
                (new_stock, warehouse_id, int(product_id)),
            )
        else:
            self.db.execute(
                "INSERT INTO Inventory (WarehouseID, ProductID, QuantityInStock, LastUpdated) VALUES (?, ?, ?, CAST(GETDATE() AS DATE))",
                (warehouse_id, int(product_id), new_stock),
            )

        self.db.commit()
        return True


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
        history_rows = self.handler.get_item_history(int(item.get("productID") or 0))
        for history in history_rows:
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
        success = self.handler.apply_inventory_adjustment(self.item, mode, quantity, note)
        if not success:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể cập nhật tồn kho. Vui lòng kiểm tra số lượng.")
            return
        self.accept()


class InventoryTabController:
    def __init__(self, window, db: Optional[Database] = None):
        self.window = window
        self.handler = InventoryHandler(db)
        self.inventory_items = []
        self.setup_handlers()
        self.refresh_table()

    def setup_handlers(self):
        self.window.tblTonKho.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.window.tblTonKho.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.window.txtTimKiemTK.setPlaceholderText("Nhập mã hoặc tên sản phẩm")

        if not hasattr(self.window, "btnChiTietTK"):
            self.window.btnChiTietTK = QtWidgets.QPushButton("Chi tiết", parent=self.window.pageTonKho)
            self.window.buttonLayout.insertWidget(1, self.window.btnChiTietTK)

        self.window.tblTonKho.itemDoubleClicked.connect(lambda _: self.open_detail())
        self.window.btnChiTietTK.clicked.connect(self.open_detail)
        self.window.btnCapNhatTK.clicked.connect(self.open_update)
        self.window.btnRefreshTK.clicked.connect(self.refresh_table)
        self.window.btnTimKiemTK.clicked.connect(self.filter_table)
        self.window.txtTimKiemTK.textChanged.connect(self.filter_table)

    def update_total_label(self):
        total_quantity = sum(int(item.get("soLuong", item.get("tonKho", 0)) or 0) for item in self.inventory_items)
        self.window.lblTongTK.setText(f"Tổng số lượng sản phẩm: {total_quantity}")

    def populate_table(self, items):
        self.window.tblTonKho.setRowCount(0)
        for item in items:
            row = self.window.tblTonKho.rowCount()
            self.window.tblTonKho.insertRow(row)
            self.window.tblTonKho.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("maKho", "")))
            self.window.tblTonKho.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get("maSP", "")))
            self.window.tblTonKho.setItem(row, 2, QtWidgets.QTableWidgetItem(item.get("tenSP", "")))
            self.window.tblTonKho.setItem(row, 3, QtWidgets.QTableWidgetItem(item.get("danhMuc", "")))
            self.window.tblTonKho.setItem(row, 4, QtWidgets.QTableWidgetItem(str(item.get("soLuong", 0))))

    def refresh_table(self):
        self.inventory_items = self.handler.list_items()
        self.populate_table(self.inventory_items)
        self.update_total_label()

    def get_selected(self):
        row = self.window.tblTonKho.currentRow()
        if row < 0:
            return None
        code = self.window.tblTonKho.item(row, 1).text()
        for item in self.inventory_items:
            if item.get("maSP") == code:
                return item
        return None

    def filter_table(self):
        keyword = self.window.txtTimKiemTK.text().strip().lower()
        if not keyword:
            self.populate_table(self.inventory_items)
            self.update_total_label()
            return

        filtered = [
            item
            for item in self.inventory_items
            if keyword in item.get("maSP", "").lower()
            or keyword in item.get("tenSP", "").lower()
            or keyword in item.get("danhMuc", "").lower()
        ]
        self.populate_table(filtered)
        self.window.lblTongTK.setText(f"Kết quả tìm kiếm: {len(filtered)} sản phẩm")

    def open_detail(self):
        item = self.get_selected()
        if item is None:
            QtWidgets.QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một sản phẩm để xem chi tiết.")
            return
        dialog = InventoryDetailDialog(self.handler, self.window)
        dialog.fill_item(item)
        dialog.setWindowTitle("Chi tiết tồn kho")
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_table()

    def open_update(self):
        item = self.get_selected()
        if item is None:
            QtWidgets.QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một sản phẩm để cập nhật tồn kho.")
            return
        dialog = InventoryUpdateDialog(self.handler, self.window)
        dialog.prepare_for_update(item)
        dialog.setWindowTitle("Cập nhật tồn kho")
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_table()
            QtWidgets.QMessageBox.information(self.window, "Thông báo", "Cập nhật tồn kho thành công!")
