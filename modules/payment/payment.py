from __future__ import annotations

from datetime import date
import os
import sys
from typing import Optional

from PyQt6 import QtCore, QtWidgets

try:
    from connect import Database
except ModuleNotFoundError:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from connect import Database
from .payment_detail_ui import Ui_hopThoaiThanhToanChiTiet


class PaymentHandler:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    @staticmethod
    def _to_payment_code(payment_id: int) -> str:
        return f"TT{int(payment_id):03d}"

    @staticmethod
    def _to_order_code(order_id: int) -> str:
        return f"DH{int(order_id):03d}"

    @staticmethod
    def _parse_payment_code(code: str) -> Optional[int]:
        raw = (code or "").strip().upper()
        if raw.startswith("TT") and raw[2:].isdigit():
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

    def list_payments(self) -> list[dict]:
        query = """
            SELECT p.PaymentID, p.OrderID, p.Amount, p.PaymentMethod, p.PaymentStatus, p.PaymentDate,
                   o.CustomerID
            FROM Payment p
            LEFT JOIN [Order] o ON o.OrderID = p.OrderID
            ORDER BY p.PaymentID
        """
        rows = self.db.execute(query).fetchall()
        result = []
        for row in rows:
            payment_id = int(row[0] or 0)
            order_id = int(row[1] or 0)
            result.append(
                {
                    "paymentID": payment_id,
                    "maTT": self._to_payment_code(payment_id),
                    "maDH": self._to_order_code(order_id),
                    "orderID": order_id,
                    "tongTien": float(row[2] or 0),
                    "phuongThuc": row[3] or "",
                    "trangThai": row[4] or "",
                    "ngayTT": self._format_date(row[5]),
                    "khachHang": f"KH{int(row[6] or 0):03d}" if row[6] is not None else "",
                }
            )
        return result

    def confirm_payment(self, payment: dict):
        if not payment:
            return False
        payment_id = self._parse_payment_code((payment.get("maTT") or "").strip())
        if payment_id is None:
            return False

        self.db.execute(
            """
            UPDATE Payment
            SET PaymentStatus = ?, PaymentDate = CAST(GETDATE() AS DATE)
            WHERE PaymentID = ?
            """,
            ("Đã thanh toán", int(payment_id)),
        )
        self.db.commit()
        return True

    def delete_payment(self, maTT: str):
        payment_id = self._parse_payment_code((maTT or "").strip())
        if payment_id is None:
            return False
        self.db.execute("DELETE FROM Payment WHERE PaymentID = ?", (int(payment_id),))
        self.db.commit()
        return True


class PaymentDetailDialog(QtWidgets.QDialog, Ui_hopThoaiThanhToanChiTiet):
    def __init__(self, handler: PaymentHandler, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.handler = handler
        self.payment = None
        self.btnXacNhanTT.clicked.connect(self.on_confirm)
        self.btnClose.clicked.connect(self.reject)

    def fill_payment(self, payment):
        self.payment = payment
        self.lblMaTT.setText(payment.get("maTT", ""))
        self.lblMaDH.setText(payment.get("maDH", ""))
        self.lblTenKH.setText(payment.get("khachHang", ""))
        self.lblPhuongThucThanhToan.setText(payment.get("phuongThuc", ""))
        self.lblngayTT.setText(payment.get("ngayTT", "") or "--/--/----")
        self.lblTrangThaiTT.setText(payment.get("trangThai", ""))
        self.lblTongTien.setText(f"{payment.get('tongTien', 0):,.0f} VND")

    def on_confirm(self):
        if self.payment is None:
            return
        success = self.handler.confirm_payment(self.payment)
        if success:
            QtWidgets.QMessageBox.information(self, "Thông báo", "Đã thanh toán thành công!")
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể xác nhận thanh toán.")


class PaymentTabController:
    def __init__(self, window, db: Optional[Database] = None):
        self.window = window
        self.handler = PaymentHandler(db)
        self.payment_records = []
        self.setup_handlers()
        self.refresh_table()

    def setup_handlers(self):
        self.window.tblThanhToan.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.window.tblThanhToan.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        if not hasattr(self.window, "btnChiTietTT"):
            self.window.btnChiTietTT = QtWidgets.QPushButton("Chi tiết", parent=self.window.pageThanhToan)
            self.window.crudLayout.insertWidget(1, self.window.btnChiTietTT)

        self.window.tblThanhToan.itemDoubleClicked.connect(lambda _: self.open_detail())
        self.window.btnChiTietTT.clicked.connect(self.open_detail)
        self.window.btnXacNhanTT.clicked.connect(self.open_confirm_flow)
        self.window.btnXoaTT.clicked.connect(self.delete_selected)
        self.window.btnRefreshTT.clicked.connect(self.refresh_table)
        self.window.btnTimKiemTT.clicked.connect(self.filter_table)
        self.window.txtTimKiemTT.textChanged.connect(self.filter_table)

        self.window.txtTuNgayTT.setDate(QtCore.QDate(2000, 1, 1))
        self.window.txtDenNgayTT.setDate(QtCore.QDate(2000, 1, 1))
        self.window.txtTuNgayTT.dateChanged.connect(self.filter_table)
        self.window.txtDenNgayTT.dateChanged.connect(self.filter_table)

    def get_selected(self):
        row = self.window.tblThanhToan.currentRow()
        if row < 0:
            return None
        code = self.window.tblThanhToan.item(row, 4).text()
        for item in self.payment_records:
            if item.get("maTT") == code:
                return item
        return None

    def populate_table(self, items):
        self.window.tblThanhToan.setRowCount(0)
        for item in items:
            row = self.window.tblThanhToan.rowCount()
            self.window.tblThanhToan.insertRow(row)
            status = item.get("trangThai", "")
            payment_date = item.get("ngayTT", "") if status == "Đã thanh toán" else ""

            self.window.tblThanhToan.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("maDH", "")))
            self.window.tblThanhToan.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{item.get('tongTien', 0):,.0f}"))
            self.window.tblThanhToan.setItem(row, 2, QtWidgets.QTableWidgetItem(item.get("phuongThuc", "")))
            self.window.tblThanhToan.setItem(row, 3, QtWidgets.QTableWidgetItem(status))
            self.window.tblThanhToan.setItem(row, 4, QtWidgets.QTableWidgetItem(item.get("maTT", "")))
            self.window.tblThanhToan.setItem(row, 5, QtWidgets.QTableWidgetItem(payment_date))

    def refresh_table(self):
        self.payment_records = self.handler.list_payments()
        self.populate_table(self.payment_records)

    def filter_table(self):
        keyword = self.window.txtTimKiemTT.text().strip().lower()
        default_date = QtCore.QDate(2000, 1, 1)
        start = self.window.txtTuNgayTT.date()
        end = self.window.txtDenNgayTT.date()
        if start == default_date:
            start = None
        if end == default_date:
            end = None

        filtered = self.payment_records
        if keyword:
            filtered = [
                item
                for item in filtered
                if keyword in item.get("maTT", "").lower() or keyword in item.get("maDH", "").lower()
            ]

        def parse_date(text: str):
            if not text:
                return None
            qdate = QtCore.QDate.fromString(text, "dd/MM/yyyy")
            return qdate if qdate.isValid() else None

        if start is not None or end is not None:
            by_date = []
            for item in filtered:
                paid_date = parse_date(item.get("ngayTT", ""))
                if paid_date is None:
                    continue
                if start is not None and paid_date < start:
                    continue
                if end is not None and paid_date > end:
                    continue
                by_date.append(item)
            filtered = by_date

        self.populate_table(filtered)

    def open_detail(self):
        payment = self.get_selected()
        if payment is None:
            QtWidgets.QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một thanh toán để xem chi tiết.")
            return
        dialog = PaymentDetailDialog(self.handler, self.window)
        dialog.fill_payment(payment)
        dialog.setWindowTitle("Chi tiết thanh toán")
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_table()

    def open_confirm_flow(self):
        payment = self.get_selected()
        if payment is None:
            QtWidgets.QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một thanh toán để xác nhận.")
            return
        dialog = PaymentDetailDialog(self.handler, self.window)
        dialog.fill_payment(payment)
        dialog.setWindowTitle("Chi tiết thanh toán")
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_table()
            QtWidgets.QMessageBox.information(self.window, "Thông báo", "Đã thanh toán thành công!")

    def delete_selected(self):
        payment = self.get_selected()
        if payment is None:
            QtWidgets.QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một thanh toán để xóa.")
            return
        reply = QtWidgets.QMessageBox.question(
            self.window,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa thanh toán {payment.get('maTT', '')}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            deleted = self.handler.delete_payment(payment.get("maTT", ""))
            if deleted:
                self.refresh_table()
                QtWidgets.QMessageBox.information(self.window, "Thông báo", "Xóa thanh toán thành công!")
