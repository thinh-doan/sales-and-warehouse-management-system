import os
from datetime import datetime

import pyodbc
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QMessageBox


class ReportPageController:
    def __init__(self, window):
        self.window = window
        self.conn = None
        self._connect_signals()
        self._init_defaults()

    def _connect_signals(self):
        self.window.btnXemBaoCao.clicked.connect(self.load_report)
        self.window.btnRefreshBC.clicked.connect(self.refresh_report)

    def _init_defaults(self):
        self.window.cbbLoaiBaoCao.setCurrentIndex(0)
        self.window.txtTuNgayBC.setDate(datetime.today().replace(day=1))
        self.window.txtDenNgayBC.setDate(datetime.today())

    def refresh_report(self):
        self._init_defaults()
        self.load_report()

    def connect_db(self):
        server = os.getenv("SQL_SERVER", "localhost")
        database = os.getenv("SQL_DATABASE", "QL_BANHANG_KHOHANG")
        user = os.getenv("SQL_UID", "")
        password = os.getenv("SQL_PWD", "")

        if user and password:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={user};"
                f"PWD={password}"
            )
        else:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                "Trusted_Connection=yes;"
            )

        self.conn = pyodbc.connect(conn_str)
        return self.conn

    def close_db(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def load_report(self):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()

            report_type = self._normalize_report_type(self.window.cbbLoaiBaoCao.currentText())
            start_date = self.window.txtTuNgayBC.date().toPyDate()
            end_date = self.window.txtDenNgayBC.date().toPyDate()

            if report_type == "Doanh thu":
                sql = """
                    SELECT CAST(OrderDate AS DATE) AS Ngay,
                           COUNT(OrderID) AS SoDon,
                           SUM(TotalAmount) AS DoanhThu
                    FROM [Order]
                    WHERE CAST(OrderDate AS DATE) BETWEEN ? AND ?
                    GROUP BY CAST(OrderDate AS DATE)
                    ORDER BY Ngay
                """
                cursor.execute(sql, start_date, end_date)
                # truyền chuỗi câu lệnh SQL vào làm tham số
                rows = cursor.fetchall()
                # lấy kết quả trả về
                headers = ["Ngày", "Số Đơn", "Doanh Thu"]

            elif report_type == "Đơn hàng":
                sql = """
                    SELECT o.OrderID,
                           c.CusName,
                           e.EmpName,
                           o.TotalAmount,
                           o.OrderStatus
                    FROM [Order] o
                    JOIN Customer c ON o.CustomerID = c.CustomerID
                    JOIN Employee e ON o.EmployeeID = e.EmployeeID
                    WHERE CAST(o.OrderDate AS DATE) BETWEEN ? AND ?
                    ORDER BY o.OrderID
                """
                cursor.execute(sql, start_date, end_date)
                rows = cursor.fetchall()
                headers = ["Mã đơn", "Khách hàng", "Nhân viên", "Tổng tiền", "Trạng thái"]

            elif report_type == "Thanh toán":
                sql = """
                    SELECT o.OrderID,
                           c.CusName,
                           e.EmpName,
                           p.Amount,
                           p.PaymentStatus
                    FROM Payment p
                    JOIN [Order] o ON p.OrderID = o.OrderID
                    JOIN Customer c ON o.CustomerID = c.CustomerID
                    JOIN Employee e ON o.EmployeeID = e.EmployeeID
                    WHERE CAST(o.OrderDate AS DATE) BETWEEN ? AND ?
                    ORDER BY o.OrderID
                """
                cursor.execute(sql, start_date, end_date)
                rows = cursor.fetchall()
                headers = ["Mã đơn", "Khách hàng", "Nhân viên", "Tổng tiền", "Trạng thái"]

            elif report_type == "Sản phẩm":
                sql = """
                    SELECT p.ProductID,
                           p.ProductName,
                           c.CategoryName,
                           p.ProductUnitPrice,
                           ISNULL(SUM(i.QuantityInStock), 0) AS QuantityInStock,
                           p.ProductStatus
                    FROM Product p
                    LEFT JOIN Inventory i ON p.ProductID = i.ProductID
                    LEFT JOIN Category c ON p.CategoryID = c.CategoryID
                    GROUP BY p.ProductID, p.ProductName, c.CategoryName, p.ProductUnitPrice, p.ProductStatus
                    ORDER BY p.ProductID
                """
                cursor.execute(sql)
                rows = cursor.fetchall()
                headers = ["Mã SP", "Tên sản phẩm", "Danh mục", "Đơn giá", "Tồn kho", "Trạng thái"]

            elif report_type == "Giao hàng":
                sql = """
                    SELECT s.ShipmentID,
                           s.OrderID,
                           d.PrtName,
                           s.ShipmentDate,
                           s.ShipmentStatus
                    FROM Shipment s
                    JOIN Delivery_Partner d ON s.PartnerID = d.PartnerID
                    WHERE CAST(s.ShipmentDate AS DATE) BETWEEN ? AND ?
                    ORDER BY s.ShipmentID
                """
                cursor.execute(sql, start_date, end_date)
                rows = cursor.fetchall()
                headers = ["Mã Giao Hàng", "Mã Đơn hàng", "Đối tác", "Ngày giao", "Trạng thái"]

            elif report_type == "Khách hàng":
                sql = """
                    SELECT c.CustomerID,
                           c.CusName,
                           c.CusPhone,
                           COUNT(DISTINCT o.OrderID) AS TongDon,
                           SUM(o.TotalAmount) AS TongChiTieu
                    FROM Customer c
                    LEFT JOIN [Order] o ON c.CustomerID = o.CustomerID
                    GROUP BY c.CustomerID, c.CusName, c.CusPhone
                    ORDER BY c.CustomerID
                """
                cursor.execute(sql)
                rows = cursor.fetchall()
                headers = ["Mã KH", "Họ tên", "SĐT", "Tổng đơn", "Tổng chi tiêu"]

            else:
                rows = []
                headers = []

            self._render_table(headers, rows)
            self._update_summary(report_type, rows)
            self.close_db()

        except Exception as exc:
            QMessageBox.critical(self.window, "Lỗi kết nối", f"Không thể tải dữ liệu báo cáo.\n{exc}")
            self.close_db()

    def _render_table(self, headers, rows):
        self.window.tblBaoCao.setColumnCount(len(headers))
        self.window.tblBaoCao.setHorizontalHeaderLabels(headers)
        self.window.tblBaoCao.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                item = QtWidgets.QTableWidgetItem(self._format_value(value))
                self.window.tblBaoCao.setItem(row_idx, col_idx, item)

        self.window.tblBaoCao.resizeColumnsToContents()
        self.window.tblBaoCao.setSortingEnabled(True)

    def _update_summary(self, report_type, rows):
        self.window.lblTongBanGhi.setText(str(len(rows)))

        money_index = None
        if report_type == "Doanh thu":
            money_index = 2
        elif report_type in {"Đơn hàng", "Thanh toán"}:
            money_index = 3
        elif report_type == "Khách hàng":
            money_index = 4
        elif report_type == "Sản phẩm":
            money_index = 3

        total_amount = 0.0
        if money_index is not None:
            for row in rows:
                try:
                    total_amount += float(row[money_index])
                except (TypeError, ValueError):
                    pass

        self.window.lblTongGiaTri.setText(self._format_currency(total_amount))

        completed = 0
        failed = 0
        if report_type == "Đơn hàng":
            completed = self._count_rows_by_value(rows, 4, "Hoàn thành")
            failed = self._count_rows_by_value(rows, 4, "Đã hủy")
            self.window.lblThatBai.setText(str(failed))
        elif report_type == "Thanh toán":
            completed = self._count_rows_by_value(rows, 4, "Đã thanh toán")
            self.window.lblThatBai.setText("")
        elif report_type == "Giao hàng":
            completed = self._count_rows_by_value(rows, 4, "Giao thành công")
            failed = self._count_rows_by_value(rows, 4, "Giao thất bại")
            self.window.lblThatBai.setText(str(failed))
        else:
            for row in rows:
                for value in row:
                    if isinstance(value, str):
                        text = value.lower()
                        if "hoàn thành" in text:
                            completed += 1
                        if "thất bại" in text:
                            failed += 1
            self.window.lblThatBai.setText(str(failed))

        self.window.lblHoanThanh.setText(str(completed))

    def _count_rows_by_value(self, rows, column_index, target_value):
        return sum(1 for row in rows if len(row) > column_index and row[column_index] == target_value)

    def _format_value(self, value):
        if value is None:
            return ""
        if isinstance(value, (int, float)):
            return str(value)
        return str(value)

    def _format_currency(self, value):
        return f"{value:,.0f} VNĐ"

    def _normalize_report_type(self, text):
        text = (text or "").strip().lower()
        mapping = {
            "doanh thu": "Doanh thu",
            "đơn hàng": "Đơn hàng",
            "don hang": "Đơn hàng",
            "thanh toán": "Thanh toán",
            "thanh toan": "Thanh toán",
            "giao hàng": "Giao hàng",
            "sản phẩm": "Sản phẩm",
            "san pham": "Sản phẩm",
            "kho": "Sản phẩm",
            "khách hàng": "Khách hàng",
            "khach hang": "Khách hàng",
        }
        return mapping.get(text, text)