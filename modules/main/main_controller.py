"""Main controller for the sales-and-warehouse app."""
import logging
import traceback

from PyQt6 import QtCore, QtWidgets

from database.database import Database
from modules.category.category_handler import (
    CategoryHandler,
    CategoryAddDialog,
    CategoryDetailDialog,
)
from modules.inventory.inventory_handler import (
    InventoryHandler,
    InventoryDetailDialog,
    InventoryUpdateDialog,
)
from modules.payment.payment_handler import PaymentHandler, PaymentDetailDialog
from ui.main_window import Ui_phanTuChinhWindow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MainController(QtWidgets.QMainWindow, Ui_phanTuChinhWindow):
    def __init__(self):
        super().__init__()
        try:
            self.setupUi(self)
            self.db = Database()
            self.category_handler = CategoryHandler(self.db)
            self.inventory_handler = InventoryHandler(self.db)
            self.payment_handler = PaymentHandler(self.db)

            self.categories = self.category_handler.list_categories()
            self.product_map = {}
            self.inventory_items = self.inventory_handler.list_items()
            self.payment_records = self.payment_handler.list_payments()

            self.btnDanhMuc.clicked.connect(lambda: self.khungChuyenTrangStacked.setCurrentWidget(self.pageDanhMuc))
            self.btnTonKho.clicked.connect(lambda: self.khungChuyenTrangStacked.setCurrentWidget(self.pageTonKho))
            self.btnThanhToan.clicked.connect(lambda: self.khungChuyenTrangStacked.setCurrentWidget(self.pageThanhToan))

            self.setup_category_handlers()
            self.setup_inventory_handlers()
            self.setup_payment_handlers()
            self.refresh_category_table()
            self.refresh_inventory_table()
            self.refresh_payment_table()
        except Exception:
            logger.error("Unhandled error during MainController initialization:\n%s", traceback.format_exc())
            raise

    def setup_category_handlers(self):
        self.tblDM.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblDM.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.cbbTimKiemDM.setEditable(True)
        self.cbbTimKiemDM.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.cbbTimKiemDM.lineEdit().setPlaceholderText("Nhập mã hoặc tên danh mục")
        self.btnThemDM.clicked.connect(self.open_add_category)
        self.btnChiTietDM.clicked.connect(self.open_detail_category)
        self.btnCapNhatDM.clicked.connect(self.open_update_category)
        self.btnXoaDM.clicked.connect(self.delete_selected_category)
        self.btnRefreshDM.clicked.connect(self.refresh_category_table)
        self.btnTimKiemDM.clicked.connect(self.filter_category_table)
        self.cbbTimKiemDM.currentTextChanged.connect(self.filter_category_table)

    def setup_inventory_handlers(self):
        self.tblTonKho.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblTonKho.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.txtTimKiemTK.setPlaceholderText("Nhập mã hoặc tên sản phẩm")
        self.btnChiTietTK = QtWidgets.QPushButton("Chi tiết", parent=self.pageTonKho)
        self.buttonLayout.insertWidget(1, self.btnChiTietTK)
        self.tblTonKho.itemDoubleClicked.connect(lambda _: self.open_inventory_detail())
        self.btnChiTietTK.clicked.connect(self.open_inventory_detail)
        self.btnCapNhatTK.clicked.connect(self.open_inventory_update)
        self.btnRefreshTK.clicked.connect(self.refresh_inventory_table)
        self.btnTimKiemTK.clicked.connect(self.filter_inventory_table)
        self.txtTimKiemTK.textChanged.connect(self.filter_inventory_table)

    def setup_payment_handlers(self):
        self.tblThanhToan.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblThanhToan.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.btnChiTietTT = QtWidgets.QPushButton("Chi tiết", parent=self.pageThanhToan)
        self.crudLayout.insertWidget(1, self.btnChiTietTT)
        self.tblThanhToan.itemDoubleClicked.connect(lambda _: self.open_payment_detail())
        self.btnChiTietTT.clicked.connect(self.open_payment_detail)
        self.btnXacNhanTT.clicked.connect(self.open_payment_detail)
        self.btnXoaTT.clicked.connect(self.delete_selected_payment)
        self.btnRefreshTT.clicked.connect(self.refresh_payment_table)
        self.btnTimKiemTT.clicked.connect(self.filter_payment_table)
        self.txtTimKiemTT.textChanged.connect(self.filter_payment_table)
        self.txtTuNgayTT.setDate(QtCore.QDate(2000, 1, 1))
        self.txtDenNgayTT.setDate(QtCore.QDate(2000, 1, 1))
        self.txtTuNgayTT.dateChanged.connect(self.filter_payment_table)
        self.txtDenNgayTT.dateChanged.connect(self.filter_payment_table)

    def generate_category_code(self):
        return self.category_handler.generate_category_code()

    def refresh_product_map(self):
        self.product_map = {}
        for item in self.inventory_items:
            category_name = item.get("danhMuc", "")
            self.product_map.setdefault(category_name, []).append(item)

    def refresh_category_table(self):
        self.categories = self.category_handler.list_categories()
        current_text = self.cbbTimKiemDM.currentText()
        self.cbbTimKiemDM.blockSignals(True)
        self.cbbTimKiemDM.clear()
        self.cbbTimKiemDM.addItem("")
        for item in self.categories:
            self.cbbTimKiemDM.addItem(item.get("maDM", ""))
            self.cbbTimKiemDM.addItem(item.get("tenDM", ""))
        self.cbbTimKiemDM.setCurrentText(current_text)
        self.cbbTimKiemDM.blockSignals(False)
        self.populate_category_table(self.categories)

    def populate_category_table(self, items):
        self.tblDM.setRowCount(0)
        for item in items:
            row = self.tblDM.rowCount()
            self.tblDM.insertRow(row)
            self.tblDM.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("maDM", "")))
            self.tblDM.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get("tenDM", "")))
            self.tblDM.setItem(row, 2, QtWidgets.QTableWidgetItem(item.get("moTa", "")))
            self.tblDM.setItem(row, 3, QtWidgets.QTableWidgetItem(str(item.get("sl", 0))))

    def filter_category_table(self):
        keyword = self.cbbTimKiemDM.currentText().strip().lower()
        if not keyword:
            self.populate_category_table(self.categories)
            return
        filtered = [
            item for item in self.categories
            if keyword in item.get("maDM", "").lower() or keyword in item.get("tenDM", "").lower()
        ]
        self.populate_category_table(filtered)

    def get_selected_category(self):
        row = self.tblDM.currentRow()
        if row < 0:
            return None
        category_id = self.tblDM.item(row, 0).text()
        for item in self.categories:
            if item.get("maDM") == category_id:
                return item
        return None

    def open_add_category(self):
        dialog = CategoryAddDialog(self.category_handler, self)
        dialog.prepare_for_add()
        dialog.setWindowTitle("Thêm danh mục")
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_category_table()
            QtWidgets.QMessageBox.information(self, "Thông báo", "Thêm danh mục thành công!")

    def open_detail_category(self):
        category = self.get_selected_category()
        if category is None:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một danh mục để xem chi tiết.")
            return
        dialog = CategoryDetailDialog(self.category_handler, self)
        dialog.fill_category(category, self.inventory_items)
        dialog.setWindowTitle("Chi tiết danh mục")
        result = dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_category_table()
            self.refresh_inventory_table()

    def open_update_category(self, category=None):
        if category is None:
            category = self.get_selected_category()
        if category is None:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một danh mục để cập nhật.")
            return
        dialog = CategoryAddDialog(self.category_handler, self)
        dialog.setWindowTitle("Cập nhật danh mục")
        dialog.prepare_for_update(category)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_category_table()
            QtWidgets.QMessageBox.information(self, "Thông báo", "Cập nhật danh mục thành công!")

    def delete_category(self, category=None):
        if category is None:
            category = self.get_selected_category()
        if category is None:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một danh mục để xóa.")
            return False
        reply = QtWidgets.QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa danh mục {category.get('maDM', '')} - {category.get('tenDM', '')}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.category_handler.delete_category(category.get("maDM", ""))
            self.refresh_category_table()
            self.refresh_inventory_table()
            QtWidgets.QMessageBox.information(self, "Thông báo", "Xóa danh mục thành công!")
            return True
        return False

    def delete_selected_category(self):
        self.delete_category()

    def update_inventory_total_label(self):
        total = sum(int(item.get("tonKho", 0)) for item in self.inventory_items)
        self.lblTongTK.setText(f"Tổng tồn kho: {total}")

    def populate_inventory_table(self, items):
        self.tblTonKho.setRowCount(0)
        for item in items:
            row = self.tblTonKho.rowCount()
            self.tblTonKho.insertRow(row)
            self.tblTonKho.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("maSP", "")))
            self.tblTonKho.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get("tenSP", "")))
            self.tblTonKho.setItem(row, 2, QtWidgets.QTableWidgetItem(item.get("danhMuc", "")))
            self.tblTonKho.setItem(row, 3, QtWidgets.QTableWidgetItem(item.get("donViTinh", "")))
            self.tblTonKho.setItem(row, 4, QtWidgets.QTableWidgetItem(str(item.get("tonKho", 0))))
            self.tblTonKho.setItem(row, 5, QtWidgets.QTableWidgetItem(item.get("trangThai", "")))
            self.tblTonKho.setItem(row, 6, QtWidgets.QTableWidgetItem(item.get("capNhatGanNhat", "")))

    def refresh_inventory_table(self):
        self.inventory_items = self.inventory_handler.list_items()
        self.refresh_product_map()
        self.populate_inventory_table(self.inventory_items)
        self.update_inventory_total_label()

    def get_selected_inventory_item(self):
        row = self.tblTonKho.currentRow()
        if row < 0:
            return None
        code = self.tblTonKho.item(row, 0).text()
        for item in self.inventory_items:
            if item.get("maSP") == code:
                return item
        return None

    def filter_inventory_table(self):
        keyword = self.txtTimKiemTK.text().strip().lower()
        if not keyword:
            self.populate_inventory_table(self.inventory_items)
        else:
            filtered = [
                item for item in self.inventory_items
                if keyword in item.get("maSP", "").lower() or keyword in item.get("tenSP", "").lower() or keyword in item.get("danhMuc", "").lower()
            ]
            self.populate_inventory_table(filtered)
        self.update_inventory_total_label()

    def open_inventory_detail(self, item=None):
        if item is None:
            item = self.get_selected_inventory_item()
        if item is None:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một sản phẩm để xem chi tiết.")
            return
        dialog = InventoryDetailDialog(self.inventory_handler, self)
        dialog.fill_item(item)
        dialog.setWindowTitle("Chi tiết tồn kho")
        result = dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_inventory_table()

    def open_inventory_update(self, item=None):
        if item is None:
            item = self.get_selected_inventory_item()
        if item is None:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một sản phẩm để cập nhật tồn kho.")
            return
        dialog = InventoryUpdateDialog(self.inventory_handler, self)
        dialog.prepare_for_update(item)
        dialog.setWindowTitle("Cập nhật tồn kho")
        result = dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_inventory_table()

    def apply_inventory_adjustment(self, item, mode, quantity, note):
        self.inventory_handler.apply_inventory_adjustment(item, mode, quantity, note, nhan_vien="NV999")
        self.refresh_inventory_table()
        QtWidgets.QMessageBox.information(self, "Thông báo", "Cập nhật tồn kho thành công!")

    def get_selected_payment(self):
        row = self.tblThanhToan.currentRow()
        if row < 0:
            return None
        code = self.tblThanhToan.item(row, 0).text()
        for item in self.payment_records:
            if item.get("maTT") == code:
                return item
        return None

    def populate_payment_table(self, items):
        self.tblThanhToan.setRowCount(0)
        for item in items:
            row = self.tblThanhToan.rowCount()
            self.tblThanhToan.insertRow(row)
            self.tblThanhToan.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("maTT", "")))
            self.tblThanhToan.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get("maDH", "")))
            self.tblThanhToan.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{item.get('tongTien', 0):,}"))
            self.tblThanhToan.setItem(row, 3, QtWidgets.QTableWidgetItem(item.get("phuongThuc", "")))
            self.tblThanhToan.setItem(row, 4, QtWidgets.QTableWidgetItem(item.get("trangThai", "")))

    def refresh_payment_table(self):
        self.payment_records = self.payment_handler.list_payments()
        self.populate_payment_table(self.payment_records)

    def filter_payment_table(self):
        keyword = self.txtTimKiemTT.text().strip().lower()
        default_date = QtCore.QDate(2000, 1, 1)
        start = self.txtTuNgayTT.date()
        end = self.txtDenNgayTT.date()
        if start == default_date:
            start = None
        if end == default_date:
            end = None
        filtered = self.payment_records
        if keyword:
            filtered = [
                item for item in filtered
                if keyword in item.get("maTT", "").lower() or keyword in item.get("maDH", "").lower()
            ]
        if start is not None and end is not None:
            filtered = [
                item for item in filtered
                if item.get("ngayTT") and start <= QtCore.QDate.fromString(item.get("ngayTT", ""), "dd/MM/yyyy") <= end
            ]
        elif start is not None:
            filtered = [
                item for item in filtered
                if item.get("ngayTT") and QtCore.QDate.fromString(item.get("ngayTT", ""), "dd/MM/yyyy") >= start
            ]
        elif end is not None:
            filtered = [
                item for item in filtered
                if item.get("ngayTT") and QtCore.QDate.fromString(item.get("ngayTT", ""), "dd/MM/yyyy") <= end
            ]
        self.populate_payment_table(filtered)

    def confirm_payment(self, payment=None):
        if payment is None:
            payment = self.get_selected_payment()
        if payment is None:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một thanh toán để xác nhận.")
            return
        self.payment_handler.confirm_payment(payment)
        self.refresh_payment_table()
        QtWidgets.QMessageBox.information(self, "Thông báo", "Xác nhận thanh toán thành công!")

    def delete_selected_payment(self):
        payment = self.get_selected_payment()
        if payment is None:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một thanh toán để xóa.")
            return
        reply = QtWidgets.QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa thanh toán {payment.get('maTT', '')}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.payment_handler.delete_payment(payment.get("maTT", ""))
            self.refresh_payment_table()
            QtWidgets.QMessageBox.information(self, "Thông báo", "Xóa thanh toán thành công!")

    def open_payment_detail(self, payment=None):
        if payment is None:
            payment = self.get_selected_payment()
        if payment is None:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một thanh toán để xem chi tiết.")
            return
        dialog = PaymentDetailDialog(self.payment_handler, self)
        dialog.fill_payment(payment)
        dialog.setWindowTitle("Chi tiết thanh toán")
        result = dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.refresh_payment_table()
