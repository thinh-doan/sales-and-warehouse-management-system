import pyodbc
from datetime import date

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QAbstractItemView, QDialog, QMessageBox, QTableWidgetItem

from connect import Database
from modules.partner.partner_add_ui import Ui_PartnerAddDialog
from modules.partner.partner_detail_ui import Ui_PartnerAddDialog as Ui_PartnerDetailDialog


class PartnerFormDialog(QDialog, Ui_PartnerAddDialog):
    def __init__(self, parent=None, partner=None):
        super().__init__(parent)
        self.setupUi(self)
        self.partner = partner
        self._prepare_form()
        self._connect_signals()

    def _connect_signals(self):
        self.btnLuuDT.clicked.connect(self._save_partner)
        self.btnHuyDT.clicked.connect(self.reject)

    def _prepare_form(self):
        if self.partner:
            self.setWindowTitle("Cập nhật đối tác")
            self._fill_form()
        else:
            self.setWindowTitle("Thêm đối tác")
            self._fill_next_partner_id()

    def _fill_next_partner_id(self):
        try:
            db = Database()
            cursor = db.execute("SELECT ISNULL(MAX(PartnerID), 0) + 1 FROM Delivery_Partner")
            row = cursor.fetchone()
            next_id = row[0] if row and row[0] is not None else 1
            self.txtMaDT.setText(str(next_id))
            db.close()
        except Exception:
            self.txtMaDT.setText("")

    def _fill_form(self):
        partner = self.partner
        self.txtMaDT.setText(str(partner[0]))
        self.txtTenDT.setText(partner[1] or "")
        self.txtSDT_DT.setText(partner[2] or "")
        self.txtEmai_DT.setText(partner[3] or "")
        self.txtDiaChiDT.setText(partner[4] or "")

        db = Database()
        try:
            cursor = db.execute(
                "SELECT ShippingMethodName FROM Prt_Shipping_Methods WHERE PartnerID = ?",
                (partner[0],),
            )
            methods = {row[0] for row in cursor.fetchall()}
            self._set_shipping_methods(methods)
        except Exception:
            pass
        finally:
            db.close()

    def _set_shipping_methods(self, methods):
        self.rbTieuchuan.setChecked("Tiêu chuẩn" in methods)
        self.rbTietKiem.setChecked("Tiết kiệm" in methods)
        self.rbHoaToc.setChecked("Hỏa tốc" in methods)

    def _get_selected_methods(self):
        methods = []
        if self.rbTieuchuan.isChecked():
            methods.append("Tiêu chuẩn")
        if self.rbTietKiem.isChecked():
            methods.append("Tiết kiệm")
        if self.rbHoaToc.isChecked():
            methods.append("Hỏa tốc")
        return methods

    def _save_partner(self):
        partner_id = self.txtMaDT.text().strip()
        name = self.txtTenDT.text().strip()
        phone = self.txtSDT_DT.text().strip()
        email = self.txtEmai_DT.text().strip()
        address = self.txtDiaChiDT.text().strip()
        methods = self._get_selected_methods()

        if not name:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập tên đối tác.")
            return
        if not methods:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn ít nhất một phương thức vận chuyển.")
            return

        try:
            db = Database()
            if self.partner:
                db.execute(
                    "UPDATE Delivery_Partner SET PrtName = ?, PrtPhone = ?, PrtEmail = ?, PrtAddress = ? WHERE PartnerID = ?",
                    (name, phone, email, address, int(partner_id)),
                )
                db.execute("DELETE FROM Prt_Shipping_Methods WHERE PartnerID = ?", (int(partner_id),))
            else:
                db.execute(
                    "INSERT INTO Delivery_Partner (PartnerID, PrtName, PrtPhone, PrtEmail, PrtAddress) VALUES (?, ?, ?, ?, ?)",
                    (int(partner_id), name, phone, email, address),
                )
            for method in methods:
                db.execute(
                    "INSERT INTO Prt_Shipping_Methods (PartnerID, ShippingMethodName) VALUES (?, ?)",
                    (int(partner_id), method),
                )
            db.commit()
            db.close()
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi lưu", f"Không thể lưu đối tác.\n{exc}")
            try:
                db.rollback()
                db.close()
            except Exception:
                pass


class PartnerDetailDialog(QDialog, Ui_PartnerDetailDialog):
    def __init__(self, parent=None, partner=None):
        super().__init__(parent)
        self.setupUi(self)
        self.partner = partner
        self.action_requested = None
        self.btnCloseDT.clicked.connect(self.close)
        self.btnCapNhatDT.clicked.connect(self._request_update)
        self.btnXoaDT.clicked.connect(self._request_delete)
        if partner:
            self._fill_detail(partner)
            self._load_summary(partner[0])
            self._load_history(partner[0])

    def _fill_detail(self, partner):
        self.txtMaDT.setText(str(partner[0]))
        self.txtTenDT.setText(partner[1] or "")
        self.txtSDT_DT.setText(partner[2] or "")
        self.txtEmail_DT.setText(partner[3] or "")
        self.txtDiaChiDT.setText(partner[4] or "")

        db = Database()
        try:
            cursor = db.execute(
                "SELECT ShippingMethodName FROM Prt_Shipping_Methods WHERE PartnerID = ? ORDER BY ShippingMethodName",
                (partner[0],),
            )
            methods = ", ".join(row[0] for row in cursor.fetchall() if row[0])
            self.txtPhuongThucVC.setText(methods)
        except Exception:
            self.txtPhuongThucVC.setText("")
        finally:
            db.close()

    def _load_summary(self, partner_id):
        db = Database()
        try:
            cursor = db.execute(
                """
                SELECT
                    COUNT(s.ShipmentID),
                    SUM(CASE WHEN s.ShipmentStatus = N'Giao thành công' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN s.ShipmentStatus = N'Giao thất bại' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN s.ShipmentStatus = N'Giao thành công' THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(s.ShipmentID), 0),
                    SUM(s.ShippingFee)
                FROM Shipment s
                WHERE s.PartnerID = ?
                """,
                (partner_id,),
            )
            row = cursor.fetchone()
            if row:
                self.lblTongSoDon.setText(str(row[0] or 0))
                self.lblDonThanhCong.setText(str(row[1] or 0))
                self.lblDonThatBai.setText(str(row[2] or 0))
                self.lblTiLeThanhCong.setText(f"{(row[3] or 0) * 100:.1f}%")
                self.lblTongPhiVC.setText(f"{row[4] or 0:,.0f}")
        except Exception:
            pass
        finally:
            db.close()

    def _load_history(self, partner_id):
        db = Database()
        try:
            cursor = db.execute(
                """
                SELECT s.ShipmentID, s.OrderID, s.ShippingFee, s.ShipmentDate, s.ShipmentStatus
                FROM Shipment s
                WHERE s.PartnerID = ?
                ORDER BY s.ShipmentDate DESC
                """,
                (partner_id,),
            )
            rows = cursor.fetchall()
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setHorizontalHeaderLabels(["Mã giao hàng", "Mã đơn hàng", "Phí", "Ngày", "Trạng thái"])
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    self.tableWidget.setItem(row_idx, col_idx, item)
            self.tableWidget.resizeColumnsToContents()
        except Exception as exc:
            QMessageBox.warning(self, "Thông báo", f"Không thể tải lịch sử giao hàng.\n{exc}")
        finally:
            db.close()

    def _request_update(self):
        self.action_requested = "update"
        self.accept()

    def _request_delete(self):
        # THAY ĐỔI TẠI ĐÂY: Thêm xác nhận ngay trong form chi tiết trước khi đóng
        answer = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa đối tác {self.partner[1]} ({self.partner[0]}) không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.action_requested = "delete"
            self.accept()


class PartnerPageController:
    def __init__(self, window):
        self.window = window
        self._connect_signals()
        self._prepare_table()
        self.load_partner_table()

    def _connect_signals(self):
        self.window.btnDoiTac.clicked.connect(self.show_partner_page)
        self.window.btnTimKiemDT.clicked.connect(self.search_partner)
        self.window.btnThemDT.clicked.connect(self.open_add_partner_dialog)
        self.window.btnChiTietDT.clicked.connect(self.open_detail_partner_dialog)
        self.window.btnCapNhatDT.clicked.connect(self.open_update_partner_dialog)
        self.window.btnXoaDT.clicked.connect(self.delete_partner_with_confirm)  # Đổi sang hàm mới
        self.window.btnRefreshDT.clicked.connect(self.load_partner_table)

    def _prepare_table(self):
        self.window.tblDoiTac.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.window.tblDoiTac.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def show_partner_page(self):
        self.window.khungChuyenTrangStacked.setCurrentWidget(self.window.pageDoiTacVC)

    def _create_db(self):
        return Database()

    def search_partner(self):
        keyword = self.window.txtTimKiemDT.text().strip()
        self.load_partner_table(keyword=keyword or None)

    def load_partner_table(self, keyword=None):
        db = self._create_db()
        try:
            query = """
                SELECT dp.PartnerID, dp.PrtName, dp.PrtPhone, dp.PrtEmail, dp.PrtAddress,
                       COALESCE(STUFF((SELECT ', ' + sm.ShippingMethodName
                                      FROM Prt_Shipping_Methods sm
                                      WHERE sm.PartnerID = dp.PartnerID
                                      FOR XML PATH('')), 1, 2, ''), '') AS ShippingMethods
                FROM Delivery_Partner dp
                WHERE 1=1
            """
            params = []
            if keyword:
                query += " AND (CAST(dp.PartnerID AS NVARCHAR) LIKE ? OR dp.PrtName LIKE ? )"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            query += " ORDER BY dp.PartnerID"
            cursor = db.execute(query, params if params else None)
            rows = cursor.fetchall()
            self._render_partner_table(rows)
        except Exception as exc:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải danh sách đối tác.\n{exc}")
        finally:
            db.close()

    def _render_partner_table(self, rows):
        existing_widths = [self.window.tblDoiTac.columnWidth(i) for i in range(self.window.tblDoiTac.columnCount())]
        should_autofit = not existing_widths or all(width == 100 for width in existing_widths)

        self.window.tblDoiTac.setRowCount(len(rows))
        self.window.tblDoiTac.setColumnCount(6)
        self.window.tblDoiTac.setHorizontalHeaderLabels(["Mã ĐT", "Tên ĐT", "SĐT", "Email", "Địa chỉ", "Phương thức VC"])
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value) if value is not None else "")
                self.window.tblDoiTac.setItem(row_index, col_index, item)

        if should_autofit:
            self.window.tblDoiTac.resizeColumnsToContents()
        else:
            for column_index, width in enumerate(existing_widths[: self.window.tblDoiTac.columnCount()]):
                self.window.tblDoiTac.setColumnWidth(column_index, width)

    def _get_selected_partner_id(self):
        selected = self.window.tblDoiTac.selectedItems()
        if not selected:
            return None
        item = self.window.tblDoiTac.item(selected[0].row(), 0)
        if item is None:
            return None
        return item.text().strip()

    def _load_partner_record(self, partner_id):
        if not partner_id:
            return None
        db = self._create_db()
        try:
            cursor = db.execute(
                "SELECT PartnerID, PrtName, PrtPhone, PrtEmail, PrtAddress FROM Delivery_Partner WHERE PartnerID = ?",
                (partner_id,),
            )
            return cursor.fetchone()
        except Exception as exc:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải đối tác.\n{exc}")
            return None
        finally:
            db.close()

    def open_add_partner_dialog(self):
        dialog = PartnerFormDialog(self.window)
        if dialog.exec():
            self.load_partner_table()

    def open_detail_partner_dialog(self):
        partner_id = self._get_selected_partner_id()
        if not partner_id:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn đối tác để xem chi tiết.")
            return
        partner = self._load_partner_record(partner_id)
        if partner:
            dialog = PartnerDetailDialog(self.window, partner)
            result = dialog.exec()
            if result:
                if dialog.action_requested == "update":
                    self.open_update_partner_dialog()
                elif dialog.action_requested == "delete":
                    # THAY ĐỔI TẠI ĐÂY: Vì Dialog đã confirm rồi nên ở đây xóa trực tiếp, không hỏi lại lần 2
                    self._execute_delete(partner_id)

    def open_update_partner_dialog(self):
        partner_id = self._get_selected_partner_id()
        if not partner_id:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn đối tác để cập nhật.")
            return
        partner = self._load_partner_record(partner_id)
        if partner:
            dialog = PartnerFormDialog(self.window, partner=partner)
            if dialog.exec():
                self.load_partner_table()

    def delete_partner_with_confirm(self):
        """Hàm này xử lý khi click nút Xóa từ bảng danh sách chính (Cần Confirm)"""
        partner_id = self._get_selected_partner_id()
        if not partner_id:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn đối tác để xóa.")
            return
        partner = self._load_partner_record(partner_id)
        if not partner:
            return

        answer = QMessageBox.question(
            self.window,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa đối tác {partner[1]} ({partner[0]}) không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._execute_delete(partner_id)

    def _execute_delete(self, partner_id):
        """Hàm lõi thực hiện câu lệnh SQL DELETE tách biệt"""
        db = self._create_db()
        try:
            db.execute("DELETE FROM Prt_Shipping_Methods WHERE PartnerID = ?", (partner_id,))
            db.execute("DELETE FROM Shipment WHERE PartnerID = ?", (partner_id,))
            db.execute("DELETE FROM Delivery_Partner WHERE PartnerID = ?", (partner_id,))
            db.commit()
            QMessageBox.information(self.window, "Thành công", "Đối tác đã được xóa.")
            self.load_partner_table()
        except pyodbc.Error as exc:
            QMessageBox.critical(self.window, "Lỗi xóa", f"Không thể xóa đối tác.\n{exc}")
        finally:
            db.close()