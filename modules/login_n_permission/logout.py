from __future__ import annotations

from typing import Callable, Optional

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMessageBox

from modules.login_n_permission.login import LoginDialog


def handle_logout(
    main_window: QtWidgets.QWidget,
    on_login_success: Optional[Callable[[dict], None]] = None,
) -> bool:
    reply = QMessageBox.question(
        main_window,
        "Xác nhận đăng xuất",
        "Bạn có muốn đăng xuất tài khoản không?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )

    if reply != QMessageBox.StandardButton.Yes:
        return False

    main_window.hide()

    login_dialog = LoginDialog()
    result = login_dialog.exec()

    if result == QtWidgets.QDialog.DialogCode.Accepted:
        user_info = login_dialog.get_user_info() or {}
        if on_login_success is not None:
            on_login_success(user_info)
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        return True

    QApplication.instance().quit()
    return True