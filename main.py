import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from modules.main_window import Ui_phanTuChinhWindow


class MainWindow(QMainWindow, Ui_phanTuChinhWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


app = QApplication(sys.argv)

with open("resources/styles.qss", "r", encoding="utf-8") as f:
    app.setStyleSheet(f.read())

window = MainWindow()
window.show()

sys.exit(app.exec())