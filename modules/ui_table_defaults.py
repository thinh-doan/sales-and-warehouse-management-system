from __future__ import annotations

from typing import Dict, Sequence

from PyQt6 import QtCore, QtWidgets


class _TableAutoSizer(QtCore.QObject):
    def __init__(self, app: QtWidgets.QApplication, column_weights: Dict[str, Sequence[float]] | None = None):
        super().__init__(app)
        self._app = app
        self._column_weights = column_weights or {}

    def eventFilter(self, watched, event):  # noqa: N802 - Qt callback name
        if isinstance(watched, QtWidgets.QWidget):
            if event.type() in (
                QtCore.QEvent.Type.Show,
                QtCore.QEvent.Type.Resize,
                QtCore.QEvent.Type.Polish,
                QtCore.QEvent.Type.LayoutRequest,
            ):
                self.apply_to_widget_tree(watched)
        return super().eventFilter(watched, event)

    def apply_to_widget_tree(self, widget: QtWidgets.QWidget) -> None:
        if isinstance(widget, (QtWidgets.QTableWidget, QtWidgets.QTableView)):
            self._apply_to_table(widget)

        for table in widget.findChildren((QtWidgets.QTableWidget, QtWidgets.QTableView)):
            self._apply_to_table(table)

    def _apply_to_table(self, table: QtWidgets.QAbstractItemView) -> None:
        table.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsMovable(False)
        header.setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self._hook_table_model(table)

        if hasattr(table, "setWordWrap"):
            table.setWordWrap(False)

        column_count = self._get_column_count(table)
        if column_count <= 0:
            return

        weights = self._resolve_weights(table, column_count)
        total_weight = sum(weights) or float(column_count)

        available_width = table.viewport().width()
        if available_width <= 0:
            return

        widths = []
        used_width = 0
        for index, weight in enumerate(weights):
            if index == column_count - 1:
                width = max(0, available_width - used_width)
            else:
                width = max(48, int(round(available_width * weight / total_weight)))
                used_width += width
            widths.append(width)

        difference = available_width - sum(widths)
        if widths and difference != 0:
            widths[-1] = max(0, widths[-1] + difference)

        for column_index, width in enumerate(widths):
            table.setColumnWidth(column_index, width)

    def _hook_table_model(self, table: QtWidgets.QAbstractItemView) -> None:
        if bool(table.property("_autoResizeHooked")):
            return

        model = table.model()
        if model is None:
            return

        table.setProperty("_autoResizeHooked", True)

        def refresh(*_args):
            self._apply_to_table(table)

        model.modelReset.connect(refresh)
        model.layoutChanged.connect(refresh)
        model.rowsInserted.connect(refresh)
        model.rowsRemoved.connect(refresh)
        model.columnsInserted.connect(refresh)
        model.columnsRemoved.connect(refresh)
        model.dataChanged.connect(refresh)

    def _get_column_count(self, table: QtWidgets.QAbstractItemView) -> int:
        if hasattr(table, "columnCount"):
            try:
                return int(table.columnCount())
            except Exception:
                pass

        model = table.model()
        if model is not None:
            return int(model.columnCount())
        return 0

    def _resolve_weights(self, table: QtWidgets.QAbstractItemView, column_count: int) -> list[float]:
        object_name = table.objectName()
        if object_name in self._column_weights:
            raw_weights = list(self._column_weights[object_name])
            if raw_weights:
                if len(raw_weights) < column_count:
                    raw_weights.extend([1.0] * (column_count - len(raw_weights)))
                return [max(1.0, float(value)) for value in raw_weights[:column_count]]

        labels: list[str] = []
        for column_index in range(column_count):
            label = ""
            if hasattr(table, "horizontalHeaderItem"):
                try:
                    item = table.horizontalHeaderItem(column_index)
                    if item is not None:
                        label = item.text().strip()
                except Exception:
                    label = ""

            if not label and table.model() is not None:
                try:
                    label = str(table.model().headerData(column_index, QtCore.Qt.Orientation.Horizontal) or "").strip()
                except Exception:
                    label = ""

            labels.append(label)

        return [self._heuristic_weight(label) for label in labels]

    @staticmethod
    def _heuristic_weight(label: str) -> float:
        text = label.lower()
        if not text:
            return 1.0

        if any(keyword in text for keyword in ("mã", "ma", "id", "code", "số lượng", "so luong", "sl")):
            return 0.8
        if any(keyword in text for keyword in ("ngày", "ngay", "date", "time", "thời gian")):
            return 0.95
        if any(keyword in text for keyword in ("trạng thái", "trang thai", "status", "loại", "loai")):
            return 0.9
        if any(keyword in text for keyword in ("tên", "ten", "name", "khách", "khach", "sản phẩm", "san pham")):
            return 1.4
        if any(keyword in text for keyword in ("địa chỉ", "dia chi", "mô tả", "mo ta", "description", "nội dung", "noi dung", "chi tiết", "chi tiet")):
            return 1.8

        return max(1.0, min(2.0, len(text) / 8.0))


_AUTO_SIZER: _TableAutoSizer | None = None


def install_table_auto_sizer(app: QtWidgets.QApplication, column_weights: Dict[str, Sequence[float]] | None = None) -> _TableAutoSizer:
    global _AUTO_SIZER

    if _AUTO_SIZER is None or _AUTO_SIZER.parent() is not app:
        _AUTO_SIZER = _TableAutoSizer(app, column_weights=column_weights)
        app.installEventFilter(_AUTO_SIZER)
    elif column_weights:
        _AUTO_SIZER._column_weights.update(column_weights)

    return _AUTO_SIZER


def apply_table_defaults(widget: QtWidgets.QWidget, column_weights: Dict[str, Sequence[float]] | None = None) -> None:
    app = QtWidgets.QApplication.instance()
    if app is None:
        return

    sizer = install_table_auto_sizer(app, column_weights=column_weights)
    sizer.apply_to_widget_tree(widget)