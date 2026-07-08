import pyodbc
from datetime import date

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from connect import Database
from modules.employee.employee_add_ui import Ui_EmployeeFormDialog
from modules.employee.employee_detail_ui import Ui_EmployeeDetailDialog

# =====================================================================
# 1. CLASS FORM THÊM / CẬP NHẬT NHÂN VIÊN (DIALOG)
# =====================================================================
class EmployeeFormDialog(QDialog, Ui_EmployeeFormDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent)
        self.setupUi(self)
        self.employee = employee
        
        # Cấu hình bảng ánh xạ: Phòng ban -> Chức vụ tương ứng
        self.ROLE_MAPPING = {
            "Quản trị": {"position": "Quản lý hệ thống"},
            "Kinh doanh": {"position": "Nhân viên bán hàng"},
            "Quản lý sản phẩm": {"position": "Nhân viên quản lý sản phẩm"},
            "Kho vận": {"position": "Nhân viên kho"},
            "Kế toán": {"position": "Kế toán thanh toán"}
        }
        
        self._prepare_form()
        self._connect_signals()

    def _connect_signals(self):
        self.btnLuuNV.clicked.connect(self._save_employee)
        self.btnHuyNV.clicked.connect(self.reject)
        
        # Tự động cập nhật Chức vụ khi người dùng đổi Phòng ban
        self.cbbPhongBan.currentTextChanged.connect(self._on_department_changed)

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
        # Đổ danh sách phòng ban vào ComboBox
        self.cbbPhongBan.clear()
        self.cbbPhongBan.addItems(list(self.ROLE_MAPPING.keys()))
        
        # Khóa không cho chọn lệch Chức vụ so với Phòng ban
        self.cbbChucVu.setEnabled(False) 
        self._on_department_changed(self.cbbPhongBan.currentText())

    def _on_department_changed(self, dept_name):
        """Tự động đồng bộ Chức vụ tương ứng khi Phòng ban thay đổi"""
        if dept_name in self.ROLE_MAPPING:
            target_position = self.ROLE_MAPPING[dept_name]["position"]
            self.cbbChucVu.clear()
            self.cbbChucVu.addItem(target_position)

    def _fill_next_employee_id(self):
        db = Database()
        try:
            cursor = db.execute("SELECT MAX(EmployeeID) FROM Employee")
            row = cursor.fetchone()
            next_id = (row[0] if row and row[0] is not None else 0) + 1
            self.txtMaNV.setText(str(next_id))
        except Exception as exc:
            print(f"Không thể lấy mã nhân viên tiếp theo: {exc}")
        finally:
            db.close()

    def _fill_form(self):
        if not self.employee:
            return
        
        self.txtMaNV.setText(str(self.employee[0]))
        self.txtHoTenNV.setText(str(self.employee[1] or ""))
        
        gender = str(self.employee[2] or "Nam")
        if gender == "Nam":
            self.rbNam.setChecked(True)
        else:
            self.rbNu.setChecked(True)

        if self.employee[3]:
            dob = self.employee[3]
            self.lblNgaySinhNV.setDate(QtCore.QDate(dob.year, dob.month, dob.day))

        self.txtSDT_NV.setText(str(self.employee[4] or ""))
        self.txtEmail_NV.setText(str(self.employee[5] or ""))
        
        if len(self.employee) > 6 and self.employee[6]:
            self.cbbPhongBan.setCurrentText(str(self.employee[6]))
            self._on_department_changed(str(self.employee[6]))
            
        if len(self.employee) > 8 and self.employee[8]:
            hd = self.employee[8]
            self.txtNgayTuyenDung.setDate(QtCore.QDate(hd.year, hd.month, hd.day))

    def _save_employee(self):
        ma_nv = self.txtMaNV.text().strip()
        ten_nv = self.txtHoTenNV.text().strip()
        gioi_tinh = "Nam" if self.rbNam.isChecked() else "Nữ"
        ngay_sinh = self.lblNgaySinhNV.date().toString("yyyy-MM-dd")
        sdt = self.txtSDT_NV.text().strip()
        email = self.txtEmail_NV.text().strip()
        phong_ban = self.cbbPhongBan.currentText()
        chuc_vu = self.cbbChucVu.currentText()
        ngay_tuyen_dung = self.txtNgayTuyenDung.date().toString("yyyy-MM-dd")

        if not ten_nv:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng nhập tên nhân viên!")
            return

        db = Database()
        try:
            if self.employee:
                # Chỉ UPDATE bảng Employee
                query = """
                    UPDATE Employee 
                    SET EmpName=?, EmpGender=?, EmpDateOfBirth=?, EmpPhone=?, EmpEmail=?, Department=?, Position=?, HireDate=?
                    WHERE EmployeeID=?
                """
                db.execute(query, (ten_nv, gioi_tinh, ngay_sinh, sdt, email, phong_ban, chuc_vu, ngay_tuyen_dung, ma_nv))
            else:
                # Chỉ INSERT vào bảng Employee (Đã bỏ phần tạo Account tự động)
                query = """
                    INSERT INTO Employee (EmployeeID, EmpName, EmpGender, EmpDateOfBirth, EmpPhone, EmpEmail, Department, Position, HireDate) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                db.execute(query, (ma_nv, ten_nv, gioi_tinh, ngay_sinh, sdt, email, phong_ban, chuc_vu, ngay_tuyen_dung))
            
            db.commit()
            QMessageBox.information(self, "Thành công", "Đã lưu thông tin nhân viên thành công!")
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi cơ sở dữ liệu", f"Đã xảy ra lỗi khi lưu thông tin:\n{exc}")
        finally:
            db.close()


# =====================================================================
# 2. CLASS CHI TIẾT NHÂN VIÊN (DIALOG)
# =====================================================================
class EmployeeDetailDialog(QDialog, Ui_EmployeeDetailDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent)
        self.setupUi(self)
        self.employee = employee
        
        # Tạo cấu trúc model cho bảng tblHoatDongNV (Ví dụ gồm 3 cột)
        self.activity_model = QStandardItemModel()
        self.activity_model.setHorizontalHeaderLabels(["Thời gian", "Hành động", "Chi tiết"])
        self.tblHoatDongNV.setModel(self.activity_model)
        
        self._fill_data()
        self._load_activities()  # Gọi nạp hoạt động của nhân viên
        
        self.btnDongNV.clicked.connect(self.accept)
        self.btnCapNhatNV.setVisible(False)
        self.btnXoaNV.setVisible(False)

    def _fill_data(self):
        if not self.employee: return
        self.txtMaNV.setText(str(self.employee[0]))
        self.txtHoTenNV.setText(str(self.employee[1] or ""))
        self.txtGioiTinhNV.setText(str(self.employee[2] or ""))
        
        if self.employee[3]:
            dob = self.employee[3]
            self.txtNgaySinhNV.setDate(QtCore.QDate(dob.year, dob.month, dob.day))
            
        self.txtSDT_NV.setText(str(self.employee[4] or ""))
        self.txtEmailNV.setText(str(self.employee[5] or ""))
        
        if len(self.employee) > 6: self.txtPhongBan.setText(str(self.employee[6] or ""))
        if len(self.employee) > 7: self.txtChucVu.setText(str(self.employee[7] or ""))
        if len(self.employee) > 8 and self.employee[8]:
            hd = self.employee[8]
            self.txtNgayTuyenDung.setDate(QtCore.QDate(hd.year, hd.month, hd.day))

    def _load_activities(self):
        """Truy vấn bảng lịch sử hoạt động dựa trên ID nhân viên hiện tại"""
        if not self.employee: return
        
        emp_id = self.employee[0]
        self.activity_model.setRowCount(0) # Làm sạch bảng trước khi nạp
        
        db = Database()
        try:
            # GIẢ ĐỊNH: Bạn có một bảng lưu vết tên là Order hoặc ActivityLog liên kết bằng EmployeeID
            # Ở đây mình giả định quét từ bảng [Order] xem nhân viên này đã xử lý những đơn hàng nào
            query = """
                SELECT OrderDate, N'Xử lý đơn hàng', N'Đơn hàng mã #' + CAST(OrderID AS NVARCHAR) + N' - Tổng tiền: ' + CAST(TotalAmount AS NVARCHAR)
                FROM [Order]
                WHERE EmployeeID = ?
                ORDER BY OrderDate DESC
            """
            
            # MẸO: Nếu sau này bạn tạo bảng log riêng (ví dụ: LogActivity), chỉ cần sửa lại câu SQL thành:
            # SELECT LogTime, ActionName, Description FROM LogActivity WHERE EmployeeID = ?
            
            cursor = db.execute(query, (emp_id,))
            rows = cursor.fetchall()
            
            for row_data in rows:
                row_items = []
                for field in row_data:
                    # Định dạng ngày tháng hiển thị cho đẹp nếu là đối tượng date/datetime
                    if isinstance(field, (date, QtCore.QDateTime)):
                        val_str = field.strftime("%d/%m/%Y %H:%M:%S") if hasattr(field, 'strftime') else str(field)
                    else:
                        val_str = str(field) if field is not None else ""
                        
                    item = QStandardItem(val_str)
                    item.setEditable(False) # Không cho sửa trực tiếp trên bảng chi tiết
                    row_items.append(item)
                    
                self.activity_model.appendRow(row_items)
                
            # Tự động co giãn kích thước cột cho vừa chữ
            self.tblHoatDongNV.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Không thể tải bảng hoạt động của nhân viên: {e}")
        finally:
            db.close()


# =====================================================================
# 3. CLASS CONTROLLER CHÍNH KẾT NỐI VỚI MAIN_WINDOW.UI
# =====================================================================
class EmployeePageController:
    def __init__(self, main_window):
        self.ui = main_window 
        self._connect_signals()
        self._load_data()

    def _connect_signals(self):
        self.ui.btnThemNV.clicked.connect(self._add_employee)
        self.ui.btnCapNhatNV.clicked.connect(self._edit_employee)
        self.ui.btnXoaNV.clicked.connect(self._delete_employee)
        self.ui.btnChiTietNV.clicked.connect(self._show_detail)
        self.ui.btnRefreshNV.clicked.connect(self._load_data)
        self.ui.btnTimKiemNV.clicked.connect(self._search_employee)

    def _load_data(self, search_query=None):
        self.ui.tblNhanVien.setRowCount(0)
        db = Database()
        try:
            base_query = "SELECT EmployeeID, EmpName, EmpPhone, Position, Department FROM Employee"
            if search_query:
                base_query += f" WHERE EmployeeID LIKE '%{search_query}%' OR EmpName LIKE N'%{search_query}%'"
                
            cursor = db.execute(base_query)
            rows = cursor.fetchall()
            
            for row_idx, row_data in enumerate(rows):
                self.ui.tblNhanVien.insertRow(row_idx)
                for col_idx in range(5):
                    val_str = str(row_data[col_idx]) if row_data[col_idx] is not None else ""
                    self.ui.tblNhanVien.setItem(row_idx, col_idx, QTableWidgetItem(val_str))
                self.ui.tblNhanVien.setItem(row_idx, 5, QTableWidgetItem("Đang làm"))
                
        except Exception as e:
            print(f"Lỗi tải danh sách nhân viên: {e}")
        finally:
            db.close()

    def _search_employee(self):
        query = self.ui.txtMaNV.text().strip()
        self._load_data(search_query=query)

    def _add_employee(self):
        dialog = EmployeeFormDialog(self.ui)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_data()

    def _get_full_employee_data(self, emp_id):
        db = Database()
        try:
            query = "SELECT EmployeeID, EmpName, EmpGender, EmpDateOfBirth, EmpPhone, EmpEmail, Department, Position, HireDate FROM Employee WHERE EmployeeID = ?"
            cursor = db.execute(query, (emp_id,))
            return cursor.fetchone()
        except Exception as e:
            QMessageBox.critical(self.ui, "Lỗi", f"Không thể lấy thông tin nhân viên: {e}")
            return None
        finally:
            db.close()

    def _edit_employee(self):
        selected_row = self.ui.tblNhanVien.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng chọn một nhân viên từ bảng để sửa!")
            return
        
        emp_id = self.ui.tblNhanVien.item(selected_row, 0).text()
        employee_data = self._get_full_employee_data(emp_id)

        if employee_data:
            dialog = EmployeeFormDialog(self.ui, employee=employee_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._load_data()

    def _show_detail(self):
        selected_row = self.ui.tblNhanVien.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng chọn một nhân viên để xem chi tiết!")
            return
            
        emp_id = self.ui.tblNhanVien.item(selected_row, 0).text()
        employee_data = self._get_full_employee_data(emp_id)
        
        if employee_data:
            dialog = EmployeeDetailDialog(self.ui, employee=employee_data)
            dialog.exec()

    def _delete_employee(self):
        selected_row = self.ui.tblNhanVien.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng chọn nhân viên cần xóa!")
            return
            
        emp_id = self.ui.tblNhanVien.item(selected_row, 0).text()
        emp_name = self.ui.tblNhanVien.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self.ui, "Xác nhận", 
            f"Bạn có chắc chắn muốn xóa nhân viên '{emp_name}' (Mã: {emp_id}) khỏi hệ thống không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            db = Database()
            try:
                # Đã loại bỏ dòng DELETE FROM Account cũ
                db.execute("DELETE FROM Employee WHERE EmployeeID = ?", (emp_id,))
                db.commit()
                QMessageBox.information(self.ui, "Thành công", "Đã xóa nhân viên thành công!")
                self._load_data()
            except Exception as e:
                QMessageBox.critical(self.ui, "Lỗi", f"Không thể xóa nhân viên: {e}")
            finally:
                db.close()