import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from modules.main_window import Ui_phanTuChinhWindow
from modules.login_n_permission.role import RolePermissionManager
from modules.login_n_permission.login import LoginDialog
from modules.employee.employee import EmployeePageController
from modules.partner.partner import PartnerPageController
from modules.report.report import ReportPageController
from modules.customer.customer import CustomerPageController
from modules.product.product import ProductPageController
from modules.order.order import OrderPageController


class MainWindow(QMainWindow, Ui_phanTuChinhWindow):
    def __init__(self, user_info=None):
        super().__init__()
        self.setupUi(self)
        self.current_user = user_info or {}
        self.permission_manager = RolePermissionManager()

        self._connect_navigation()

        # Các controller hiện có vẫn được khởi tạo như trước.
        self.employee_controller = EmployeePageController(self)
        self.partner_controller = PartnerPageController(self)
        self.report_controller = ReportPageController(self)
        self.customer_controller = CustomerPageController(self)
        self.product_controller = ProductPageController(self)
        self.order_controller = OrderPageController(self)

        # 2. Kết nối nút bấm cho những trang chưa có Controller riêng (nếu có)
        self.btnBaoCao.clicked.connect(self.show_report_page)
        if hasattr(self, 'btnDonhang'):
            self.btnDonhang.clicked.connect(self.show_order_page)
        if hasattr(self, 'btnKhachHang'):
            self.btnKhachHang.clicked.connect(self.show_customer_page)
        if hasattr(self, 'btnSanPham'):
            self.btnSanPham.clicked.connect(self.show_product_page)

    def show_report_page(self):
        self.khungChuyenTrangStacked.setCurrentWidget(self.pageBaoCao)

    def show_customer_page(self):
        if hasattr(self, 'khungChuyenTrangStacked') and hasattr(self, 'pageKhachHang'):
            self.khungChuyenTrangStacked.setCurrentWidget(self.pageKhachHang)
            self.customer_controller.load_customer_table()

    def show_product_page(self):
        if hasattr(self, 'khungChuyenTrangStacked') and hasattr(self, 'pageSanPham'):
            self.khungChuyenTrangStacked.setCurrentWidget(self.pageSanPham)
            self.product_controller.load_product_table()

    def show_order_page(self):
        if hasattr(self, 'khungChuyenTrangStacked') and hasattr(self, 'pageDonHang'):
            self.khungChuyenTrangStacked.setCurrentWidget(self.pageDonHang)
            self.order_controller.load_order_table()


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