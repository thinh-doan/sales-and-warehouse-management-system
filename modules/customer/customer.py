import pyodbc
from datetime import date, datetime
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QAbstractItemView

from connect import Database
# Import các class giao diện được biên dịch từ file .ui của bạn
from modules.customer.customer_add_ui import Ui_hopThoaiKhachHang
from modules.customer.customer_detail_ui import Ui_khungKhachHang


class CustomerFormDialog(QDialog, Ui_hopThoaiKhachHang):
    """Màn hình Thêm / Cập nhật Khách Hàng (customer_add_ui.py)"""

    def __init__(self, parent=None, customer_id=None, is_edit_mode=False):
        super().__init__(parent)
        self.setupUi(self)
        self.customer_id = customer_id
        self.is_edit_mode = is_edit_mode

        if self.is_edit_mode:
            self.setWindowTitle("Cập nhật khách hàng")
        else:
            self.setWindowTitle("Thêm khách hàng mới")

        self._prepare_form()
        self._connect_signals()

        # Nếu là chế độ chỉnh sửa, nạp dữ liệu khách hàng vào form
        if self.is_edit_mode and self.customer_id is not None:
            try:
                self._load_for_edit(self.customer_id)
            except Exception:
                pass

    def _prepare_form(self):
        # Mặc định chọn Khách cá nhân khi mới mở giao diện
        if hasattr(self, 'rdCaNhan'):
            self.rdCaNhan.setChecked(True)
            self._toggle_group_boxes()

        if hasattr(self, 'txtNgaySinh'):
            self.txtNgaySinh.setDate(QtCore.QDate.currentDate())

    def _connect_signals(self):
        # Bắt sự kiện thay đổi loại khách hàng để làm mờ khung tương ứng
        if hasattr(self, 'rdCaNhan'):
            self.rdCaNhan.toggled.connect(self._toggle_group_boxes)
        if hasattr(self, 'rdDoanhNghiep'):
            self.rdDoanhNghiep.toggled.connect(self._toggle_group_boxes)

        # Kết nối nút Lưu và Hủy (hỗ trợ cả trường hợp có hoặc không có hậu tố KH)
        for btn_name in ['btnLuu', 'btnLuuKH']:
            if hasattr(self, btn_name):
                getattr(self, btn_name).clicked.connect(self._save_customer)

        for btn_name in ['btnHuy', 'btnHuyKH']:
            if hasattr(self, btn_name):
                getattr(self, btn_name).clicked.connect(self.reject)

    def _toggle_group_boxes(self):
        """Xử lý làm mờ khung thông tin theo loại khách hàng được chọn"""
        is_ca_nhan = self.rdCaNhan.isChecked() if hasattr(self, 'rdCaNhan') else True

        if hasattr(self, 'nhomCaNhan'):
            self.nhomCaNhan.setEnabled(is_ca_nhan)
        if hasattr(self, 'nhomDoanhNghiep'):
            self.nhomDoanhNghiep.setEnabled(not is_ca_nhan)

    def _save_customer(self):
        # 1. Lấy thông tin chung
        name = self.txtTenKH.text().strip() if hasattr(self, 'txtTenKH') else ""
        phone = self.txtSDT_KH.text().strip() if hasattr(self, 'txtSDT_KH') else ""
        email = self.txtEmailKH.text().strip() if hasattr(self, 'txtEmailKH') else ""
        address = self.txtDiaChiKH.text().strip() if hasattr(self, 'txtDiaChiKH') else ""

        if not name or not phone or not address:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ Tên, Số điện thoại và Địa chỉ khách hàng!")
            return

        is_ca_nhan = self.rdCaNhan.isChecked() if hasattr(self, 'rdCaNhan') else True
        cus_type = "Cá nhân" if is_ca_nhan else "Doanh nghiệp"
        created_date = date.today()

        db = Database()
        try:
            # Tự động lấy Mã số khách hàng tiếp theo (STT tự tăng trong hệ thống)
            if not self.is_edit_mode:
                cursor = db.execute("SELECT ISNULL(MAX(CustomerID), 0) + 1 FROM Customer")
                next_id = cursor.fetchone()[0]

                # 2. Lưu vào bảng Customer gốc
                query_cust = """INSERT INTO Customer (CustomerID, CusName, CusPhone, CusEmail, CusAddress, CusCreatedDate, CusType) 
                                VALUES (?, ?, ?, ?, ?, ?, ?)"""
                db.execute(query_cust, (next_id, name, phone, email if email else None, address, created_date, cus_type))

                # 3. Lưu vào bảng phụ tương ứng theo cấu trúc Đa hình Database của bạn
                if is_ca_nhan:
                    gender = "Nam"
                    if hasattr(self, 'rdNu') and self.rdNu.isChecked():
                        gender = "Nữ"

                    q_date = self.txtNgaySinh.date() if hasattr(self, 'txtNgaySinh') else QtCore.QDate.currentDate()
                    dob = date(q_date.year(), q_date.month(), q_date.day())

                    query_sub = "INSERT INTO Individual_Customer (ICustomerID, Gender, CusDateOfBirth) VALUES (?, ?, ?)"
                    db.execute(query_sub, (next_id, gender, dob))
                else:
                    tax_code = self.txtMaSoThue.text().strip() if hasattr(self, 'txtMaSoThue') else ""
                    if not tax_code:
                        QMessageBox.warning(self, "Thông báo", "Vui lòng nhập Mã số thuế cho doanh nghiệp!")
                        db.close()
                        return
                    query_sub = "INSERT INTO Business_Customer (BCustomerID, TaxCode) VALUES (?, ?)"
                    db.execute(query_sub, (next_id, tax_code))
            else:
                # Update existing customer
                db.execute("UPDATE Customer SET CusName = ?, CusPhone = ?, CusEmail = ?, CusAddress = ? WHERE CustomerID = ?",
                           (name, phone, email if email else None, address, self.customer_id))

                # Update subtype
                cur_check = db.execute("SELECT CusType FROM Customer WHERE CustomerID = ?", (self.customer_id,))
                ctype = cur_check.fetchone()[0]
                if ctype == "Cá nhân":
                    gender = "Nam"
                    if hasattr(self, 'rdNu') and self.rdNu.isChecked():
                        gender = "Nữ"
                    q_date = self.txtNgaySinh.date() if hasattr(self, 'txtNgaySinh') else QtCore.QDate.currentDate()
                    dob = date(q_date.year(), q_date.month(), q_date.day())
                    db.execute("UPDATE Individual_Customer SET Gender = ?, CusDateOfBirth = ? WHERE ICustomerID = ?",
                               (gender, dob, self.customer_id))
                else:
                    tax_code = self.txtMaSoThue.text().strip() if hasattr(self, 'txtMaSoThue') else ""
                    db.execute("UPDATE Business_Customer SET TaxCode = ? WHERE BCustomerID = ?",
                               (tax_code, self.customer_id))

            db.commit()
            QMessageBox.information(self, "Thành công", "Lưu khách hàng thành công!")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu khách hàng.\nChi tiết: {e}")
        finally:
            db.close()

    def _load_for_edit(self, customer_id):
        """Nạp dữ liệu khách hàng vào form thêm để chỉnh sửa"""
        db = Database()
        try:
            query = """
                SELECT c.CustomerID, c.CusName, c.CusPhone, c.CusEmail, c.CusAddress, c.CusType,
                       i.Gender, i.CusDateOfBirth, b.TaxCode
                FROM Customer c
                LEFT JOIN Individual_Customer i ON c.CustomerID = i.ICustomerID
                LEFT JOIN Business_Customer b ON c.CustomerID = b.BCustomerID
                WHERE c.CustomerID = ?
            """
            cur = db.execute(query, (customer_id,))
            row = cur.fetchone()
            if not row:
                return

            # Set common fields
            if hasattr(self, 'txtTenKH'): self.txtTenKH.setText(str(row[1]))
            if hasattr(self, 'txtSDT_KH'): self.txtSDT_KH.setText(str(row[2]))
            if hasattr(self, 'txtEmailKH'): self.txtEmailKH.setText(str(row[3]) if row[3] else "")
            if hasattr(self, 'txtDiaChiKH'):
                # txtDiaChiKH is QLineEdit in add UI
                self.txtDiaChiKH.setText(str(row[4]) if row[4] else "")

            cus_type = row[5]
            if cus_type == "Cá nhân":
                if hasattr(self, 'rdCaNhan'): self.rdCaNhan.setChecked(True)
                gender = row[6]
                if gender == "Nam" and hasattr(self, 'rdNam'):
                    self.rdNam.setChecked(True)
                elif gender == "Nữ" and hasattr(self, 'rdNu'):
                    self.rdNu.setChecked(True)
                if row[7] and hasattr(self, 'txtNgaySinh'):
                    dob = row[7]
                    # txtNgaySinh is QDateEdit in add UI
                    try:
                        self.txtNgaySinh.setDate(QtCore.QDate(dob.year, dob.month, dob.day))
                    except Exception:
                        pass
                if hasattr(self, 'txtMaSoThue'): self.txtMaSoThue.setText("")
            else:
                if hasattr(self, 'rdDoanhNghiep'): self.rdDoanhNghiep.setChecked(True)
                if hasattr(self, 'txtMaSoThue'): self.txtMaSoThue.setText(str(row[8]) if row[8] else "")
                if hasattr(self, 'rdNam'): self.rdNam.setChecked(False)
                if hasattr(self, 'rdNu'): self.rdNu.setChecked(False)
        finally:
            db.close()


class CustomerDetailDialog(QDialog, Ui_khungKhachHang):
    """Màn hình Xem Chi Tiết & Cập Nhật Khách Hàng (customer_detail_ui.py)"""

    def __init__(self, parent=None, customer_id=None, is_editable=False):
        super().__init__(parent)
        self.setupUi(self)
        self.customer_id = customer_id
        self.is_editable = is_editable

        self._prepare_ui_mode()
        self._load_customer_data()
        self._connect_signals()
    def _prepare_ui_mode(self):
        """Phân bổ quyền chỉnh sửa dựa theo chế độ gọi (Xem chi tiết hay Cập nhật)"""
        if self.is_editable:
            self.setWindowTitle("Cập nhật thông tin khách hàng")
        else:
            self.setWindowTitle("Chi tiết khách hàng")

        # Khóa trường Mã khách hàng (Không cho phép sửa Khóa chính)
        if hasattr(self, 'txtMaKH'):
            self.txtMaKH.setEnabled(False)
        # Thiết lập trạng thái hoạt động của các ô nhập dữ liệu định danh
        fields = ['txtTenKH', 'txtSDT_KH', 'txtEmailKH', 'txtNgaySinh', 'rdNam', 'rdNu', 'txtMaSoThue']
        for field in fields:
            if hasattr(self, field):
                getattr(self, field).setEnabled(self.is_editable)

        # NOTE: Don't disable the tab widget or the tables here — they must remain interactive
        # so user can view order/payment/history/statistics even when dialog is in read-only mode.

    def _connect_signals(self):
        # Kết nối sự kiện nút cập nhật và xóa trong giao diện chi tiết
        if hasattr(self, 'btnCapNhatKH'):
            # Nếu đang ở chế độ chỉnh sửa trong dialog chi tiết, lưu trực tiếp
            if self.is_editable:
                self.btnCapNhatKH.clicked.connect(self._update_customer)
            else:
                # Ở chế độ chỉ xem: chuyển sang form chỉnh sửa (customer_add_ui) với dữ liệu hiện tại
                self.btnCapNhatKH.setEnabled(True)
                self.btnCapNhatKH.clicked.connect(self._open_edit_form_from_detail)

        if hasattr(self, 'btnXoaKh'):
            self.btnXoaKh.clicked.connect(self._delete_customer_from_detail)

        # Khi thay đổi tab Thống kê / Lịch sử, nạp dữ liệu tương ứng
        if hasattr(self, 'tblThongKe'):
            self.tblThongKe.currentChanged.connect(self._on_tab_changed)

    def _load_customer_data(self):
        """Truy vấn nạp dữ liệu chi tiết, thống kê chỉ số, lịch sử mua hàng và thanh toán từ SQL Server"""
        db = Database()
        ui = self  # Kế thừa cấu trúc trực tiếp 'self'
        try:
            # ==========================================
            # PHẦN 1: NẠP THÔNG TIN CƠ BẢN CỦA KHÁCH HÀNG
            # ==========================================
            query = """
                SELECT c.CustomerID, c.CusName, c.CusPhone, c.CusEmail, c.CusAddress, c.CusType,
                       i.Gender, i.CusDateOfBirth, b.TaxCode
                FROM Customer c
                LEFT JOIN Individual_Customer i ON c.CustomerID = i.ICustomerID
                LEFT JOIN Business_Customer b ON c.CustomerID = b.BCustomerID
                WHERE c.CustomerID = ?
            """
            cursor = db.execute(query, (self.customer_id,))
            row = cursor.fetchone()
            if row:
                if hasattr(ui, 'txtMaKH'): ui.txtMaKH.setText(str(row[0]))
                if hasattr(ui, 'txtTenKH'): ui.txtTenKH.setText(str(row[1]))
                if hasattr(ui, 'txtSDT_KH'): ui.txtSDT_KH.setText(str(row[2]))
                if hasattr(ui, 'txtEmailKH'): ui.txtEmailKH.setText(str(row[3]) if row[3] else "")

                cus_type = row[5]
                if cus_type == "Cá nhân":
                    gender = row[6]
                    if gender == "Nam" and hasattr(ui, 'rdNam'):
                        ui.rdNam.setChecked(True)
                    elif gender == "Nữ" and hasattr(ui, 'rdNu'):
                        ui.rdNu.setChecked(True)

                    # ĐÃ SỬA LỖI: Vì txtNgaySinh là QLineEdit, phải dùng .setText() thay vì .setDate()
                    if row[7] and hasattr(ui, 'txtNgaySinh'):
                        dob = row[7]
                        ui.txtNgaySinh.setText(dob.strftime("%d/%m/%Y"))

                    if hasattr(ui, 'txtMaSoThue'): ui.txtMaSoThue.setEnabled(False)
                else:
                    if hasattr(ui, 'txtMaSoThue'): ui.txtMaSoThue.setText(str(row[8]) if row[8] else "")
                    if hasattr(ui, 'txtNgaySinh'): ui.txtNgaySinh.setEnabled(False)
                    if hasattr(ui, 'rdNam'): ui.rdNam.setEnabled(False)
                    if hasattr(ui, 'rdNu'): ui.rdNu.setEnabled(False)

            # ==========================================
            # PHẦN 2: TỔNG HỢP SỐ LIỆU THỐNG KÊ (KPI LABELS)
            # ==========================================
            query_stats = """
                SELECT COUNT(OrderID), ISNULL(SUM(TotalAmount), 0)
                FROM [Order] WHERE CustomerID = ?
            """
            cursor_stats = db.execute(query_stats, (self.customer_id,))
            row_stats = cursor_stats.fetchone()

            query_latest = """
                SELECT TOP 1 OrderDate FROM [Order] 
                WHERE CustomerID = ? ORDER BY OrderDate DESC, OrderID DESC
            """
            cursor_latest = db.execute(query_latest, (self.customer_id,))
            row_latest = cursor_latest.fetchone()

            if row_stats:
                total_orders = row_stats[0]
                total_amount = row_stats[1]
                latest_date = row_latest[0].strftime("%d/%m/%Y") if row_latest and row_latest[0] else "Chưa có đơn"

                if hasattr(ui, 'labelTotalOrders_4'): ui.labelTotalOrders_4.setText(str(total_orders))
                if hasattr(ui, 'lblTotalOrdersValue'): ui.lblTotalOrdersValue.setText(f"{total_amount:,.0f} VNĐ")
                if hasattr(ui, 'labelTotalOrders_3'): ui.labelTotalOrders_3.setText(latest_date)

            # Nạp các bảng lịch sử / thống kê mặc định (nếu có)
            try:
                # Gọi các bộ nạp dữ liệu chuyên trách (nếu tồn tại)
                if hasattr(self, 'load_order_history'):
                    self.load_order_history()
                if hasattr(self, 'load_payment_history'):
                    self.load_payment_history()
                if hasattr(self, 'load_statistics'):
                    self.load_statistics()
            except Exception:
                # Nếu có lỗi ở đây, bỏ qua để không chặn hiển thị dialog
                pass

            # ==========================================
            # PHẦN 4: ĐỔ DỮ LIỆU BẢNG LỊCH SỬ THANH TOÁN
            # ==========================================
            if hasattr(ui, 'bangThanhToanLichSu'):
                ui.bangThanhToanLichSu.setRowCount(0)
                query_payments = """
                    SELECT p.PaymentID, p.PaymentDate, p.PaymentMethod, p.Amount
                    FROM Payment p
                    JOIN [Order] o ON p.OrderID = o.OrderID
                    WHERE o.CustomerID = ?
                    ORDER BY p.PaymentDate DESC, p.PaymentID DESC
                """
                cursor_payments = db.execute(query_payments, (self.customer_id,))
                rows_payments = cursor_payments.fetchall()

                ui.bangThanhToanLichSu.setRowCount(len(rows_payments))
                for row_idx, row_data in enumerate(rows_payments):
                    p_id = str(row_data[0])
                    p_date = row_data[1].strftime("%d/%m/%Y") if row_data[1] else "N/A"
                    p_method = str(row_data[2])
                    p_amount = f"{row_data[3]:,.0f} VNĐ"

                    ui.bangThanhToanLichSu.setItem(row_idx, 0, QTableWidgetItem(p_id))
                    ui.bangThanhToanLichSu.setItem(row_idx, 1, QTableWidgetItem(p_date))
                    ui.bangThanhToanLichSu.setItem(row_idx, 2, QTableWidgetItem(p_method))
                    ui.bangThanhToanLichSu.setItem(row_idx, 3, QTableWidgetItem(p_amount))

        except Exception as e:
            print(f"Lỗi tải chi tiết khách hàng: {e}")
        finally:
            db.close()
    def _update_customer(self):
        """Xử lý cập nhật thông tin đã chỉnh sửa vào Database"""
        name = self.txtTenKH.text().strip() if hasattr(self, 'txtTenKH') else ""
        phone = self.txtSDT_KH.text().strip() if hasattr(self, 'txtSDT_KH') else ""
        email = self.txtEmailKH.text().strip() if hasattr(self, 'txtEmailKH') else ""
        address = self.txtDiaChiKH.toPlainText().strip() if hasattr(self, 'txtDiaChiKH') else ""

        if not name or not phone:
            QMessageBox.warning(self, "Thông báo", "Tên và Số điện thoại khách hàng không được để trống!")
            return

        db = Database()
        try:
            # 1. Cập nhật bảng Customer chung (bao gồm địa chỉ)
            query_cust = "UPDATE Customer SET CusName = ?, CusPhone = ?, CusEmail = ?, CusAddress = ? WHERE CustomerID = ?"
            db.execute(query_cust, (name, phone, email if email else None, address, self.customer_id))

            # 2. Xác định kiểu khách để cập nhật bảng con đặc thù
            cur_check = db.execute("SELECT CusType FROM Customer WHERE CustomerID = ?", (self.customer_id,))
            cus_type = cur_check.fetchone()[0]

            if cus_type == "Cá nhân":
                gender = "Nam"
                if hasattr(self, 'rdNu') and self.rdNu.isChecked():
                    gender = "Nữ"

                # txtNgaySinh is a QLineEdit in this UI; parse its text as dd/mm/YYYY
                dob = None
                if hasattr(self, 'txtNgaySinh'):
                    raw = self.txtNgaySinh.text().strip()
                    if raw:
                        try:
                            dob = datetime.strptime(raw, "%d/%m/%Y").date()
                        except Exception:
                            QMessageBox.warning(self, "Thông báo", "Định dạng Ngày sinh không hợp lệ. Vui lòng dùng dd/mm/YYYY.")
                            db.close()
                            return

                db.execute("UPDATE Individual_Customer SET Gender = ?, CusDateOfBirth = ? WHERE ICustomerID = ?",
                           (gender, dob, self.customer_id))
            else:
                tax_code = self.txtMaSoThue.text().strip() if hasattr(self, 'txtMaSoThue') else ""
                db.execute("UPDATE Business_Customer SET TaxCode = ? WHERE BCustomerID = ?",
                           (tax_code, self.customer_id))

            db.commit()
            QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin khách hàng thành công!")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật dữ liệu.\nChi tiết: {e}")
        finally:
            db.close()

    def _delete_customer_from_detail(self):
        """Hỗ trợ xóa trực tiếp khách hàng ngay từ giao diện xem chi tiết"""
        ans = QMessageBox.question(
            self, "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa khách hàng này không?\nDữ liệu định danh sẽ bị xóa hoàn toàn khỏi hệ thống.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ans == QMessageBox.StandardButton.Yes:
            db = Database()
            try:
                # Xóa dữ liệu ở bảng con phụ thuộc trước nhằm tránh xung đột khóa ngoại (Foreign Key Constraint)
                db.execute("DELETE FROM Individual_Customer WHERE ICustomerID = ?", (self.customer_id,))
                db.execute("DELETE FROM Business_Customer WHERE BCustomerID = ?", (self.customer_id,))
                db.execute("DELETE FROM Customer WHERE CustomerID = ?", (self.customer_id,))
                db.commit()
                QMessageBox.information(self, "Thành công", "Đã xóa khách hàng thành công!")
                self.accept()
            except pyodbc.Error:
                db.rollback()
                QMessageBox.critical(self, "Lỗi",
                                     "Không thể xóa khách hàng này do tài khoản đã phát sinh giao dịch/hóa đơn trong hệ thống!")
            finally:
                db.close()

    def _open_edit_form_from_detail(self):
        """Mở form Thêm (chế độ sửa) với dữ liệu của khách hàng hiện tại"""
        if not self.customer_id:
            return
        dialog = CustomerFormDialog(self, customer_id=self.customer_id, is_edit_mode=True)
        if dialog.exec():
            # Reload detail and child tables
            try:
                self._load_customer_data()
            except Exception:
                pass

    def _on_tab_changed(self, index):
        # Tab indexes in the UI: 0 = Lịch Sử Mua Hàng, 1 = Lịch Sử Thanh Toán, 2 = Thống Kê
        try:
            if index == 0:
                self.load_order_history()
            elif index == 1:
                self.load_payment_history()
            elif index == 2:
                self.load_statistics()
        except Exception:
            pass

    def load_order_history(self):
        """Nạp dữ liệu lịch sử mua hàng: gộp danh sách sản phẩm ở giữa Ngày tạo và Thanh toán"""
        if not hasattr(self, 'tblLichSuMuahang'):
            return

        db = Database()
        try:
            self.tblLichSuMuahang.setRowCount(0)
            query_orders = """
                SELECT 
                    o.OrderID, 
                    o.OrderDate, 
                    STRING_AGG(p.ProductName, ', ') AS ProductList,
                    o.TotalAmount, 
                    o.OrderStatus 
                FROM [Order] o
                LEFT JOIN Order_Detail od ON o.OrderID = od.OrderID
                LEFT JOIN Product p ON od.ProductID = p.ProductID
                WHERE o.CustomerID = ?
                GROUP BY o.OrderID, o.OrderDate, o.TotalAmount, o.OrderStatus
                ORDER BY o.OrderDate DESC, o.OrderID DESC
            """
            cursor = db.execute(query_orders, (self.customer_id,))
            rows = cursor.fetchall()

            self.tblLichSuMuahang.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                order_id = str(row_data[0])
                order_date = row_data[1].strftime("%d/%m/%Y") if row_data[1] else "N/A"
                product_list = str(row_data[2]) if row_data[2] else "Không có sản phẩm"
                total_amount = f"{row_data[3]:,.0f} VNĐ"
                status = str(row_data[4])

                self.tblLichSuMuahang.setItem(row_idx, 0, QTableWidgetItem(order_id))
                self.tblLichSuMuahang.setItem(row_idx, 1, QTableWidgetItem(order_date))
                self.tblLichSuMuahang.setItem(row_idx, 2, QTableWidgetItem(product_list))
                self.tblLichSuMuahang.setItem(row_idx, 3, QTableWidgetItem(total_amount))
                self.tblLichSuMuahang.setItem(row_idx, 4, QTableWidgetItem(status))
        except Exception as e:
            print(f"Lỗi nạp lịch sử đơn hàng: {e}")
        finally:
            db.close()

    def load_payment_history(self):
        """Nạp dữ liệu lịch sử các đợt giao dịch dòng tiền thanh toán"""
        if not hasattr(self, 'bangThanhToanLichSu'):
            return

        db = Database()
        try:
            self.bangThanhToanLichSu.setRowCount(0)
            query_payments = """
                SELECT p.PaymentID, p.PaymentDate, p.PaymentMethod, p.Amount
                FROM Payment p
                JOIN [Order] o ON p.OrderID = o.OrderID
                WHERE o.CustomerID = ?
                ORDER BY p.PaymentDate DESC, p.PaymentID DESC
            """
            cursor = db.execute(query_payments, (self.customer_id,))
            rows = cursor.fetchall()

            self.bangThanhToanLichSu.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                p_id = str(row_data[0])
                p_date = row_data[1].strftime("%d/%m/%Y") if row_data[1] else "N/A"
                p_method = str(row_data[2])
                p_amount = f"{row_data[3]:,.0f} VNĐ"

                self.bangThanhToanLichSu.setItem(row_idx, 0, QTableWidgetItem(p_id))
                self.bangThanhToanLichSu.setItem(row_idx, 1, QTableWidgetItem(p_date))
                self.bangThanhToanLichSu.setItem(row_idx, 2, QTableWidgetItem(p_method))
                self.bangThanhToanLichSu.setItem(row_idx, 3, QTableWidgetItem(p_amount))
        except Exception as e:
            print(f"Lỗi nạp lịch sử thanh toán: {e}")
        finally:
            db.close()

    def load_statistics(self):
        """Tính toán tổng hợp số liệu đưa vào các ô Thống kê tổng quan"""
        db = Database()
        try:
            query_stats = """
                SELECT 
                    COUNT(OrderID) AS TotalOrders,
                    ISNULL(SUM(TotalAmount), 0) AS TotalSpent,
                    MAX(OrderID) AS LatestOrder
                FROM [Order]
                WHERE CustomerID = ? AND OrderStatus <> N'Đã hủy'
            """
            cursor = db.execute(query_stats, (self.customer_id,))
            result = cursor.fetchone()

            if result:
                if hasattr(self, 'labelTotalOrders_4'):
                    self.labelTotalOrders_4.setText(str(result[0]))
                if hasattr(self, 'lblTotalOrdersValue'):
                    self.lblTotalOrdersValue.setText(f"{result[1]:,.0f} VNĐ")
                if hasattr(self, 'labelTotalOrders_3'):
                    self.labelTotalOrders_3.setText(str(result[2]) if result[2] else "Không có")
        except Exception as e:
            print(f"Lỗi xử lý số liệu thống kê: {e}")
        finally:
            db.close()



class CustomerPageController:
    """Bộ điều hướng trang Quản lý khách hàng chính hiển thị trên main_window_ui.py"""

    def __init__(self, window):
        self.window = window
        self._setup_table()
        self._connect_signals()
        self._toggle_action_buttons(False)  # Làm mờ 3 nút ban đầu khi chưa chọn dòng

    def _setup_table(self):
        table = self.window.tblKhachHang
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def _connect_signals(self):
        # Kết nối các nút chức năng chính trên trang quản lý khách hàng
        self.window.btnThemKH.clicked.connect(self.add_customer)
        self.window.btnChiTietKH.clicked.connect(self.view_customer_detail)
        self.window.btnCapNhatKH.clicked.connect(self.edit_customer)
        self.window.btnXoaKH.clicked.connect(self.delete_customer)
        self.window.btnRefreshKH.clicked.connect(self.load_customer_table)

        # Sự kiện khi người dùng gõ tìm kiếm mã số khách hàng tại txtTimKiemKH
        self.window.txtTimKiemKH.textChanged.connect(self.search_customer)

        # Theo dõi sự kiện click chuột chọn hàng để làm sáng/mờ các nút hành động
        self.window.tblKhachHang.itemSelectionChanged.connect(self._on_row_selection_changed)

    def _toggle_action_buttons(self, enabled):
        """Hàm bật / làm mờ 3 nút Chi tiết, Cập nhật, Xóa"""
        self.window.btnChiTietKH.setEnabled(enabled)
        self.window.btnCapNhatKH.setEnabled(enabled)
        self.window.btnXoaKH.setEnabled(enabled)

    def _on_row_selection_changed(self):
        selected_indexes = self.window.tblKhachHang.selectedIndexes()
        self._toggle_action_buttons(len(selected_indexes) > 0)

    def _get_selected_customer_id(self):
        table = self.window.tblKhachHang
        selected_indexes = table.selectedIndexes()
        if not selected_indexes:
            return None
        row = selected_indexes[0].row()
        # Lấy ID ẩn lưu trữ tại cột số 0
        return table.item(row, 0).data(QtCore.Qt.ItemDataRole.UserRole)

    def load_customer_table(self, search_id=None):
        """Tải dữ liệu từ database lên QTableWidget theo 4 cột nghiệp vụ yêu cầu"""
        table = self.window.tblKhachHang
        table.setRowCount(0)

        db = Database()
        try:
            if search_id:
                query = "SELECT CustomerID, CusName, CusType, CusPhone FROM Customer WHERE CAST(CustomerID AS VARCHAR) LIKE ?"
                cursor = db.execute(query, (f"%{search_id}%",))
            else:
                # SỬA TẠI ĐÂY: Đổi ORDER BY CustomerID DESC thành ORDER BY CustomerID ASC để đúng thứ tự xuôi
                query = "SELECT CustomerID, CusName, CusType, CusPhone FROM Customer ORDER BY CustomerID ASC"
                cursor = db.execute(query)

            rows = cursor.fetchall()
            for row_idx, row_data in enumerate(rows):
                table.insertRow(row_idx)
                for col_idx in range(4):
                    val = str(row_data[col_idx]) if row_data[col_idx] is not None else ""
                    item = QTableWidgetItem(val)
                    table.setItem(row_idx, col_idx, item)

                # Lưu ID gốc vào UserRole của ô đầu tiên để xử lý dòng chọn chuẩn xác
                table.item(row_idx, 0).setData(QtCore.Qt.ItemDataRole.UserRole, row_data[0])
        except Exception as e:
            print(f"Lỗi tải bảng dữ liệu khách hàng: {e}")
        finally:
            db.close()
            self._on_row_selection_changed()  # Reset lại trạng thái mờ/rõ của các nút bấm

    def search_customer(self):
        """Thực thi tìm kiếm tức thời khi người dùng nhập thông tin mã vào txtTimKiemKH"""
        search_text = self.window.txtTimKiemKH.text().strip()
        self.load_customer_table(search_id=search_text)

    def add_customer(self):
        dialog = CustomerFormDialog(self.window)
        if dialog.exec():
            self.load_customer_table()

    def view_customer_detail(self):
        customer_id = self._get_selected_customer_id()
        if customer_id:
            dialog = CustomerDetailDialog(self.window, customer_id=customer_id, is_editable=False)
            dialog.exec()
            self.load_customer_table()  # Tải lại nếu có thao tác xóa bên trong màn hình chi tiết

    def edit_customer(self):
        customer_id = self._get_selected_customer_id()
        if customer_id:
            dialog = CustomerFormDialog(self.window, customer_id=customer_id, is_edit_mode=True)
            if dialog.exec():
                self.load_customer_table()

    def delete_customer(self):
        customer_id = self._get_selected_customer_id()
        if not customer_id: return

        # Lấy tên khách hàng phục vụ thông báo xác nhận trực quan
        table = self.window.tblKhachHang
        row = table.selectedIndexes()[0].row()
        customer_name = table.item(row, 1).text()

        ans = QMessageBox.question(
            self.window, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa khách hàng: {customer_name} (Mã số: {customer_id}) không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ans != QMessageBox.StandardButton.Yes:
            return

        db = Database()
        try:
            # Xóa tuần tự bảng phụ -> bảng chính tuân thủ cấu trúc quan hệ khóa ngoại dữ liệu
            db.execute("DELETE FROM Individual_Customer WHERE ICustomerID = ?", (customer_id,))
            db.execute("DELETE FROM Business_Customer WHERE BCustomerID = ?", (customer_id,))
            db.execute("DELETE FROM Customer WHERE CustomerID = ?", (customer_id,))
            db.commit()

            QMessageBox.information(self.window, "Thành công", "Khách hàng đã được xóa hẳn khỏi hệ thống database.")
            self.load_customer_table()
        except pyodbc.Error:
            db.rollback()
            QMessageBox.critical(self.window, "Lỗi ràng buộc dữ liệu",
                                 "Không thể xóa khách hàng này do lịch sử giao dịch mua hàng đã tồn tại.")
        finally:
            db.close()
    

