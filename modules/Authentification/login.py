import hashlib
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialog, QMessageBox

from connect import Database
from modules.Authentification.login_ui import Ui_LoginDialog

class LoginDialog(QDialog, Ui_LoginDialog):
    """Dialog xử lý logic đăng nhập và xác thực"""
    
    login_successful = QtCore.pyqtSignal(dict)  # Signal khi đăng nhập thành công
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.user_info = None
        self._connect_signals()
        
        # Ẩn nút hỏi chấm (?) mặc định trên thanh tiêu đề của QDialog
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        
    def _connect_signals(self):
        """Kết nối tín hiệu nút bấm"""
        self.btnDangNhap.clicked.connect(self._handle_login)
        self.btnThoatDangNhap.clicked.connect(self.reject)
        self.txtTenDangNhap.returnPressed.connect(self._handle_login)
        self.txtPMatKhau.returnPressed.connect(self._handle_login)
    
    def _handle_login(self):
        """Xử lý sự kiện đăng nhập"""
        username = self.txtTenDangNhap.text().strip()
        password = self.txtPMatKhau.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập và mật khẩu")
            return
        
        user_info = self._authenticate_user(username, password)
        
        if user_info:
            self.user_info = user_info
            self.login_successful.emit(user_info)
            self.accept()  # Đóng dialog và trả về QDialog.DialogCode.Accepted
        else:
            QMessageBox.critical(self, "Lỗi đăng nhập", "Tên đăng nhập hoặc mật khẩu không chính xác")
            self.txtPMatKhau.clear()
            self.txtTenDangNhap.setFocus()
    
    def _authenticate_user(self, username: str, password: str) -> dict:
        """Xác thực người dùng từ database"""
        try:
            db = Database()
            query = """
            SELECT 
                a.AccountID, a.Username, a.PasswordHash, a.AccountStatus,
                a.EmployeeID, a.RoleID, e.EmpName, e.Department, e.Position, r.RoleName
            FROM Account a
            INNER JOIN Employee e ON a.EmployeeID = e.EmployeeID
            INNER JOIN Role r ON a.RoleID = r.RoleID
            WHERE a.Username = ?
            """
            cursor = db.execute(query, (username,))
            row = cursor.fetchone()
            db.close()
            
            if row is None:
                return None
            
            account_id, db_username, password_hash, status, emp_id, role_id, emp_name, department, position, role_name = row
            
            if status != "Đang hoạt động":
                QMessageBox.warning(self, "Cảnh báo", "Tài khoản của bạn đang bị khóa!")
                return None
            
            if not self._verify_password(password, password_hash):
                return None
            
            return {
                "account_id": account_id,
                "username": db_username,
                "employee_id": emp_id,
                "employee_name": emp_name,
                "department": department,
                "position": position,
                "role_id": role_id,
                "role_name": role_name,
                "status": status
            }
            
        except Exception as e:
            print(f"Lỗi xác thực database: {e}")
            return None
    

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Xác thực mật khẩu theo dữ liệu hiện có trong database."""
        if password_hash is None:
            return False

        password_hash = str(password_hash).strip()
        password = password.strip()
        sha256_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        demo_hash = f"hash_{password.lower()}_123"

        return password == password_hash or password_hash == sha256_hash or password_hash == demo_hash
    
    def get_user_info(self) -> dict:
        """Trả về thông tin user cho Main sử dụng nếu cần"""
        return self.user_info