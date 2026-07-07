import pyodbc
from datetime import date

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QAbstractItemView, QDialog, QMessageBox, QTableWidgetItem

from connect import Database
from modules.employee.employee_add_ui import Ui_EmployeeFormDialog
from modules.employee.employee_detail_ui import Ui_EmployeeDetailDialog


class EmployeeFormDialog(QDialog, Ui_EmployeeFormDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent)
        self.setupUi(self)
        self.employee = employee
        self._prepare_form()
        self._connect_signals()

    def _connect_signals(self):
        self.btnLuuNV.clicked.connect(self._save_employee)
        self.btnHuyNV.clicked.connect(self.reject)

    def _prepare_form(self):
        self._populate_selectors()
        if self.employee:
            self.setWindowTitle("Cập nhật nhân viên")
            self._fill_form()
        else:
            self.setWindowTitle("Thêm nhân viên")
            self._fill_next_employee_id()
            self.lblNgaySinhNV.setDate(QtCore.QDate.currentDate())
            self.txtNgayTuyenDung.setDate(QtCore.QDate.currentDate())

    def _populate_selectors(self):
        departments = [
            "Quản trị",
            "Kinh doanh",
            "Quản lý sản phẩm",
            "Kho vận",
            "Kế toán",
        ]
        positions = [
            "Quản lý hệ thống",
            "Nhân viên bán hàng",
            "Nhân viên quản lý sản phẩm",
            "Nhân viên kho",
            "Điều phối giao hàng",
            "Kế toán thanh toán",
        ]

        self.cbbPhongBan.clear()
        self.cbbPhongBan.addItems(departments)

        self.cbbChucVu.clear()
        self.cbbChucVu.addItems(positions)

    def _fill_next_employee_id(self):
        try:
            db = Database()
            cursor = db.execute("SELECT ISNULL(MAX(EmployeeID), 0) + 1 FROM Employee")
            row = cursor.fetchone()
            next_id = row[0] if row and row[0] is not None else 1
            self.txtMaNV.setText(str(next_id))
            db.close()
        except Exception:
            self.txtMaNV.setText("")

    def _fill_form(self):
        employee = self.employee
        self.txtMaNV.setText(str(employee[0]))
        self.txtHoTenNV.setText(employee[1] or "")
        gender = (employee[2] or "").strip()
        self.rbNam.setChecked(gender.lower() == "nam")
        self.rbNu.setChecked(gender.lower() == "nữ" or gender.lower() == "nu")
        if isinstance(employee[3], date):
            self.lblNgaySinhNV.setDate(QtCore.QDate(employee[3].year, employee[3].month, employee[3].day))
        self.txtSDT_NV.setText(employee[4] or "")
        self.txtEmail_NV.setText(employee[5] or "")

        department = employee[6] or ""
        if department and self.cbbPhongBan.findText(department) == -1:
            self.cbbPhongBan.addItem(department)
        self.cbbPhongBan.setCurrentText(department)

        position = employee[7] or ""
        if position and self.cbbChucVu.findText(position) == -1:
            self.cbbChucVu.addItem(position)
        self.cbbChucVu.setCurrentText(position)

        if isinstance(employee[8], date):
            self.txtNgayTuyenDung.setDate(QtCore.QDate(employee[8].year, employee[8].month, employee[8].day))

    def _save_employee(self):
        employee_id = self.txtMaNV.text().strip()
        name = self.txtHoTenNV.text().strip()
        gender = "Nam" if self.rbNam.isChecked() else "Nữ" if self.rbNu.isChecked() else ""
        dob = self.lblNgaySinhNV.date().toPyDate()
        phone = self.txtSDT_NV.text().strip()
        email = self.txtEmail_NV.text().strip()
        department = self.cbbPhongBan.currentText().strip()
        position = self.cbbChucVu.currentText().strip()
        hire_date = self.txtNgayTuyenDung.date().toPyDate()

        if not name:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập họ và tên.")
            return
        if not gender:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn giới tính.")
            return
        if not phone:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập số điện thoại.")
            return
        if not position:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn chức vụ.")
            return

        try:
            db = Database()
            if self.employee:
                db.execute(
                    "UPDATE Employee SET EmpName = ?, EmpGender = ?, EmpDateOfBirth = ?, EmpPhone = ?, EmpEmail = ?, Department = ?, Position = ?, HireDate = ? WHERE EmployeeID = ?",
                    (name, gender, dob, phone, email, department, position, hire_date, int(employee_id)),
                )
            else:
                db.execute(
                    "INSERT INTO Employee (EmployeeID, EmpName, EmpGender, EmpDateOfBirth, EmpPhone, EmpEmail, Department, Position, HireDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (int(employee_id), name, gender, dob, phone, email, department, position, hire_date),
                )
            db.commit()
            db.close()
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi lưu", f"Không thể lưu nhân viên.\n{exc}")
            try:
                db.rollback()
                db.close()
            except Exception:
                pass


class EmployeeDetailDialog(QDialog, Ui_EmployeeDetailDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent)
        self.setupUi(self)
        self.employee = employee
        self.action_requested = None

        self.btnDongNV.clicked.connect(self.close)
        self.btnCapNhatNV.clicked.connect(self._request_update)
        self.btnXoaNV.clicked.connect(self._request_delete)

        if employee:
            self._fill_detail(employee)
            self._load_activity_table(employee[0])

    def _fill_detail(self, employee):
        self.txtMaNV.setText(str(employee[0]))
        self.txtHoTenNV.setText(employee[1] or "")
        self.txtGioiTinhNV.setText(employee[2] or "")
        if isinstance(employee[3], date):
            self.txtNgaySinhNV.setDate(QtCore.QDate(employee[3].year, employee[3].month, employee[3].day))
        self.txtSDT_NV.setText(employee[4] or "")
        self.txtEmailNV.setText(employee[5] or "")
        self.txtPhongBan.setText(employee[6] or "")
        self.txtChucVu.setText(employee[7] or "")
        if isinstance(employee[8], date):
            self.txtNgayTuyenDung.setDate(QtCore.QDate(employee[8].year, employee[8].month, employee[8].day))

    def _load_activity_table(self, employee_id):
        db = Database()
        try:
            self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
            self.tableView.setAlternatingRowColors(True)
            self.tableView.setColumnCount(4)
            self.tableView.setHorizontalHeaderLabels(["Loại hoạt động", "Mã liên quan", "Ngày", "Chi tiết"])

            query = """
                SELECT 'Đơn hàng' AS LoaiHoatDong, CAST(o.OrderID AS VARCHAR) AS MaLienQuan,
                       CAST(o.OrderDate AS DATE) AS Ngay,
                       CONCAT('Tổng tiền: ', FORMAT(o.TotalAmount, 'N0')) AS ChiTiet
                FROM [Order] o
                WHERE o.EmployeeID = ?
                UNION ALL
                SELECT 'Giao hàng' AS LoaiHoatDong, CAST(s.ShipmentID AS VARCHAR) AS MaLienQuan,
                       CAST(s.ShipmentDate AS DATE) AS Ngay,
                       CONCAT('Trạng thái: ', s.ShipmentStatus) AS ChiTiet
                FROM Shipment s
                WHERE s.EmployeeID = ?
                ORDER BY Ngay DESC
            """
            cursor = db.execute(query, (employee_id, employee_id))
            rows = cursor.fetchall()

            self.tableView.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    self.tableView.setItem(row_idx, col_idx, item)
            self.tableView.resizeColumnsToContents()
        except Exception as exc:
            QMessageBox.warning(self, "Thông báo", f"Không thể tải hoạt động nhân viên.\n{exc}")
        finally:
            db.close()

    def _request_update(self):
        self.action_requested = "update"
        self.accept()

    def _request_delete(self):
        self.action_requested = "delete"
        self.accept()

class EmployeePageController:
    def __init__(self, window):
        self.window = window
        self._ensure_core_page_controllers()
        self._ensure_core_navigation()
        self._connect_signals()
        self._prepare_table()
        self.load_employee_table()

    def _ensure_core_page_controllers(self):
        if not hasattr(self.window, "category_controller"):
            from modules.category.category import CategoryTabController

            self.window.category_controller = CategoryTabController(self.window)

        if not hasattr(self.window, "inventory_controller"):
            from modules.inventory.inventory import InventoryTabController

            self.window.inventory_controller = InventoryTabController(self.window)

        if not hasattr(self.window, "payment_controller"):
            from modules.payment.payment import PaymentTabController

            self.window.payment_controller = PaymentTabController(self.window)

    def _ensure_core_navigation(self):
        mapping = [
            ("btnDanhMuc", "pageDanhMuc"),
            ("btnTonKho", "pageTonKho"),
            ("btnThanhToan", "pageThanhToan"),
        ]
        for button_name, page_name in mapping:
            if hasattr(self.window, button_name) and hasattr(self.window, page_name):
                button = getattr(self.window, button_name)
                page = getattr(self.window, page_name)
                button.clicked.connect(lambda _=False, p=page: self.window.khungChuyenTrangStacked.setCurrentWidget(p))

    def _connect_signals(self):
        self.window.btnNhanVien.clicked.connect(self.show_employee_page)
        self.window.btnTimKiemNV.clicked.connect(self.search_employee)
        self.window.btnThemNV.clicked.connect(self.open_add_employee_dialog)
        self.window.btnChiTietNV.clicked.connect(self.open_employee_detail_dialog)
        self.window.btnCapNhatNV.clicked.connect(self.open_update_employee_dialog)
        self.window.btnXoaNV.clicked.connect(self.delete_employee)
        self.window.btnRefreshNV.clicked.connect(self.load_employee_table)

    def _prepare_table(self):
        self.window.tblNhanVien.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.window.tblNhanVien.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def show_employee_page(self):
        self.window.khungChuyenTrangStacked.setCurrentWidget(self.window.pageNhanVien)

    def _create_db(self):
        return Database()
 
    def _build_position_filter(self, position_text):
        if not position_text or position_text == "Tất cả":
            return None
        mapping = {
            "Nv bán hàng": "Nhân viên bán hàng",
            "Nv quản lý sản phẩm": "Nhân viên quản lý sản phẩm",
            "Nv kế toán": "Kế toán thanh toán",
            "Nv kho": "Nhân viên kho",
        }
        return mapping.get(position_text, position_text)

    def search_employee(self):
        employee_id = self.window.txtMaNV.text().strip()
        position = self.window.cbbChucVu.currentText()
        self.load_employee_table(employee_id=employee_id or None, position=position)

    def load_employee_table(self, employee_id=None, position=None):
        db = self._create_db()
        try:
            query = "SELECT EmployeeID, EmpName, EmpPhone, Position, Department, '' AS Status FROM Employee WHERE 1=1"
            params = []
            if employee_id:
                query += " AND EmployeeID = ?"
                params.append(employee_id)
            filter_position = self._build_position_filter(position)
            if filter_position:
                query += " AND Position LIKE ?"
                params.append(f"%{filter_position}%")
            query += " ORDER BY EmployeeID"
            cursor = db.execute(query, params if params else None)
            rows = cursor.fetchall()
            self._render_employee_table(rows)
        except Exception as exc:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải danh sách nhân viên.\n{exc}")
        finally:
            db.close()

    def _render_employee_table(self, rows):
        self.window.tblNhanVien.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value) if value is not None else "")
                self.window.tblNhanVien.setItem(row_index, col_index, item)
        self.window.tblNhanVien.resizeColumnsToContents()

    def _get_selected_employee_id(self):
        selected = self.window.tblNhanVien.selectedItems()
        if not selected:
            return None
        item = self.window.tblNhanVien.item(selected[0].row(), 0)
        if item is None:
            return None
        return item.text().strip()

    def _load_employee_record(self, employee_id):
        if not employee_id:
            return None
        db = self._create_db()
        try:
            cursor = db.execute(
                "SELECT EmployeeID, EmpName, EmpGender, EmpDateOfBirth, EmpPhone, EmpEmail, Department, Position, HireDate FROM Employee WHERE EmployeeID = ?",
                (employee_id,),
            )
            return cursor.fetchone()
        except Exception as exc:
            QMessageBox.critical(self.window, "Lỗi dữ liệu", f"Không thể tải nhân viên.\n{exc}")
            return None
        finally:
            db.close()

    def open_add_employee_dialog(self):
        dialog = EmployeeFormDialog(self.window)
        if dialog.exec():
            self.load_employee_table()

    def open_employee_detail_dialog(self):
        employee_id = self._get_selected_employee_id()
        if not employee_id:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn nhân viên để xem chi tiết.")
            return
        
        employee = self._load_employee_record(employee_id)
        if employee:
            dialog = EmployeeDetailDialog(self.window, employee)
            
            # Chờ người dùng tương tác với Dialog chi tiết
            dialog.exec()
            
            # Kiểm tra xem người dùng có bấm Cập nhật hoặc Xóa từ trong Dialog chi tiết không
            if dialog.action_requested == "update":
                self.open_update_employee_dialog()
            elif dialog.action_requested == "delete":
                self.delete_employee()

    def open_update_employee_dialog(self):
        employee_id = self._get_selected_employee_id()
        if not employee_id:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn nhân viên để cập nhật.")
            return
        employee = self._load_employee_record(employee_id)
        if employee:
            dialog = EmployeeFormDialog(self.window, employee=employee)
            if dialog.exec():
                self.load_employee_table()

    def delete_employee(self):
        employee_id = self._get_selected_employee_id()
        if not employee_id:
            QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn nhân viên để xóa.")
            return
        employee = self._load_employee_record(employee_id)
        if not employee:
            return

        answer = QMessageBox.question(
            self.window,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa nhân viên {employee[1]} ({employee[0]}) không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        db = self._create_db()
        try:
            db.execute("DELETE FROM Employee WHERE EmployeeID = ?", (employee_id,))
            db.commit()
            QMessageBox.information(self.window, "Thành công", "Nhân viên đã được xóa.")
            self.load_employee_table()
        except pyodbc.Error as exc:
            QMessageBox.critical(self.window, "Lỗi xóa", f"Không thể xóa nhân viên.\n{exc}")
        finally:
            db.close()
