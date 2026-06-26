from PyQt6 import uic
from PyQt6.QtWidgets import QApplication

app = QApplication([])

with open("theme.qss", "r", encoding="utf-8") as f:
    app.setStyleSheet(f.read())

window = uic.loadUi("ui/main_window.ui")
window.show()

app.exec()