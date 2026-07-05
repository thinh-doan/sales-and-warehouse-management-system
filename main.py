import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from modules.main_window import Ui_phanTuChinhWindow
from modules.report.report import ReportPageController
# Import thêm EmployeePageController (bạn hãy sửa lại đường dẫn module cho đúng với project của mình)
from modules.employee.employee import EmployeePageController 


class MainWindow(QMainWindow, Ui_phanTuChinhWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 1. Khởi tạo các Controller quản lý từng trang 
        # Khi khởi tạo, các Controller này sẽ tự kết nối nút bấm và tự chuyển trang thông qua hàm __init__ của chúng
        self.employee_controller = EmployeePageController(self)
        self.report_controller = ReportPageController(self)
        
        # 2. Kết nối nút bấm cho những trang chưa có Controller riêng (nếu có)
        self.btnBaoCao.clicked.connect(self.show_report_page)

    def show_report_page(self):
        self.khungChuyenTrangStacked.setCurrentWidget(self.pageBaoCao)


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