"""Payment module handler: encapsulates payment business logic and DB access."""
from typing import Optional
from datetime import datetime
from database.database import Database


class PaymentHandler:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def list_payments(self):
        return self.db.get_payments()

    def get_payment(self, maTT: str):
        for p in self.list_payments():
            if p.get("maTT") == maTT:
                return p
        return None

    def confirm_payment(self, payment: dict):
        """Mark a payment as confirmed (Đã thanh toán) and persist to DB."""
        if not payment or "maTT" not in payment:
            return False
        payment["trangThai"] = "Đã thanh toán"
        payment["ngayTT"] = datetime.now().strftime("%d/%m/%Y")
        self.db.update_payment(payment)
        return True

    def delete_payment(self, maTT: str):
        self.db.delete_payment(maTT)


from PyQt6 import QtWidgets
from .payment_detail_ui import Ui_hopThoaiThanhToanChiTiet


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
        self.lblTongTien.setText(f"{payment.get('tongTien', 0):,} VND")

    def on_confirm(self):
        if self.payment is None:
            return
        # use handler to confirm
        success = self.handler.confirm_payment(self.payment)
        if success:
            QtWidgets.QMessageBox.information(self, "Thông báo", "Xác nhận thanh toán thành công!")
        else:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể xác nhận thanh toán.")
        self.accept()
