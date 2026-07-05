"""Deprecated compatibility shim.

Use the root `main.py` runner and the main controller in
`modules/main/main_controller.py` for app startup.
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6 import QtWidgets
from modules.main.main_controller import MainController


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainController()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
