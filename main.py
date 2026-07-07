import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

# Import các giao diện từ các module của bạn
from modules.main_window import Ui_phanTuChinhWindow
from modules.report.report import ReportPageController
from modules.employee.employee import EmployeePageController
from modules.partner.partner import PartnerPageController

# Import LoginDialog từ file login vừa tách ở trên
from modules.login.login import LoginDialog 


class MainWindow(QMainWindow, Ui_phanTuChinhWindow):
    def __init__(self, user_info=None):
        super().__init__()
        self.setupUi(self)
        self.current_user = user_info # Lưu thông tin user để phân quyền nếu cần

        # 1. Khởi tạo các Controller quản lý từng trang 
        self.employee_controller = EmployeePageController(self)
        self.partner_controller = PartnerPageController(self)
        self.report_controller = ReportPageController(self)
        
        # 2. Kết nối nút bấm chuyển trang
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

    # BƯỚC 1: Khởi chạy cửa sổ đăng nhập trước
    login_dialog = LoginDialog()
    
    # exec() giúp biến login thành cửa sổ ưu tiên, chặn code chạy tiếp cho đến khi có kết quả
    if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
        
        # BƯỚC 2: Đăng nhập thành công -> Lấy thông tin user
        user_data = login_dialog.get_user_info()
        print(f"Chào mừng {user_data['employee_name']} đăng nhập thành công!")
        
        # BƯỚC 3: Mở cửa sổ chính và truyền data user vào
        window = MainWindow(user_info=user_data)
        window.show()
        
        # Duy trì ứng dụng chạy
        sys.exit(app.exec())
    else:
        # Người dùng tắt form login hoặc bấm Thoát
        print("Ứng dụng kết thúc do hủy đăng nhập.")
        sys.exit(0)