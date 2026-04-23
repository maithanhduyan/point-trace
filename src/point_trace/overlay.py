"""
overlay.py — Cửa sổ trong suốt, luôn nổi trên cùng, click-through.
Vẽ các điểm chuột và đường nối bằng PyQt5.
"""

from PyQt5 import QtWidgets, QtGui, QtCore

from point_trace.store import PointStore


# Màu sắc
COLOR_DOT      = QtGui.QColor(220, 30, 30, 230)   # đỏ đậm
COLOR_DOT_BORDER = QtGui.QColor(255, 255, 255, 180)
COLOR_LINE     = QtGui.QColor(255, 120, 0, 160)    # cam
COLOR_LABEL    = QtGui.QColor(255, 255, 255, 200)  # trắng

DOT_RADIUS = 5
LINE_WIDTH  = 2


class Overlay(QtWidgets.QWidget):
    def __init__(self, store: PointStore) -> None:
        super().__init__()
        self.store = store
        self.draw_lines = True

        # ── Cờ cửa sổ ──────────────────────────────────────────────────
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint       |
            QtCore.Qt.WindowStaysOnTopHint      |
            QtCore.Qt.Tool                       # không hiện trên taskbar
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)  # click-through

        self.showFullScreen()

    # ------------------------------------------------------------------ #
    #  Vẽ                                                                  #
    # ------------------------------------------------------------------ #

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        points = self.store.get_points()
        if not points:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # -- Đường nối ---------------------------------------------------
        if self.draw_lines and len(points) > 1:
            pen = QtGui.QPen(COLOR_LINE, LINE_WIDTH)
            pen.setStyle(QtCore.Qt.SolidLine)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.NoBrush)
            for i in range(len(points) - 1):
                painter.drawLine(
                    points[i][0],     points[i][1],
                    points[i + 1][0], points[i + 1][1],
                )

        # -- Chấm + số thứ tự -------------------------------------------
        font = QtGui.QFont("Segoe UI", 8, QtGui.QFont.Bold)
        painter.setFont(font)

        for idx, (x, y) in enumerate(points):
            # Viền trắng
            painter.setPen(QtGui.QPen(COLOR_DOT_BORDER, 1))
            painter.setBrush(QtGui.QBrush(COLOR_DOT))
            painter.drawEllipse(QtCore.QPoint(x, y), DOT_RADIUS, DOT_RADIUS)

            # Nhãn số
            painter.setPen(QtGui.QPen(COLOR_LABEL))
            painter.drawText(x + DOT_RADIUS + 3, y - DOT_RADIUS, str(idx + 1))

    # ------------------------------------------------------------------ #
    #  Slot công khai (gọi từ main thread qua signals)                    #
    # ------------------------------------------------------------------ #

    @QtCore.pyqtSlot(int, int)
    def add_point(self, x: int, y: int) -> None:
        self.store.add(x, y)
        self.update()

    @QtCore.pyqtSlot()
    def undo_point(self) -> None:
        self.store.undo()
        self.update()

    @QtCore.pyqtSlot()
    def clear_points(self) -> None:
        self.store.clear()
        self.update()

    @QtCore.pyqtSlot()
    def toggle_lines(self) -> None:
        self.draw_lines = not self.draw_lines
        self.update()
