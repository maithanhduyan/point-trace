"""
config.py — Đọc config.toml và trả về bộ hotkeys đã parse.

Mỗi hotkey là một frozenset các pynput Key / KeyCode để so sánh
với tập phím đang giữ (pressed set) trong listener.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from pynput import keyboard

# ── tomllib có sẵn từ Python 3.11, dùng tomli cho 3.10 ───────────────
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib          # type: ignore[no-redef]
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

# Vị trí mặc định của config file
# - PyInstaller bundle : next to .exe  (sys.executable.parent)
# - Chạy từ source     : project root  (__file__/../../../)
if getattr(sys, "frozen", False):
    _DEFAULT_CONFIG = Path(sys.executable).parent / "config.toml"
else:
    _DEFAULT_CONFIG = Path(__file__).parent.parent.parent / "config.toml"

# ── Ánh xạ tên chuỗi → pynput Key ────────────────────────────────────
_MODIFIER_MAP: dict[str, keyboard.Key] = {
    "ctrl":   keyboard.Key.ctrl,
    "shift":  keyboard.Key.shift,
    "alt":    keyboard.Key.alt,
    "space":  keyboard.Key.space,
    "esc":    keyboard.Key.esc,
    "enter":  keyboard.Key.enter,
    "tab":    keyboard.Key.tab,
    "up":     keyboard.Key.up,
    "down":   keyboard.Key.down,
    "left":   keyboard.Key.left,
    "right":  keyboard.Key.right,
    "f1":     keyboard.Key.f1,
    "f2":     keyboard.Key.f2,
    "f3":     keyboard.Key.f3,
    "f4":     keyboard.Key.f4,
    "f5":     keyboard.Key.f5,
    "f6":     keyboard.Key.f6,
    "f7":     keyboard.Key.f7,
    "f8":     keyboard.Key.f8,
    "f9":     keyboard.Key.f9,
    "f10":    keyboard.Key.f10,
    "f11":    keyboard.Key.f11,
    "f12":    keyboard.Key.f12,
}


def _parse_combo(parts: list[str]) -> frozenset:
    """Chuyển ['ctrl', 'shift', 'c'] → frozenset pynput keys."""
    result: set = set()
    for p in parts:
        p = p.lower().strip()
        if p in _MODIFIER_MAP:
            result.add(_MODIFIER_MAP[p])
        elif len(p) == 1:
            result.add(keyboard.KeyCode.from_char(p))
        else:
            raise ValueError(f"Tên phím không hợp lệ: '{p}'")
    return frozenset(result)


# ── Hotkeys mặc định (dùng khi không tìm thấy config.toml) ───────────
_DEFAULTS: dict[str, list[str]] = {
    "add_point":      ["ctrl", "d"],
    "add_isolated":   ["ctrl", "shift", "d"],
    "break_chain":    ["ctrl", "b"],
    "toggle_overlay": ["ctrl", "shift", "space"],
    "toggle_lines":   ["ctrl", "shift", "o"],
    "undo":           ["ctrl", "z"],
    "clear":          ["ctrl", "shift", "c"],
    "save":           ["ctrl", "shift", "s"],
    "quit":           ["esc"],
}


class HotkeyConfig:
    """Bộ hotkeys đã parse sẵn, dùng để so sánh trong listener."""

    def __init__(self, raw: dict[str, list[str]]) -> None:
        self._combos: dict[str, frozenset] = {}
        for action, parts in raw.items():
            try:
                self._combos[action] = _parse_combo(parts)
            except ValueError as exc:
                print(f"[config] Cảnh báo — bỏ qua hotkey '{action}': {exc}")

    def match(self, action: str, pressed: frozenset) -> bool:
        """Trả về True nếu tập phím đang giữ khớp với hotkey của action."""
        combo = self._combos.get(action)
        if combo is None or not combo:
            return False
        return combo.issubset(pressed)

    def describe(self, action: str) -> str:
        """Trả về chuỗi mô tả tổ hợp phím, ví dụ 'Ctrl+Shift+C'."""
        combo = self._combos.get(action, frozenset())
        parts = []
        for k in combo:
            if isinstance(k, keyboard.Key):
                parts.append(k.name.capitalize())
            elif isinstance(k, keyboard.KeyCode) and k.char:
                parts.append(k.char.upper())
        return "+".join(sorted(parts))


def load_config(path: Path | None = None) -> HotkeyConfig:
    """Đọc config.toml; fallback về defaults nếu file không tồn tại."""
    cfg_path = path or _DEFAULT_CONFIG
    raw: dict[str, Any] = {}

    if cfg_path.exists():
        try:
            with open(cfg_path, "rb") as f:
                raw = tomllib.load(f).get("hotkeys", {})
            print(f"[config] Đã load: {cfg_path}")
        except Exception as exc:
            print(f"[config] Lỗi đọc config, dùng mặc định: {exc}")
            raw = {}
    else:
        print(f"[config] Không tìm thấy {cfg_path}, dùng mặc định.")

    # Merge: ưu tiên file, fallback về default từng action
    merged = {action: raw.get(action, default) for action, default in _DEFAULTS.items()}
    return HotkeyConfig(merged)
