# Point Trace

Overlay trong suốt ghi lại và hiển thị điểm chuột xuyên ứng dụng trên Windows.

## Cài đặt

```bash
pip install -r requirements.txt
```

> **Lưu ý:** Trên Windows cần chạy với quyền **Administrator** để hook chuột toàn hệ thống.

## Chạy

```bash
python src/main.py
```

## Phím tắt

| Phím | Chức năng |
|------|-----------|
| Click trái chuột | Thêm điểm tại vị trí con trỏ |
| `Ctrl + Z` | Xóa điểm cuối (undo) |
| `C` | Xóa toàn bộ điểm |
| `Ctrl + S` | Lưu điểm ra `points.json` |
| `Esc` | Thoát chương trình |

Ngoài ra có thể dùng **menu system tray** (icon đỏ góc phải taskbar) để:
- Bật/tắt đường nối giữa các điểm
- Ẩn/hiện overlay
- Lưu / Load điểm từ file

## Cấu trúc dự án

```
point-trace/
├── docs/
│   └── idea.md
├── src/
│   ├── main.py        # Entry point, tray icon, kết nối signals
│   ├── overlay.py     # Cửa sổ trong suốt, click-through, vẽ điểm
│   ├── listener.py    # Lắng nghe chuột + bàn phím toàn hệ thống
│   └── store.py       # Quản lý danh sách điểm, lưu/load JSON
├── requirements.txt
└── README.md
```

## Lưu ý DPI Scaling

Chương trình tự bật **Per-Monitor DPI Awareness** để tọa độ Qt khớp với pynput.  
Nếu màn hình đặt scale 125%/150%, điểm vẫn hiển thị đúng vị trí.
