"""
listener.py — Lắng nghe bàn phím toàn hệ thống (pynput).
Phát Qt signals để cập nhật UI an toàn từ luồng nền.
Tổ hợp phím được đọc từ config.toml (hoặc dùng mặc định).
"""

from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard, mouse

from point_trace.config import HotkeyConfig, load_config


class GlobalListener(QObject):
    """
    Theo dõi tập phím đang giữ và phát signal khi khớp hotkey.

    Tất cả hotkeys cấu hình trong config.toml, mặc định:
        Ctrl + D              → thêm điểm kết nối vào chuỗi hiện tại
        Ctrl + Shift + D      → thêm điểm đơn lẻ (không nối với điểm nào)
        Ctrl + B              → ngắt chuỗi hiện tại, Ctrl+D tiếp theo bắt đầu chuỗi mới
        Ctrl + Shift + Space  → bật/tắt overlay
        Ctrl + Shift + O      → bật/tắt đường nối
        Ctrl + Z              → undo điểm cuối
        Ctrl + Shift + C      → xóa toàn bộ điểm
        Ctrl + Shift + S      → lưu điểm ra file
        Esc                   → thoát chương trình
    """

    # Signals
    point_added            = pyqtSignal(int, int)  # Ctrl+D: kết nối
    isolated_point_added   = pyqtSignal(int, int)  # Ctrl+Shift+D: đơn lẻ
    break_chain_requested  = pyqtSignal()           # Ctrl+B: ngắt chuỗi
    toggle_overlay         = pyqtSignal()
    toggle_lines           = pyqtSignal()
    undo_requested         = pyqtSignal()
    clear_requested        = pyqtSignal()
    save_requested         = pyqtSignal()
    quit_requested         = pyqtSignal()

    def __init__(self, hotkeys: HotkeyConfig | None = None) -> None:
        super().__init__()
        self._hk = hotkeys or load_config()
        self._pressed: set = set()          # tập phím đang giữ
        self._active = True                 # False khi overlay ẩn
        self._mouse_ctrl = mouse.Controller()
        self._kb_listener: keyboard.Listener | None = None

    # ------------------------------------------------------------------ #
    #  Vòng đời                                                            #
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        self._kb_listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._kb_listener.start()

    def stop(self) -> None:
        if self._kb_listener:
            self._kb_listener.stop()
        self._pressed.clear()

    def set_active(self, active: bool) -> None:
        """Khi active=False (overlay ẩn), chỉ lắng nghe toggle_overlay."""
        self._active = active
        self._pressed.clear()   # xờ pressed set khi chuyển chế độ

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize(key) -> object:
        """Chuẩn hoá ctrl_l/ctrl_r → ctrl, shift_l/shift_r → shift, v.v.
        Đồng thời chuyển control chars (Ctrl+D = \\x04) về chữ thường ('d')
        để khớp với KeyCode được parse từ config."""
        _alias = {
            keyboard.Key.ctrl_l:  keyboard.Key.ctrl,
            keyboard.Key.ctrl_r:  keyboard.Key.ctrl,
            keyboard.Key.shift_l: keyboard.Key.shift,
            keyboard.Key.shift_r: keyboard.Key.shift,
            keyboard.Key.alt_l:   keyboard.Key.alt,
            keyboard.Key.alt_r:   keyboard.Key.alt,
        }
        key = _alias.get(key, key)

        # Ctrl+<letter> → pynput trả về KeyCode(char='\x01'..'\x1a')
        # Chuẩn hoá về chữ thường để khớp với config: '\x04' → 'd'
        if (
            isinstance(key, keyboard.KeyCode)
            and key.char is not None
            and len(key.char) == 1
            and 1 <= ord(key.char) <= 26
        ):
            return keyboard.KeyCode.from_char(chr(ord(key.char) + ord("a") - 1))

        return key

    # ------------------------------------------------------------------ #
    #  Callbacks (chạy trong luồng pynput)                               #
    # ------------------------------------------------------------------ #

    def _on_press(self, key) -> None:
        try:
            self._pressed.add(self._normalize(key))
            pressed = frozenset(self._pressed)

            # toggle_overlay luôn được xử lý dù overlay ẩn hay hiện
            if self._hk.match("toggle_overlay", pressed):
                self.toggle_overlay.emit()
                return

            # Các hotkey khác chỉ hoạt động khi overlay đang hiện
            if not self._active:
                return

            if self._hk.match("add_point", pressed):
                x, y = self._mouse_ctrl.position
                self.point_added.emit(int(x), int(y))
            elif self._hk.match("add_isolated", pressed):
                x, y = self._mouse_ctrl.position
                self.isolated_point_added.emit(int(x), int(y))
            elif self._hk.match("break_chain", pressed):
                self.break_chain_requested.emit()
            elif self._hk.match("toggle_lines", pressed):
                self.toggle_lines.emit()
            elif self._hk.match("undo", pressed):
                self.undo_requested.emit()
            elif self._hk.match("clear", pressed):
                self.clear_requested.emit()
            elif self._hk.match("save", pressed):
                self.save_requested.emit()
            elif self._hk.match("quit", pressed):
                self.quit_requested.emit()

        except Exception:
            pass

    def _on_release(self, key) -> None:
        try:
            self._pressed.discard(self._normalize(key))
        except Exception:
            pass
