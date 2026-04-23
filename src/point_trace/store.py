"""
store.py — Quản lý danh sách điểm: thêm, xóa, undo, lưu/load JSON.
"""

import json
from typing import List, Tuple


class PointStore:
    def __init__(self) -> None:
        self._points: List[Tuple[int, int]] = []

    # ------------------------------------------------------------------ #
    #  Thao tác điểm                                                       #
    # ------------------------------------------------------------------ #

    def add(self, x: int, y: int) -> None:
        self._points.append((x, y))

    def undo(self) -> None:
        if self._points:
            self._points.pop()

    def clear(self) -> None:
        self._points.clear()

    def get_points(self) -> List[Tuple[int, int]]:
        return list(self._points)

    def __len__(self) -> int:
        return len(self._points)

    # ------------------------------------------------------------------ #
    #  Lưu / Load                                                          #
    # ------------------------------------------------------------------ #

    def save(self, path: str = "points.json") -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._points, f, indent=2)
        print(f"[store] Đã lưu {len(self._points)} điểm → {path}")

    def load(self, path: str = "points.json") -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._points = [tuple(p) for p in data]
            print(f"[store] Đã load {len(self._points)} điểm ← {path}")
        except FileNotFoundError:
            print(f"[store] Không tìm thấy file {path}")
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"[store] Lỗi đọc file: {exc}")
