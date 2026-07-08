from __future__ import annotations

import math
from datetime import datetime

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCharts import QBarCategoryAxis, QBarSeries, QBarSet, QChart, QPieSeries, QValueAxis
from PyQt6.QtCore import QMargins, Qt
from PyQt6.QtWidgets import QMessageBox

from connect import Database


class DashboardPageController:
    def __init__(self, window):
        self.window = window
        self.db: Database | None = None

        self._setup_visual_layout()
        self._connect_signals()
        self.load_dashboard_data()

    def _connect_signals(self):
        if hasattr(self.window, "btnRefreshDB"):
            self.window.btnRefreshDB.clicked.connect(self.refresh_dashboard)
        if hasattr(self.window, "btnTongQuan"):
            self.window.btnTongQuan.clicked.connect(self.show_dashboard_page)

    def _setup_visual_layout(self):
        if hasattr(self.window, "verticalLayout_11"):
            self.window.verticalLayout_11.setContentsMargins(8, 8, 8, 8)
            self.window.verticalLayout_11.setSpacing(6)

        if hasattr(self.window, "gridKPI"):
            self.window.gridKPI.setVerticalSpacing(4)
            self.window.gridKPI.setHorizontalSpacing(6)
        if hasattr(self.window, "gridKPI2"):
            self.window.gridKPI2.setVerticalSpacing(4)
            self.window.gridKPI2.setHorizontalSpacing(6)

        # Thu gọn KPI cards để nhường chỗ cho các bảng/chart phía dưới.
        kpi_frames = [
            "frmTotalOrder",
            "frmRevenue",
            "frmCustomer",
            "frmProduct",
            "frmShipment",
            "frmCompleted",
            "frmLowStock",
            "frmPartner",
        ]
        for frame_name in kpi_frames:
            if hasattr(self.window, frame_name):
                frame = getattr(self.window, frame_name)
                frame.setMinimumHeight(56)
                frame.setMaximumHeight(68)

        # Tăng vùng hiển thị chart và table cho dễ nhìn.
        if hasattr(self.window, "grpRevenueChart"):
            self.window.grpRevenueChart.setMinimumHeight(200)
            self.window.grpRevenueChart.setMaximumHeight(240)
        if hasattr(self.window, "chartDoanhThu"):
            self.window.chartDoanhThu.setMinimumHeight(160)

        if hasattr(self.window, "grpTopProduct"):
            self.window.grpTopProduct.setMinimumHeight(120)
            self.window.grpTopProduct.setMaximumHeight(160)
        if hasattr(self.window, "grpOrderStatus"):
            self.window.grpOrderStatus.setMinimumHeight(200)
            self.window.grpOrderStatus.setMaximumHeight(250)
        if hasattr(self.window, "chartTrangThaiGiaoHang"):
            self.window.chartTrangThaiGiaoHang.setMinimumHeight(170)

        if hasattr(self.window, "grpRecentOrder"):
            self.window.grpRecentOrder.setMinimumHeight(110)
            self.window.grpRecentOrder.setMaximumHeight(150)

        if hasattr(self.window, "btnRefreshDB"):
            self.window.btnRefreshDB.setMinimumSize(100, 30)
        if hasattr(self.window, "txtLastUpdate"):
            self.window.txtLastUpdate.setMinimumHeight(28)

        if hasattr(self.window, "horizontalLayoutStatistic"):
            self.window.horizontalLayoutStatistic.setStretch(0, 1)
            self.window.horizontalLayoutStatistic.setStretch(1, 2)

        if hasattr(self.window, "verticalLayout_11"):
            # Giữ toàn bộ dashboard trong 1 màn hình bằng cách phân bổ lại stretch.
            self.window.verticalLayout_11.setStretch(0, 0)
            self.window.verticalLayout_11.setStretch(1, 0)
            self.window.verticalLayout_11.setStretch(2, 0)
            self.window.verticalLayout_11.setStretch(3, 3)
            self.window.verticalLayout_11.setStretch(4, 3)
            self.window.verticalLayout_11.setStretch(5, 1)
            self.window.verticalLayout_11.setStretch(6, 0)

        if hasattr(self.window, "tblTopProduct"):
            self.window.tblTopProduct.verticalHeader().setVisible(False)
            self.window.tblTopProduct.horizontalHeader().setStretchLastSection(True)
            self.window.tblTopProduct.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )
        if hasattr(self.window, "tblRecentOrder"):
            self.window.tblRecentOrder.verticalHeader().setVisible(False)
            self.window.tblRecentOrder.horizontalHeader().setStretchLastSection(True)
            self.window.tblRecentOrder.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )

    def show_dashboard_page(self):
        if hasattr(self.window, "khungChuyenTrangStacked") and hasattr(self.window, "pageTongQuan"):
            self.window.khungChuyenTrangStacked.setCurrentWidget(self.window.pageTongQuan)
        self.load_dashboard_data()

    def refresh_dashboard(self):
        self.load_dashboard_data()

    def load_dashboard_data(self):
        try:
            self.db = Database()
            cursor = self.db.execute

            kpis = self._query_kpis(cursor)
            monthly_revenue = self._query_revenue_by_month(cursor)
            top_products = self._query_top_products(cursor)
            recent_rows = self._query_recent_product_rows(cursor)
            order_status = self._query_order_status(cursor)

            self._render_kpis(kpis)
            self._render_revenue_chart(monthly_revenue)
            self._render_top_products(top_products)
            self._render_recent_rows(recent_rows)
            self._render_order_status_chart(order_status)

            if hasattr(self.window, "txtLastUpdate"):
                self.window.txtLastUpdate.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        except Exception as exc:
            QMessageBox.critical(self.window, "Lỗi", f"Không thể tải dữ liệu tổng quan.\n{exc}")
        finally:
            if self.db is not None:
                self.db.close()
                self.db = None

    def _query_kpis(self, execute):
        sql = """
            SELECT
                (SELECT COUNT(*) FROM [Order]) AS TotalOrders,
                (
                    SELECT ISNULL(SUM(Amount), 0)
                    FROM Payment
                    WHERE PaymentStatus = N'Đã thanh toán'
                      AND PaymentDate IS NOT NULL
                      AND YEAR(PaymentDate) = YEAR(GETDATE())
                      AND MONTH(PaymentDate) = MONTH(GETDATE())
                ) AS MonthlyRevenue,
                (SELECT COUNT(*) FROM Customer) AS TotalCustomers,
                (SELECT COUNT(*) FROM Product) AS TotalProducts,
                (
                    SELECT COUNT(*)
                    FROM Shipment
                    WHERE ShipmentStatus IN (N'Đang vận chuyển', N'Đang giao', N'Chờ lấy hàng')
                ) AS ShippingCount,
                (
                    SELECT COUNT(*)
                    FROM [Order]
                    WHERE OrderStatus = N'Hoàn thành'
                ) AS CompletedOrders,
                (
                    SELECT COUNT(*)
                    FROM (
                        SELECT ProductID, SUM(QuantityInStock) AS TotalQty
                        FROM Inventory
                        GROUP BY ProductID
                    ) inv
                    WHERE inv.TotalQty <= 10
                ) AS LowStockProducts,
                (SELECT COUNT(*) FROM Delivery_Partner) AS PartnerCount
        """
        row = execute(sql).fetchone()
        return {
            "total_orders": int(row[0] or 0),
            "monthly_revenue": float(row[1] or 0),
            "total_customers": int(row[2] or 0),
            "total_products": int(row[3] or 0),
            "shipping_count": int(row[4] or 0),
            "completed_orders": int(row[5] or 0),
            "low_stock_products": int(row[6] or 0),
            "partner_count": int(row[7] or 0),
        }

    def _query_revenue_by_month(self, execute):
        sql_paid = """
            SELECT MONTH(PaymentDate) AS [M], SUM(Amount) AS Revenue
            FROM Payment
            WHERE PaymentStatus = N'Đã thanh toán'
              AND PaymentDate IS NOT NULL
              AND YEAR(PaymentDate) = YEAR(GETDATE())
            GROUP BY MONTH(PaymentDate)
            ORDER BY [M]
        """
        rows = execute(sql_paid).fetchall()
        revenue_by_month = {int(r[0]): float(r[1] or 0) for r in rows}

        # Fallback: neu nam hien tai chua co ban ghi thanh toan da tra,
        # dung tong doanh thu don hang de dashboard khong bi trong.
        if not revenue_by_month:
            sql_orders = """
                SELECT MONTH(OrderDate) AS [M], SUM(TotalAmount) AS Revenue
                FROM [Order]
                WHERE YEAR(OrderDate) = YEAR(GETDATE())
                GROUP BY MONTH(OrderDate)
                ORDER BY [M]
            """
            rows = execute(sql_orders).fetchall()
            revenue_by_month = {int(r[0]): float(r[1] or 0) for r in rows}

        return revenue_by_month

    def _query_top_products(self, execute):
        sql = """
            SELECT TOP 5
                p.ProductID,
                p.ProductName,
                SUM(od.Quantity) AS SoldQty
            FROM Order_Detail od
            JOIN Product p ON p.ProductID = od.ProductID
            GROUP BY p.ProductID, p.ProductName
            ORDER BY SoldQty DESC, p.ProductID ASC
        """
        return execute(sql).fetchall()

    def _query_recent_product_rows(self, execute):
        sql = """
            SELECT TOP 12
                o.OrderID,
                p.ProductName,
                od.Quantity,
                o.OrderDate,
                c.CusName
            FROM [Order] o
            JOIN Order_Detail od ON od.OrderID = o.OrderID
            JOIN Product p ON p.ProductID = od.ProductID
            JOIN Customer c ON c.CustomerID = o.CustomerID
            ORDER BY o.OrderDate DESC, o.OrderID DESC
        """
        return execute(sql).fetchall()

    def _query_order_status(self, execute):
        sql = """
            SELECT OrderStatus, COUNT(*) AS Cnt
            FROM [Order]
            GROUP BY OrderStatus
            ORDER BY Cnt DESC
        """
        return execute(sql).fetchall()

    def _render_kpis(self, kpis):
        self.window.lblTongDonHang.setText(str(kpis["total_orders"]))
        self.window.lblDoanhThuThang.setText(self._format_currency(kpis["monthly_revenue"]))
        self.window.lblKhachHang.setText(str(kpis["total_customers"]))
        self.window.lblSanPham.setText(str(kpis["total_products"]))
        self.window.lblDangGiao.setText(str(kpis["shipping_count"]))
        self.window.lblDonHoanThanh.setText(str(kpis["completed_orders"]))
        self.window.lblSapHetHang.setText(str(kpis["low_stock_products"]))
        self.window.lblDoiTacVC.setText(str(kpis["partner_count"]))

    def _render_revenue_chart(self, revenue_by_month):
        if not hasattr(self.window, "chartDoanhThu"):
            return

        values = [float(revenue_by_month.get(month, 0.0) or 0.0) for month in range(1, 13)]
        values_million = [value / 1_000_000.0 for value in values]

        bar_set = QBarSet("Doanh thu")
        for value in values_million:
            bar_set.append(value)

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Doanh thu theo tháng năm {datetime.now().year}")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        # Tang le trai de nhan truc Y khong bi rut gon thanh "...".
        chart.setMargins(QMargins(52, 8, 10, 8))

        series.setBarWidth(0.62)

        axis_x = QBarCategoryAxis()
        month_labels = [f"T{month}" for month in range(1, 13)]
        axis_x.append(month_labels)
        axis_x.setLabelsAngle(0)
        x_font = QtGui.QFont()
        x_font.setPointSize(9)
        axis_x.setLabelsFont(x_font)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.1f")
        axis_y.setTitleText("Tr. VNĐ")
        y_font = QtGui.QFont()
        y_font.setPointSize(8)
        axis_y.setLabelsFont(y_font)
        max_value_million = max(values_million) if values_million else 0.0
        upper = max(1.0, max_value_million * 1.2)
        upper = float(math.ceil(upper))
        axis_y.setRange(0.0, upper)
        axis_y.setTickCount(6)
        axis_y.setMinorTickCount(0)
        axis_y.setTickInterval(max(0.5, upper / 5.0))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # Ẩn toàn bộ label giá trị trên cột để chart gọn, dễ nhìn.
        series.setLabelsVisible(False)

        chart.legend().setVisible(False)

        self.window.chartDoanhThu.setChart(chart)
        self.window.chartDoanhThu.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

    def _render_order_status_chart(self, status_rows):
        if not hasattr(self.window, "chartTrangThaiGiaoHang"):
            return

        pie_series = QPieSeries()
        total = sum(int(row[1] or 0) for row in status_rows)

        for row in status_rows:
            status = str(row[0] or "Không xác định")
            count = int(row[1] or 0)
            if count <= 0:
                continue

            percent = (count * 100.0 / total) if total else 0.0
            label = f"{status}: {percent:.1f}%"
            slice_obj = pie_series.append(label, count)
            slice_obj.setLabelVisible(True)

        chart = QChart()
        chart.addSeries(pie_series)
        chart.setTitle("Tỷ lệ trạng thái đơn hàng")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)

        self.window.chartTrangThaiGiaoHang.setChart(chart)
        self.window.chartTrangThaiGiaoHang.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

    def _render_top_products(self, rows):
        if not hasattr(self.window, "tblTopProduct"):
            return

        table = self.window.tblTopProduct
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Mã SP", "Tên sản phẩm", "Đã bán"])
        table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            product_id = int(row[0] or 0)
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(f"SP{product_id:03d}"))
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(row[1] or "")))
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(int(row[2] or 0))))

        table.resizeColumnsToContents()

    def _render_recent_rows(self, rows):
        if not hasattr(self.window, "tblRecentOrder"):
            return

        table = self.window.tblRecentOrder
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Mã đơn", "Sản phẩm", "Số lượng", "Ngày mua", "Khách hàng"])
        table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            order_id = int(row[0] or 0)
            product_name = str(row[1] or "")
            quantity = int(row[2] or 0)
            order_date = self._format_date(row[3])
            customer_name = str(row[4] or "")

            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(f"DH{order_id:03d}"))
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(product_name))
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(quantity)))
            table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(order_date))
            table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(customer_name))

        table.resizeColumnsToContents()

    def _format_currency(self, value):
        return f"{float(value or 0):,.0f} VNĐ"

    def _format_date(self, value):
        if value is None:
            return ""
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y")
        return str(value)
