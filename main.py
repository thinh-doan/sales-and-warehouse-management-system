import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from modules.login_n_permission.role import RolePermissionManager
from modules.login_n_permission.login import LoginDialog

from modules.employee.employee import EmployeePageController
from modules.main_window import Ui_phanTuChinhWindow
from modules.partner.partner import PartnerPageController
from modules.report.report import ReportPageController
from modules.customer.customer import CustomerPageController
from modules.product.product import ProductPageController
from modules.order.order import OrderPageController
from modules.shipment.shipment import ShipmentPageController
from modules.dashboard.dashboard import DashboardPageController



class MainWindow(QMainWindow, Ui_phanTuChinhWindow):
    def __init__(self, user_info=None):
        super().__init__()
        self.setupUi(self)
        self.current_user = user_info or {}
        self.permission_manager = RolePermissionManager()

        self._connect_navigation()

        self.employee_controller = EmployeePageController(self)
        self.partner_controller = PartnerPageController(self)
        self.report_controller = ReportPageController(self)
        self.customer_controller = CustomerPageController(self)
        self.product_controller = ProductPageController(self)
        self.order_controller = OrderPageController(self)
        self.shipment_controller = ShipmentPageController(self)
        self.dashboard_controller = DashboardPageController(self)
        self.btnBaoCao.clicked.connect(self.show_report_page)

        self.current_role_key = self.permission_manager.apply(self, self.current_user)
        self._show_default_page()

    def _connect_navigation(self):
        self.btnTongQuan.clicked.connect(lambda: self._show_page(self.pageTongQuan))
        self.btnDonhang.clicked.connect(lambda: self._show_page(self.pageDonHang))
        self.btnKhachHang.clicked.connect(lambda: self._show_page(self.pageKhachHang))
        self.btnSanPham.clicked.connect(lambda: self._show_page(self.pageSanPham))
        self.btnDanhMuc.clicked.connect(lambda: self._show_page(self.pageDanhMuc))
        self.btnTonKho.clicked.connect(lambda: self._show_page(self.pageTonKho))
        self.btnThanhToan.clicked.connect(lambda: self._show_page(self.pageThanhToan))
        self.btnVanChuyen.clicked.connect(lambda: self._show_page(self.pageVanChuyen))
        self.btnNhanVien.clicked.connect(lambda: self._show_page(self.pageNhanVien))
        self.btnBaoCao.clicked.connect(lambda: self._show_page(self.pageBaoCao))
        self.btnDangXuat.clicked.connect(self.logout)

    def _show_page(self, page_widget):
        if page_widget is not None and page_widget.isEnabled():
            self.khungChuyenTrangStacked.setCurrentWidget(page_widget)

    def _show_default_page(self):
        self._show_page(self.pageTongQuan)

    def logout(self):
        QApplication.instance().quit()

# Test coi nếu bỏ có chạy dc ko
    # def show_report_page(self):
    #     self._show_page(self.pageBaoCao)


    # def show_customer_page(self):
    #     if hasattr(self, 'khungChuyenTrangStacked') and hasattr(self, 'pageKhachHang'):
    #         self.khungChuyenTrangStacked.setCurrentWidget(self.pageKhachHang)
    #         # Kiểm tra xem controller và hàm load dữ liệu có tồn tại không trước khi gọi
    #         if hasattr(self, 'customer_controller') and hasattr(self.customer_controller, 'load_customer_table'):
    #             self.customer_controller.load_customer_table()

    # def show_product_page(self):
    #     if hasattr(self, 'khungChuyenTrangStacked') and hasattr(self, 'pageSanPham'):
    #         self.khungChuyenTrangStacked.setCurrentWidget(self.pageSanPham)
    #         if hasattr(self, 'product_controller') and hasattr(self.product_controller, 'load_product_table'):
    #             self.product_controller.load_product_table()

    # def show_order_page(self):
    #     if hasattr(self, 'khungChuyenTrangStacked') and hasattr(self, 'pageDonHang'):
    #         self.khungChuyenTrangStacked.setCurrentWidget(self.pageDonHang)
    #         if hasattr(self, 'order_controller') and hasattr(self.order_controller, 'load_order_table'):
    #             self.order_controller.load_order_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        with open("resources/styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Cảnh báo: Không tìm thấy file styles.qss")

    login_dialog = LoginDialog()
    if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
        user_data = login_dialog.get_user_info()
        print(f"Chào mừng {user_data.get('employee_name', 'người dùng')} đăng nhập thành công!")
        window = MainWindow(user_info=user_data)
        window.show()
        sys.exit(app.exec())

    print("Ứng dụng kết thúc do hủy đăng nhập.")
    sys.exit(0)