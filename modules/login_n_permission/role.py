from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


SIDEBAR_BUTTONS = (
    "btnTongQuan",
    "btnDonhang",
    "btnKhachHang",
    "btnSanPham",
    "btnDanhMuc",
    "btnTonKho",
    "btnThanhToan",
    "btnVanChuyen",
    "btnDoiTac",
    "btnNhanVien",
    "btnBaoCao",
    "btnDangXuat",
)

ROLE_KEYWORDS = {
    "admin": ("admin", "quản trị", "quan tri", "system administrator"),
    "sales": ("bán hàng", "ban hang", "xử lý đơn hàng", "xu ly don hang", "sales"),
    "product_manager": ("quản lý sản phẩm", "quan ly san pham", "product manager"),
    "warehouse": ("kho", "warehouse"),
    "shipping": ("giao hàng", "giao hang", "dispatch", "shipping"),
    "accountant": ("kế toán", "ke toan", "accountant"),
    "customer_service": ("chăm sóc khách hàng", "cham soc khach hang", "cskh", "customer service"),
}


@dataclass(frozen=True)
class RolePolicy:
    visible_sidebar_buttons: tuple[str, ...]
    blocked_pages: tuple[str, ...] = ()
    view_only_pages: tuple[str, ...] = ()
    managed_pages: tuple[str, ...] = ()


ROLE_POLICIES = {
    "admin": RolePolicy(
        visible_sidebar_buttons=SIDEBAR_BUTTONS,
        managed_pages=(
            "pageTongQuan",
            "pageDonHang",
            "pageKhachHang",
            "pageSanPham",
            "pageDanhMuc",
            "pageTonKho",
            "pageThanhToan",
            "pageVanChuyen",
            "pageDoiTacVC",
            "pageNhanVien",
            "pageBaoCao",
        ),
    ),
    "sales": RolePolicy(
        visible_sidebar_buttons=(
            "btnTongQuan",
            "btnDonhang",
            "btnKhachHang",
            "btnSanPham",
            "btnTonKho",
            "btnVanChuyen",
            "btnDangXuat",
        ),
        managed_pages=("pageDonHang", "pageKhachHang"),
        view_only_pages=("pageTongQuan", "pageSanPham", "pageTonKho", "pageVanChuyen"),
        blocked_pages=("pageDanhMuc", "pageThanhToan", "pageDoiTacVC", "pageNhanVien", "pageBaoCao"),
    ),
    "product_manager": RolePolicy(
        visible_sidebar_buttons=(
            "btnTongQuan",
            "btnSanPham",
            "btnDanhMuc",
            "btnTonKho",
            "btnDoiTac",
            "btnNhanVien",
            "btnBaoCao",
            "btnDangXuat",
        ),
        managed_pages=("pageSanPham", "pageDanhMuc"),
        view_only_pages=("pageTongQuan", "pageTonKho", "pageDoiTacVC", "pageNhanVien", "pageBaoCao"),
        blocked_pages=("pageDonHang", "pageKhachHang", "pageThanhToan", "pageVanChuyen"),
    ),

    "warehouse": RolePolicy(
        visible_sidebar_buttons=(
            "btnTongQuan",
            "btnDonhang",
            "btnSanPham",
            "btnTonKho",
            "btnVanChuyen",
            "btnDoiTac",
            "btnDangXuat",
        ),
        managed_pages=(
            "pageTonKho",
            "pageVanChuyen",
            "pageDoiTacVC",
        ),
        view_only_pages=(
            "pageTongQuan",
            "pageDonHang",
            "pageSanPham",
        ),
        blocked_pages=(
            "pageKhachHang",
            "pageDanhMuc",
            "pageThanhToan",
            "pageNhanVien",
            "pageBaoCao",
        ),
    ),

    "shipping": RolePolicy(
        visible_sidebar_buttons=("btnTongQuan", "btnDonhang", "btnVanChuyen", "btnDangXuat"),
        managed_pages=("pageVanChuyen",),
        view_only_pages=("pageTongQuan", "pageDonHang"),
        blocked_pages=("pageKhachHang", "pageSanPham", "pageDanhMuc", "pageTonKho", "pageThanhToan", "pageDoiTacVC", "pageNhanVien", "pageBaoCao"),
    ),
    "accountant": RolePolicy(
        visible_sidebar_buttons=("btnTongQuan", "btnThanhToan", "btnDoiTac", "btnBaoCao", "btnDangXuat"),
        managed_pages=("pageThanhToan",),
        view_only_pages=("pageTongQuan", "pageDoiTacVC", "pageBaoCao"),
        blocked_pages=("pageDonHang", "pageKhachHang", "pageSanPham", "pageDanhMuc", "pageTonKho", "pageVanChuyen", "pageNhanVien"),
    ),
    "customer_service": RolePolicy(
        visible_sidebar_buttons=("btnTongQuan", "btnDonhang", "btnKhachHang", "btnBaoCao", "btnDangXuat"),
        managed_pages=("pageKhachHang",),
        view_only_pages=("pageTongQuan", "pageDonHang", "pageBaoCao"),
        blocked_pages=("pageSanPham", "pageDanhMuc", "pageTonKho", "pageThanhToan", "pageVanChuyen", "pageDoiTacVC", "pageNhanVien"),
    ),
}


PAGE_MODE_BUTTONS = {
    "pageDonHang": ("btnThemDH", "btnCapNhatDH", "btnXoaDH", "btnTimKiemDH", "btnRefreshDH"),
    "pageKhachHang": ("btnThemKH", "btnChiTietKH", "btnCapNhatKH", "btnXoaKH", "btnTimKiemKH", "btnRefreshKH"),
    "pageSanPham": ("btnThemSP", "btnChiTietSP", "btnCapNhatSP", "btnXoaSP", "btnTimKiemSP", "btnRefreshSP"),
    "pageDanhMuc": ("btnThemDM", "btnChiTietDM", "btnCapNhatDM", "btnXoaDM", "btnTimKiemDM", "btnRefreshDM"),
    "pageTonKho": ("btnChiTietTK", "btnCapNhatTK", "btnRefreshTK", "btnTimKiemTK"),
    "pageThanhToan": ("btnChiTietTT", "btnXacNhanTT", "btnXoaTT", "btnRefreshTT", "btnTimKiemTT"),
    "pageVanChuyen": ("btnChiTietVC", "btnCapNhatVC", "btnRefreshVC", "btnTimKiemVC"),
    "pageDoiTacVC": ("btnThemDT", "btnChiTietDT", "btnCapNhatDT", "btnXoaDT", "btnTimKiemDT", "btnRefreshDT"),
    "pageNhanVien": ("btnThemNV", "btnChiTietNV", "btnCapNhatNV", "btnXoaNV", "btnTimKiemNV", "btnRefreshNV"),
    "pageBaoCao": ("btnXemBaoCao", "btnRefreshBC"),
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def resolve_role_key(user_info: Mapping[str, Any] | None) -> str:
    if not user_info:
        return "admin"

    role_id = user_info.get("role_id")
    role_name = _normalize_text(user_info.get("role_name"))
    position = _normalize_text(user_info.get("position"))
    department = _normalize_text(user_info.get("department"))

    text = " ".join(part for part in (role_name, position, department) if part)

    if role_id == 1 or any(keyword in text for keyword in ROLE_KEYWORDS["admin"]):
        return "admin"
    if any(keyword in text for keyword in ROLE_KEYWORDS["product_manager"]):
        return "product_manager"
    if role_id == 2 or any(keyword in text for keyword in ROLE_KEYWORDS["sales"]):
        return "sales"
    if role_id == 3 or any(keyword in text for keyword in ROLE_KEYWORDS["warehouse"]):
        return "warehouse"
    if role_id == 4 or any(keyword in text for keyword in ROLE_KEYWORDS["shipping"]):
        return "shipping"
    if role_id == 5 or any(keyword in text for keyword in ROLE_KEYWORDS["accountant"]):
        return "accountant"
    if role_id == 6 or any(keyword in text for keyword in ROLE_KEYWORDS["customer_service"]):
        return "customer_service"

    return "admin"


def _get_widget(window: Any, name: str) -> Any:
    return getattr(window, name, None)


def _set_widgets_visible(window: Any, widget_names: tuple[str, ...], visible: bool) -> None:
    for name in widget_names:
        widget = _get_widget(window, name)
        if widget is not None:
            widget.setVisible(visible)
            widget.setEnabled(visible)


def _set_page_enabled(window: Any, page_name: str, enabled: bool) -> None:
    page = _get_widget(window, page_name)
    if page is not None:
        page.setEnabled(enabled)


def _set_page_button_state(window: Any, page_name: str, enabled: bool) -> None:
    for name in PAGE_MODE_BUTTONS.get(page_name, ()):
        widget = _get_widget(window, name)
        if widget is not None:
            widget.setEnabled(enabled)


def _disable_action_buttons_by_default(window: Any, page_name: str) -> None:
    for name in PAGE_MODE_BUTTONS.get(page_name, ()):
        widget = _get_widget(window, name)
        if widget is None:
            continue
        if any(token in name for token in ("Them", "CapNhat", "Xoa", "XacNhan")):
            widget.setEnabled(False)
        else:
            widget.setEnabled(True)


class RolePermissionManager:
    def apply(self, window: Any, user_info: Mapping[str, Any] | None) -> str:
        role_key = resolve_role_key(user_info)
        policy = ROLE_POLICIES.get(role_key, ROLE_POLICIES["admin"])

        _set_widgets_visible(window, SIDEBAR_BUTTONS, False)
        _set_widgets_visible(window, policy.visible_sidebar_buttons, True)

        page_names = set()
        for role_policy in ROLE_POLICIES.values():
            page_names.update(role_policy.managed_pages)
            page_names.update(role_policy.view_only_pages)
            page_names.update(role_policy.blocked_pages)

        for page_name in page_names:
            if page_name in policy.blocked_pages:
                _set_page_enabled(window, page_name, False)
                _set_page_button_state(window, page_name, False)
                continue

            if page_name in policy.managed_pages:
                _set_page_enabled(window, page_name, True)
                _set_page_button_state(window, page_name, True)
                continue

            if page_name in policy.view_only_pages:
                _set_page_enabled(window, page_name, True)
                _disable_action_buttons_by_default(window, page_name)

        return role_key