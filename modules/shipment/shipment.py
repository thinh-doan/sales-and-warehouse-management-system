from __future__ import annotations

from datetime import date, datetime
import os
import sys
from typing import Optional

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QAbstractItemView, QDialog, QMessageBox, QTableWidgetItem

try:
	from connect import Database
except ModuleNotFoundError:
	PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	if PROJECT_ROOT not in sys.path:
		sys.path.insert(0, PROJECT_ROOT)
	from connect import Database

from .shipment_detail_ui import Ui_txtNote
from .shipment_status_ui import Ui_Dialog as Ui_ShipmentStatus


class ShipmentHandler:
	def __init__(self, db: Optional[Database] = None):
		self.db = db

	@staticmethod
	def _format_date(value) -> str:
		if value is None:
			return ""
		if isinstance(value, datetime):
			value = value.date()
		if isinstance(value, date):
			return value.strftime("%d/%m/%Y")
		return str(value)

	@staticmethod
	def _format_currency(value) -> str:
		try:
			return f"{float(value or 0):,.0f}"
		except (TypeError, ValueError):
			return "0"

	def _create_db(self):
		return self.db or Database()

	def list_shipments(self, keyword=None, status=None, start_date=None, end_date=None):
		db = self._create_db()
		should_close = db is not self.db
		try:
			conditions = []
			params = []

			if keyword:
				conditions.append("(CAST(s.ShipmentID AS NVARCHAR(20)) LIKE ? OR CAST(s.OrderID AS NVARCHAR(20)) LIKE ? OR c.CusName LIKE ? OR ISNULL(d.PrtName, N'') LIKE ?)")
				like_value = f"%{keyword}%"
				params.extend([like_value, like_value, like_value, like_value])

			if status and status != "Tất cả":
				conditions.append("s.ShipmentStatus = ?")
				params.append(status)

			if start_date and end_date:
				conditions.append("CAST(s.ShipmentDate AS DATE) BETWEEN ? AND ?")
				params.extend([start_date, end_date])

			sql = """
				SELECT s.ShipmentID,
					   s.OrderID,
					   c.CusName,
					   ISNULL(d.PrtName, N''),
					   ISNULL(s.ShipmentMethod, N''),
					   s.ShipmentDate,
					   s.ShipmentStatus,
					   s.PartnerID,
					   s.ExpectedDeliveryDate,
					   s.ActualDeliveryDate,
					   s.ShippingFee
				FROM Shipment s
				JOIN [Order] o ON o.OrderID = s.OrderID
				JOIN Customer c ON c.CustomerID = o.CustomerID
				LEFT JOIN Delivery_Partner d ON d.PartnerID = s.PartnerID
			"""
			if conditions:
				sql += " WHERE " + " AND ".join(conditions)
			sql += " ORDER BY s.ShipmentDate DESC, s.ShipmentID DESC"

			rows = db.execute(sql, params).fetchall()
			return [
				{
					"shipmentID": int(row[0] or 0),
					"orderID": int(row[1] or 0),
					"customerName": row[2] or "",
					"partnerName": row[3] or "",
					"shipmentMethod": row[4] or "",
					"shipmentDate": self._format_date(row[5]),
					"shipmentStatus": row[6] or "",
					"partnerID": int(row[7] or 0),
					"expectedDeliveryDate": self._format_date(row[8]),
					"actualDeliveryDate": self._format_date(row[9]),
					"shippingFee": float(row[10] or 0),
				}
				for row in rows
			]
		finally:
			if should_close:
				db.close()

	def get_shipment(self, shipment_id):
		db = self._create_db()
		should_close = db is not self.db
		try:
			row = db.execute(
				"""
				SELECT s.ShipmentID,
					   s.OrderID,
					   c.CusName,
					   c.CusPhone,
					   c.CusAddress,
					   ISNULL(d.PrtName, N''),
					   ISNULL(s.ShipmentMethod, N''),
					   s.ShippingFee,
					   s.ShipmentDate,
					   s.ExpectedDeliveryDate,
					   s.ActualDeliveryDate,
					   s.ShipmentStatus,
					   o.ShippingAddress,
					   o.OrderDate,
					   o.TotalAmount
				FROM Shipment s
				JOIN [Order] o ON o.OrderID = s.OrderID
				JOIN Customer c ON c.CustomerID = o.CustomerID
				LEFT JOIN Delivery_Partner d ON d.PartnerID = s.PartnerID
				WHERE s.ShipmentID = ?
				""",
				(int(shipment_id),),
			).fetchone()
			if not row:
				return None
			return {
				"shipmentID": int(row[0] or 0),
				"orderID": int(row[1] or 0),
				"customerName": row[2] or "",
				"customerPhone": row[3] or "",
				"customerAddress": row[4] or "",
				"partnerName": row[5] or "",
				"shipmentMethod": row[6] or "",
				"shippingFee": float(row[7] or 0),
				"shipmentDate": self._format_date(row[8]),
				"expectedDeliveryDate": self._format_date(row[9]),
				"actualDeliveryDate": self._format_date(row[10]),
				"shipmentStatus": row[11] or "",
				"shippingAddress": row[12] or "",
				"orderDate": self._format_date(row[13]),
				"orderTotal": float(row[14] or 0),
				"note": self._build_note(row),
				"items": self.get_shipment_items(int(row[1] or 0)),
			}
		finally:
			if should_close:
				db.close()

	def _build_note(self, row):
		shipment_status = row[11] or ""
		partner_name = row[5] or ""
		method = row[6] or ""
		return f"Đối tác: {partner_name or 'Chưa cập nhật'} | Phương thức: {method or 'Chưa cập nhật'} | Trạng thái: {shipment_status or 'Chưa cập nhật'}"

	def get_shipment_items(self, order_id):
		db = self._create_db()
		should_close = db is not self.db
		try:
			rows = db.execute(
				"""
				SELECT p.ProductID,
					   p.ProductName,
					   ISNULL(p.Unit, N''),
					   od.Quantity,
					   od.OrderDetailUnitPrice,
					   od.Quantity * od.OrderDetailUnitPrice
				FROM Order_Detail od
				JOIN Product p ON p.ProductID = od.ProductID
				WHERE od.OrderID = ?
				ORDER BY p.ProductID
				""",
				(int(order_id),),
			).fetchall()
			return [
				{
					"productID": int(row[0] or 0),
					"productName": row[1] or "",
					"unit": row[2] or "",
					"quantity": int(row[3] or 0),
					"unitPrice": float(row[4] or 0),
					"amount": float(row[5] or 0),
				}
				for row in rows
			]
		finally:
			if should_close:
				db.close()

	def update_shipment_status(self, shipment_id, shipment_status):
		db = self._create_db()
		should_close = db is not self.db
		try:
			actual_date = None
			if shipment_status in {"Giao thành công", "Giao thất bại"}:
				actual_date = date.today()
			db.execute(
				"UPDATE Shipment SET ShipmentStatus = ?, ActualDeliveryDate = ? WHERE ShipmentID = ?",
				(shipment_status, actual_date, int(shipment_id)),
			)
			db.commit()
			return True
		except Exception:
			try:
				db.rollback()
			except Exception:
				pass
			raise
		finally:
			if should_close:
				db.close()


class ShipmentStatusDialog(QDialog, Ui_ShipmentStatus):
	def __init__(self, handler: ShipmentHandler, shipment=None, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.handler = handler
		self.shipment = shipment or {}
		self._current_status = self.shipment.get("shipmentStatus", "")

		self.btnCloseVC = self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		self.btnOkVC = self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
		if self.btnOkVC is not None:
			self.btnOkVC.setText("Lưu")
		if self.btnCloseVC is not None:
			self.btnCloseVC.setText("Hủy")

		self._prepare_form()
		self.buttonBox.accepted.connect(self.on_save)
		self.buttonBox.rejected.connect(self.reject)

	def _prepare_form(self):
		status = self._current_status
		if status == "Chờ lấy hàng":
			self.rbChoLayHang.setChecked(True)
		elif status == "Đang giao hàng":
			self.rbDangGiaoHang.setChecked(True)
		elif status == "Giao thành công":
			self.rbGiaoThanhCong.setChecked(True)
		elif status == "Giao thất bại":
			self.rbGiaoThaiBai.setChecked(True)

	def selected_status(self):
		if self.rbChoLayHang.isChecked():
			return "Chờ lấy hàng"
		if self.rbDangGiaoHang.isChecked():
			return "Đang giao hàng"
		if self.rbGiaoThanhCong.isChecked():
			return "Giao thành công"
		if self.rbGiaoThaiBai.isChecked():
			return "Giao thất bại"
		return self._current_status

	def on_save(self):
		shipment_id = self.shipment.get("shipmentID")
		if not shipment_id:
			QMessageBox.warning(self, "Thông báo", "Không tìm thấy mã giao hàng để cập nhật.")
			return

		new_status = self.selected_status()
		if not new_status:
			QMessageBox.warning(self, "Thông báo", "Vui lòng chọn trạng thái giao hàng.")
			return

		try:
			self.handler.update_shipment_status(shipment_id, new_status)
		except Exception as exc:
			QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật trạng thái giao hàng.\nChi tiết: {exc}")
			return
		self.accept()


class ShipmentDetailDialog(QDialog, Ui_txtNote):
	def __init__(self, handler: ShipmentHandler, shipment=None, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.handler = handler
		self.shipment = shipment or {}

		self.tblSanPham.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
		self.tblSanPham.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
		self.tblSanPham.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
		self.tblSanPham.setAlternatingRowColors(True)
		self.tblSanPham.setColumnCount(6)
		self.tblSanPham.setHorizontalHeaderLabels(["Mã SP", "Tên SP", "Đơn vị", "Số lượng", "Đơn giá", "Thành tiền"])

		self.btnCloseVC.clicked.connect(self.reject)
		self.btnCapNhatVC.clicked.connect(self.open_status_dialog)
		self._prepare_date_edits()
		self.fill_shipment(self.shipment)

	def _prepare_date_edits(self):
		for widget in (self.txtNgayTao, self.txtNgayDuKien, self.txtNgayThucTe):
			widget.setDisplayFormat("dd/MM/yyyy")
			widget.setCalendarPopup(True)
			widget.setMinimumDate(QtCore.QDate(1900, 1, 1))

		self.txtNgayTao.setReadOnly(True)
		self.txtNgayDuKien.setReadOnly(True)
		self.txtNgayThucTe.setReadOnly(True)
		self.lineEdit.setReadOnly(True)

	@staticmethod
	def _apply_date(widget, value):
		if value:
			if isinstance(value, str):
				try:
					parsed = datetime.strptime(value, "%d/%m/%Y")
					widget.setDate(parsed.date())
					return
				except ValueError:
					pass
			if isinstance(value, datetime):
				value = value.date()
			if isinstance(value, date):
				widget.setDate(value)
				return
		widget.setSpecialValueText("Chưa cập nhật")
		widget.setDate(QtCore.QDate(1900, 1, 1))

	def fill_shipment(self, shipment):
		self.shipment = shipment or {}
		if not self.shipment:
			return

		self.txtMaGH.setText(str(self.shipment.get("shipmentID", "")))
		self.txtMaDonHang.setText(str(self.shipment.get("orderID", "")))
		self.txtTenKH.setText(self.shipment.get("customerName", ""))
		self.txtDiaChi.setText(self.shipment.get("shippingAddress", "") or self.shipment.get("customerAddress", ""))
		self.txtSDT_KH.setText(self.shipment.get("customerPhone", ""))
		self.txtPhuongThucVC.setText(self.shipment.get("shipmentMethod", ""))
		self.txtPhiVC.setText(self.handler._format_currency(self.shipment.get("shippingFee", 0)))
		self.txtTrangThai.setText(self.shipment.get("shipmentStatus", ""))
		self.txtDonViVC.setText(self.shipment.get("partnerName", ""))
		self.lineEdit.setText(self.shipment.get("note", ""))
		self._apply_date(self.txtNgayTao, self.shipment.get("shipmentDate"))
		self._apply_date(self.txtNgayDuKien, self.shipment.get("expectedDeliveryDate"))
		self._apply_date(self.txtNgayThucTe, self.shipment.get("actualDeliveryDate"))

		items = self.shipment.get("items") or self.handler.get_shipment_items(int(self.shipment.get("orderID") or 0))
		self.tblSanPham.setRowCount(0)
		for item in items:
			row = self.tblSanPham.rowCount()
			self.tblSanPham.insertRow(row)
			self.tblSanPham.setItem(row, 0, QTableWidgetItem(str(item.get("productID", ""))))
			self.tblSanPham.setItem(row, 1, QTableWidgetItem(item.get("productName", "")))
			self.tblSanPham.setItem(row, 2, QTableWidgetItem(item.get("unit", "")))
			self.tblSanPham.setItem(row, 3, QTableWidgetItem(str(item.get("quantity", 0))))
			self.tblSanPham.setItem(row, 4, QTableWidgetItem(self.handler._format_currency(item.get("unitPrice", 0))))
			self.tblSanPham.setItem(row, 5, QTableWidgetItem(self.handler._format_currency(item.get("amount", 0))))

		self.tblSanPham.resizeColumnsToContents()

	def open_status_dialog(self):
		if not self.shipment.get("shipmentID"):
			QMessageBox.warning(self, "Thông báo", "Không có dữ liệu giao hàng để cập nhật.")
			return
		dialog = ShipmentStatusDialog(self.handler, shipment=self.shipment, parent=self)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			refreshed = self.handler.get_shipment(int(self.shipment.get("shipmentID")))
			if refreshed:
				self.fill_shipment(refreshed)
			self.accept()


class ShipmentPageController:
	def __init__(self, window, db: Optional[Database] = None):
		self.window = window
		self.handler = ShipmentHandler(db)
		self._connect_signals()
		self._prepare_table()
		self._prepare_filters()
		self.load_shipment_table()

	def _connect_signals(self):
		self.window.btnChiTietVC.clicked.connect(self.open_detail_dialog)
		self.window.btnCapNhatVC.clicked.connect(self.open_status_dialog)
		self.window.btnRefreshVC.clicked.connect(self.load_shipment_table)
		self.window.btnTimKiemVC.clicked.connect(self.search_shipments)
		if hasattr(self.window, "txtTimKiemVC"):
			self.window.txtTimKiemVC.returnPressed.connect(self.search_shipments)
		if hasattr(self.window, "txtTuNgayVC"):
			self.window.txtTuNgayVC.dateChanged.connect(lambda _: self.search_shipments())
		if hasattr(self.window, "txtDenNgayVC"):
			self.window.txtDenNgayVC.dateChanged.connect(lambda _: self.search_shipments())
		if hasattr(self.window, "cbbTimKiemVC"):
			self.window.cbbTimKiemVC.currentIndexChanged.connect(lambda _: self.search_shipments())
		self.window.tblVanChuyen.itemDoubleClicked.connect(lambda _: self.open_detail_dialog())
		self.window.tblVanChuyen.itemSelectionChanged.connect(self._update_button_state)

	def _prepare_table(self):
		table = self.window.tblVanChuyen
		table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
		table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
		table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
		table.setAlternatingRowColors(True)
		table.setSortingEnabled(True)
		headers = ["Mã GH", "Mã ĐH", "Khách hàng", "Đơn vị VC", "Phương thức", "Ngày giao", "Trạng thái"]
		table.setColumnCount(len(headers))
		table.setHorizontalHeaderLabels(headers)

	def _prepare_filters(self):
		if hasattr(self.window, "cbbTimKiemVC") and self.window.cbbTimKiemVC.count() == 0:
			self.window.cbbTimKiemVC.addItems([
				"Tất cả",
				"Chờ lấy hàng",
				"Đang giao hàng",
				"Giao thành công",
				"Giao thất bại",
			])
		if hasattr(self.window, "txtTuNgayVC"):
			self.window.txtTuNgayVC.setDate(QtCore.QDate.currentDate().addMonths(-1))
		if hasattr(self.window, "txtDenNgayVC"):
			self.window.txtDenNgayVC.setDate(QtCore.QDate.currentDate())

	def _selected_shipment_id(self):
		selected_rows = self.window.tblVanChuyen.selectionModel().selectedRows()
		if not selected_rows:
			return None
		row = selected_rows[0].row()
		item = self.window.tblVanChuyen.item(row, 0)
		if not item:
			return None
		try:
			return int(item.text())
		except ValueError:
			return None

	def _selected_shipment(self):
		shipment_id = self._selected_shipment_id()
		if shipment_id is None:
			return None
		return self.handler.get_shipment(shipment_id)

	def _update_button_state(self):
		has_selection = self._selected_shipment_id() is not None
		self.window.btnChiTietVC.setEnabled(has_selection)
		self.window.btnCapNhatVC.setEnabled(has_selection)

	def search_shipments(self):
		keyword = self.window.txtTimKiemVC.text().strip() if hasattr(self.window, "txtTimKiemVC") else ""
		status = self.window.cbbTimKiemVC.currentText().strip() if hasattr(self.window, "cbbTimKiemVC") else "Tất cả"
		start_date = self.window.txtTuNgayVC.date().toPyDate() if hasattr(self.window, "txtTuNgayVC") else None
		end_date = self.window.txtDenNgayVC.date().toPyDate() if hasattr(self.window, "txtDenNgayVC") else None
		self.load_shipment_table(keyword=keyword or None, status=status or None, start_date=start_date, end_date=end_date)

	def load_shipment_table(self, keyword=None, status=None, start_date=None, end_date=None):
		shipments = self.handler.list_shipments(keyword=keyword, status=status, start_date=start_date, end_date=end_date)
		table = self.window.tblVanChuyen
		table.setSortingEnabled(False)
		table.setRowCount(0)
		for shipment in shipments:
			row = table.rowCount()
			table.insertRow(row)
			table.setItem(row, 0, QTableWidgetItem(str(shipment.get("shipmentID", ""))))
			table.setItem(row, 1, QTableWidgetItem(str(shipment.get("orderID", ""))))
			table.setItem(row, 2, QTableWidgetItem(shipment.get("customerName", "")))
			table.setItem(row, 3, QTableWidgetItem(shipment.get("partnerName", "")))
			table.setItem(row, 4, QTableWidgetItem(shipment.get("shipmentMethod", "")))
			table.setItem(row, 5, QTableWidgetItem(shipment.get("shipmentDate", "")))
			table.setItem(row, 6, QTableWidgetItem(shipment.get("shipmentStatus", "")))
		table.resizeColumnsToContents()
		table.setSortingEnabled(True)
		self._update_button_state()

	def open_detail_dialog(self):
		shipment = self._selected_shipment()
		if not shipment:
			QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một dòng giao hàng để xem chi tiết.")
			return
		dialog = ShipmentDetailDialog(self.handler, shipment=shipment, parent=self.window)
		dialog.exec()
		self.load_shipment_table()

	def open_status_dialog(self):
		shipment = self._selected_shipment()
		if not shipment:
			QMessageBox.warning(self.window, "Thông báo", "Vui lòng chọn một dòng giao hàng để cập nhật trạng thái.")
			return
		dialog = ShipmentStatusDialog(self.handler, shipment=shipment, parent=self.window)
		if dialog.exec() == QDialog.DialogCode.Accepted:
			self.load_shipment_table()
