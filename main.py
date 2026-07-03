import sys
from pathlib import Path

from PyQt6 import QtCore, QtWidgets, uic


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sales & Warehouse Management")
        self.resize(1280, 820)

        ui_path = Path(__file__).resolve().parent / "ui" / "main_window.ui"
        uic.loadUi(ui_path, self)

        self._apply_theme()

    def _apply_theme(self) -> None:
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.setStyle("Fusion")

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f4f7fb;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            #khungSidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2563eb, stop:1 #0f172a);
                border: none;
                border-radius: 20px;
            }
            #khungSidebar QLabel {
                color: white;
            }
            #khungSidebar QPushButton {
                color: #e2e8f0;
                background: transparent;
                text-align: left;
                padding: 10px 14px;
                border: none;
                border-radius: 10px;
                margin: 2px 0;
            }
            #khungSidebar QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.14);
            }
            #khungSidebar QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.22);
            }
            #khungChuyenTrangStacked {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 20px;
            }
            QLabel {
                color: #0f172a;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox, QTableWidget {
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px;
                background-color: white;
            }
            QTableWidget {
                gridline-color: #e2e8f0;
            }
            """
        )

        logo_label = self.findChild(QtWidgets.QLabel, "label_2")
        title_label = self.findChild(QtWidgets.QLabel, "label")
        if logo_label is not None:
            logo_label.setText("📦")
            logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            logo_label.setStyleSheet("font-size: 24px;")
        if title_label is not None:
            title_label.setText("Smart Warehouse")
            title_label.setStyleSheet("font-size: 16px; font-weight: 700;")

        for label in self.findChildren(QtWidgets.QLabel):
            if label.objectName().startswith("lblTitle"):
                label.setStyleSheet(
                    "background-color: #eff6ff; color: #1d4ed8; padding: 10px 14px; "
                    "border-radius: 10px; font-weight: 700;"
                )


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
