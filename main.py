import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from modules.main_window import Ui_phanTuChinhWindow
from modules.report.report import ReportPageController
from modules.employee.employee import EmployeePageController
from modules.customer.customer import CustomerPageController
from modules.product.product import ProductPageController
from modules.order.order import OrderPageController


class MainWindow(QMainWindow, Ui_phanTuChinhWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 1. Khởi tạo các Controller quản lý từng trang
        # Khi khởi tạo, các Controller này sẽ tự kết nối nút bấm và tự chuyển trang thông qua hàm __init__ của chúng
        self.employee_controller = EmployeePageController(self)
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

    # Đọc file giao diện CSS (QSS)
    try:
        with open("resources/styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Cảnh báo: Không tìm thấy file styles.qss")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())