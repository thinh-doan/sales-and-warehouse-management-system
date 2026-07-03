import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sales_warehouse.db")


class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute(
                """\n                CREATE TABLE IF NOT EXISTS categories (
                    maDM TEXT PRIMARY KEY,
                    tenDM TEXT NOT NULL,
                    moTa TEXT,
                    sl INTEGER DEFAULT 0
                )
                """
            )
            conn.execute(
                """\n                CREATE TABLE IF NOT EXISTS inventory (
                    maSP TEXT PRIMARY KEY,
                    tenSP TEXT NOT NULL,
                    danhMuc TEXT,
                    donViTinh TEXT,
                    tonKho INTEGER DEFAULT 0,
                    trangThai TEXT,
                    capNhatGanNhat TEXT
                )
                """
            )
            conn.execute(
                """\n                CREATE TABLE IF NOT EXISTS inventory_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    maSP TEXT NOT NULL,
                    ngay TEXT,
                    loai TEXT,
                    soLuong INTEGER,
                    nhanVien TEXT,
                    ghiChu TEXT,
                    FOREIGN KEY(maSP) REFERENCES inventory(maSP)
                )
                """
            )
            conn.execute(
                """\n                CREATE TABLE IF NOT EXISTS payments (
                    maTT TEXT PRIMARY KEY,
                    maDH TEXT,
                    khachHang TEXT,
                    tongTien REAL DEFAULT 0,
                    phuongThuc TEXT,
                    trangThai TEXT,
                    ngayTT TEXT
                )
                """
            )
            conn.commit()
            self.seed_sample_data(conn)

    def seed_sample_data(self, conn):
        categories = [
            {"maDM": "DM001", "tenDM": "Điện tử", "moTa": "Sản phẩm điện tử", "sl": 5},
            {"maDM": "DM002", "tenDM": "Gia dụng", "moTa": "Sản phẩm gia dụng", "sl": 8},
            {"maDM": "DM003", "tenDM": "Thời trang", "moTa": "Sản phẩm thời trang", "sl": 3},
        ]
        inventory = [
            {"maSP": "SP001", "tenSP": "Laptop", "danhMuc": "Điện tử", "donViTinh": "Chiếc", "tonKho": 15, "trangThai": "Còn hàng", "capNhatGanNhat": "01/07/2026"},
            {"maSP": "SP002", "tenSP": "Phone", "danhMuc": "Điện tử", "donViTinh": "Chiếc", "tonKho": 20, "trangThai": "Còn hàng", "capNhatGanNhat": "01/07/2026"},
            {"maSP": "SP003", "tenSP": "Máy hút bụi", "danhMuc": "Gia dụng", "donViTinh": "Chiếc", "tonKho": 10, "trangThai": "Còn hàng", "capNhatGanNhat": "01/07/2026"},
        ]
        payments = [
            {"maTT": "TT001", "maDH": "DH001", "khachHang": "Nguyễn Văn An", "tongTien": 1200000, "phuongThuc": "Tiền mặt", "trangThai": "Chưa thanh toán", "ngayTT": "10/06/2026"},
            {"maTT": "TT002", "maDH": "DH002", "khachHang": "Trần Thị Bình", "tongTien": 850000, "phuongThuc": "Chuyển khoản", "trangThai": "Đã thanh toán", "ngayTT": "01/07/2026"},
            {"maTT": "TT003", "maDH": "DH003", "khachHang": "Lê Văn Cường", "tongTien": 2500000, "phuongThuc": "Thẻ", "trangThai": "Chưa thanh toán", "ngayTT": "20/06/2026"},
        ]

        for item in categories:
            conn.execute(
                "INSERT OR IGNORE INTO categories (maDM, tenDM, moTa, sl) VALUES (?, ?, ?, ?)",
                (item["maDM"], item["tenDM"], item["moTa"], item["sl"]),
            )

        for item in inventory:
            conn.execute(
                "INSERT OR IGNORE INTO inventory (maSP, tenSP, danhMuc, donViTinh, tonKho, trangThai, capNhatGanNhat) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (item["maSP"], item["tenSP"], item["danhMuc"], item["donViTinh"], item["tonKho"], item["trangThai"], item["capNhatGanNhat"]),
            )

        for item in payments:
            conn.execute(
                "INSERT OR IGNORE INTO payments (maTT, maDH, khachHang, tongTien, phuongThuc, trangThai, ngayTT) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (item["maTT"], item["maDH"], item["khachHang"], item["tongTien"], item["phuongThuc"], item["trangThai"], item["ngayTT"]),
            )

        conn.commit()

    def get_categories(self):
        with self.get_connection() as conn:
            rows = conn.execute("SELECT maDM, tenDM, moTa, sl FROM categories ORDER BY maDM").fetchall()
            return [dict(row) for row in rows]

    def add_category(self, category):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO categories (maDM, tenDM, moTa, sl) VALUES (?, ?, ?, ?)",
                (category.get("maDM", ""), category.get("tenDM", ""), category.get("moTa", ""), category.get("sl", 0)),
            )
            conn.commit()

    def update_category(self, category):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE categories SET tenDM = ?, moTa = ?, sl = ? WHERE maDM = ?",
                (category.get("tenDM", ""), category.get("moTa", ""), category.get("sl", 0), category.get("maDM", "")),
            )
            conn.commit()

    def delete_category(self, maDM):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM categories WHERE maDM = ?", (maDM,))
            conn.commit()

    def get_inventory_items(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT maSP, tenSP, danhMuc, donViTinh, tonKho, trangThai, capNhatGanNhat FROM inventory ORDER BY maSP"
            ).fetchall()
            items = [dict(row) for row in rows]
            for item in items:
                history = conn.execute(
                    "SELECT ngay, loai, soLuong, nhanVien, ghiChu FROM inventory_history WHERE maSP = ? ORDER BY id",
                    (item["maSP"],),
                ).fetchall()
                item["history"] = [dict(h) for h in history]
            return items

    def update_inventory_item(self, item):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE inventory SET tenSP = ?, danhMuc = ?, donViTinh = ?, tonKho = ?, trangThai = ?, capNhatGanNhat = ? WHERE maSP = ?",
                (item.get("tenSP", ""), item.get("danhMuc", ""), item.get("donViTinh", ""), item.get("tonKho", 0), item.get("trangThai", ""), item.get("capNhatGanNhat", ""), item.get("maSP", "")),
            )
            conn.commit()

    def add_inventory_history(self, maSP, entry):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO inventory_history (maSP, ngay, loai, soLuong, nhanVien, ghiChu) VALUES (?, ?, ?, ?, ?, ?)",
                (maSP, entry.get("ngay", ""), entry.get("loai", ""), entry.get("soLuong", 0), entry.get("nhanVien", ""), entry.get("ghiChu", "")),
            )
            conn.commit()

    def get_payments(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT maTT, maDH, khachHang, tongTien, phuongThuc, trangThai, ngayTT FROM payments ORDER BY maTT"
            ).fetchall()
            return [dict(row) for row in rows]

    def update_payment(self, payment):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE payments SET maDH = ?, khachHang = ?, tongTien = ?, phuongThuc = ?, trangThai = ?, ngayTT = ? WHERE maTT = ?",
                (payment.get("maDH", ""), payment.get("khachHang", ""), payment.get("tongTien", 0), payment.get("phuongThuc", ""), payment.get("trangThai", ""), payment.get("ngayTT", ""), payment.get("maTT", "")),
            )
            conn.commit()

    def delete_payment(self, maTT):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM payments WHERE maTT = ?", (maTT,))
            conn.commit()
