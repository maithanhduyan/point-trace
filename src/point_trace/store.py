"""
store.py — Quản lý điểm theo từng chuỗi (segment/chain).

Mô hình dữ liệu:
  _segments: List[List[Tuple[int,int]]]
  Mỗi segment là một chuỗi các điểm nối liền nhau.
  Điểm đơn lẻ = segment có đúng 1 phần tử.
  Segment cuối luôn là segment active (có thể rỗng).
"""

import json
from typing import List, Tuple


class PointStore:
    def __init__(self) -> None:
        # Luôn có ít nhất 1 segment (active, có thể rỗng)
        self._segments: List[List[Tuple[int, int]]] = [[]]

    # ------------------------------------------------------------------ #
    #  Helpers nội bộ                                                      #
    # ------------------------------------------------------------------ #

    def _active(self) -> List[Tuple[int, int]]:
        """Segment đang active (luôn là segment cuối)."""
        if not self._segments:
            self._segments.append([])
        return self._segments[-1]

    def _trim_empty_tail(self) -> None:
        """Xóa các empty segment ở cuối, giữ lại ít nhất 1."""
        while len(self._segments) > 1 and not self._segments[-1]:
            self._segments.pop()

    # ------------------------------------------------------------------ #
    #  Thao tác điểm                                                       #
    # ------------------------------------------------------------------ #

    def add_connected(self, x: int, y: int) -> None:
        """Thêm điểm vào chuỗi hiện tại (nối với điểm trước cùng chuỗi)."""
        self._active().append((x, y))

    def add_isolated(self, x: int, y: int) -> None:
        """Thêm điểm đơn lẻ — không nối với điểm nào, trước hay sau."""
        self._trim_empty_tail()
        self._segments.append([(x, y)])  # isolated point = segment riêng
        self._segments.append([])        # bắt đầu chuỗi mới sau điểm đơn

    def break_chain(self) -> None:
        """Ngắt chuỗi hiện tại. Ctrl+D tiếp theo bắt đầu chuỗi mới."""
        if self._active():               # chỉ tạo segment mới nếu chuỗi hiện có điểm
            self._segments.append([])

    def undo(self) -> None:
        """Xóa điểm cuối cùng (undo từng điểm)."""
        self._trim_empty_tail()
        if self._segments and self._segments[-1]:
            self._segments[-1].pop()
            if not self._segments[-1]:   # nếu segment rỗng thì xóa luôn
                self._segments.pop()
        if not self._segments:
            self._segments.append([])

    def clear(self) -> None:
        self._segments = [[]]

    # ------------------------------------------------------------------ #
    #  Truy vấn                                                            #
    # ------------------------------------------------------------------ #

    def get_segments(self) -> List[List[Tuple[int, int]]]:
        """Danh sách các segment có điểm (bỏ empty)."""
        return [list(s) for s in self._segments if s]

    def get_all_points(self) -> List[Tuple[int, int]]:
        """Tất cả điểm theo thứ tự thêm vào, dùng để đánh số thứ tự."""
        result: List[Tuple[int, int]] = []
        for seg in self._segments:
            result.extend(seg)
        return result

    def __len__(self) -> int:
        return sum(len(s) for s in self._segments)

    # ------------------------------------------------------------------ #
    #  Lưu / Load                                                          #
    # ------------------------------------------------------------------ #

    def save(self, path: str = "points.json") -> None:
        segments = self.get_segments()
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"segments": segments}, f, indent=2)
        n_chains = len(segments)
        print(f"[store] Đã lưu {len(self)} điểm ({n_chains} chuỗi) → {path}")

    def load(self, path: str = "points.json") -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Tương thích ngược: format cũ là flat list [[x,y], ...]
            if isinstance(data, list):
                self._segments = [[tuple(p) for p in data]]
            else:
                self._segments = [
                    [tuple(p) for p in seg]
                    for seg in data.get("segments", [])
                ]
            if not self._segments:
                self._segments = [[]]
            else:
                self._segments.append([])  # thêm active empty ở cuối
            print(f"[store] Đã load {len(self)} điểm ← {path}")
        except FileNotFoundError:
            print(f"[store] Không tìm thấy file {path}")
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"[store] Lỗi đọc file: {exc}")
