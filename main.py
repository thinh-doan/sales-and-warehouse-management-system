import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from modules.main_window import Ui_phanTuChinhWindow
from modules.report.report import ReportPageController


class MainWindow(QMainWindow, Ui_phanTuChinhWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # gọi hàm xử lý pageBaoCao
        self.btnBaoCao.clicked.connect(self.show_report_page)
        self.report_controller = ReportPageController(self)

    def show_report_page(self):
        self.khungChuyenTrangStacked.setCurrentWidget(self.pageBaoCao)


app = QApplication(sys.argv)

with open("resources/styles.qss", "r", encoding="utf-8") as f:
    app.setStyleSheet(f.read())

window = MainWindow()
window.show()

sys.exit(app.exec())