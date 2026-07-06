from __future__ import annotations

import os
import sys

from PyQt6 import QtWidgets
try:
    from connect import Database
except ModuleNotFoundError:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from connect import Database
from modules.category.category import CategoryTabController
from modules.inventory.inventory import InventoryTabController
from modules.payment.payment import PaymentTabController
from ui.main_window import Ui_phanTuChinhWindow


class MainController(QtWidgets.QMainWindow, Ui_phanTuChinhWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db = Database()
        self.category_tab = CategoryTabController(self, self.db)
        self.inventory_tab = InventoryTabController(self, self.db)
        self.payment_tab = PaymentTabController(self, self.db)

        self._setup_navigation()

    def _setup_navigation(self):
        mapping = [
            ("btnTongQuan", "pageTongQuan"),
            ("btnDonhang", "pageDonHang"),
            ("btnKhachHang", "pageKhachHang"),
            ("btnSanPham", "pageSanPham"),
            ("btnDanhMuc", "pageDanhMuc"),
            ("btnTonKho", "pageTonKho"),
            ("btnThanhToan", "pageThanhToan"),
            ("btnVanChuyen", "pageVanChuyen"),
            ("btnNhanVien", "pageNhanVien"),
            ("btnBaoCao", "pageBaoCao"),
        ]
        for button_name, page_name in mapping:
            if hasattr(self, button_name) and hasattr(self, page_name):
                button = getattr(self, button_name)
                page = getattr(self, page_name)
                button.clicked.connect(lambda _=False, p=page: self.khungChuyenTrangStacked.setCurrentWidget(p))

        if hasattr(self, "pageDanhMuc"):
            self.khungChuyenTrangStacked.setCurrentWidget(self.pageDanhMuc)

    def closeEvent(self, event):
        try:
            self.db.close()
        finally:
            super().closeEvent(event)
