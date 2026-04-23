"""
main.py — Điểm khởi động của Point Trace.

Chạy:
    uv run point-trace

Yêu cầu quyền admin trên Windows để hook chuột toàn hệ thống.
"""

import os
import sys

# ── Bật Per-Monitor DPI Awareness trước khi tạo QApplication ──────────
# Đảm bảo tọa độ Qt khớp với tọa độ pynput (đều dùng pixel vật lý).
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)   # Per-Monitor v1
except AttributeError:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from PyQt5 import QtWidgets, QtGui, QtCore

from point_trace.overlay  import Overlay
from point_trace.listener import GlobalListener
from point_trace.store    import PointStore


# ── Tạo icon tray bằng code (không cần file ảnh) ──────────────────────
def _make_tray_icon() -> QtGui.QIcon:
    px = QtGui.QPixmap(32, 32)
    px.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(px)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setBrush(QtGui.QBrush(QtGui.QColor(220, 30, 30)))
    painter.setPen(QtCore.Qt.NoPen)
    painter.drawEllipse(4, 4, 24, 24)
    painter.end()
    return QtGui.QIcon(px)


def main() -> None:
    # Tắt Qt auto-scaling để khớp với DPI awareness đã cài ở trên
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "0")

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)   # giữ chạy khi overlay ẩn

    # ── Các thành phần chính ──────────────────────────────────────────
    store   = PointStore()
    overlay = Overlay(store)
    listener = GlobalListener()

    # ── Kết nối signals → slots ───────────────────────────────────────
    listener.point_added.connect(overlay.add_point)
    listener.undo_requested.connect(overlay.undo_point)
    listener.clear_requested.connect(overlay.clear_points)
    listener.save_requested.connect(lambda: store.save())
    listener.toggle_lines.connect(overlay.toggle_lines)
    listener.quit_requested.connect(app.quit)

    def _toggle_overlay():
        if overlay.isVisible():
            overlay.hide()
            listener.set_active(False)
        else:
            overlay.showFullScreen()
            listener.set_active(True)

    listener.toggle_overlay.connect(_toggle_overlay)

    listener.start()

    # ── System Tray ───────────────────────────────────────────────────
    tray = QtWidgets.QSystemTrayIcon(_make_tray_icon(), parent=app)
    tray.setToolTip(
        "Point Trace đang chạy\n"
        "Ctrl+D: Thêm điểm  |  Ctrl+Shift+Space: Bật/tắt overlay\n"
        "Ctrl+Shift+O: Đường nối  |  Ctrl+Z: Undo\n"
        "Ctrl+Shift+C: Xóa hết  |  Ctrl+Shift+S: Lưu  |  Esc: Thoát"
    )

    menu = QtWidgets.QMenu()

    act_toggle_lines = menu.addAction("Bật/tắt đường nối  (Ctrl+Shift+O)")
    act_toggle_lines.triggered.connect(overlay.toggle_lines)

    act_toggle_vis = menu.addAction("Ẩn/hiện overlay  (Ctrl+Shift+Space)")
    act_toggle_vis.triggered.connect(_toggle_overlay)

    menu.addSeparator()

    act_save = menu.addAction("Lưu điểm  (Ctrl+Shift+S)")
    act_save.triggered.connect(lambda: store.save())

    act_load = menu.addAction("Load điểm")
    def _load_points():
        store.load()
        overlay.update()
    act_load.triggered.connect(_load_points)

    act_clear = menu.addAction("Xóa hết  (Ctrl+Shift+C)")
    act_clear.triggered.connect(overlay.clear_points)

    menu.addSeparator()

    act_quit = menu.addAction("Thoát (Esc)")
    act_quit.triggered.connect(app.quit)

    tray.setContextMenu(menu)
    tray.show()

    tray.showMessage(
        "Point Trace",
        "Ctrl+D: thêm điểm  |  Ctrl+Shift+Space: bật/tắt",
        QtWidgets.QSystemTrayIcon.Information,
        3000,
    )

    ret = app.exec_()
    listener.stop()
    sys.exit(ret)


if __name__ == "__main__":
    main()
