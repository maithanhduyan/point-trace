# Point Trace

> Transparent always-on-top overlay to pin & trace points across any Windows application — works with SketchUp, Chrome, CAD tools, and more.

---

## Tính năng

- Ghim điểm tại vị trí con trỏ bằng phím tắt — **không gây nhiễu** ứng dụng bên dưới
- Overlay trong suốt, click-through, luôn nổi trên cùng
- Bật/tắt overlay khi cần (ẩn đi để dùng app bình thường, bật lại để tiếp tục trace)
- Vẽ đường nối giữa các điểm
- Đánh số thứ tự từng điểm
- Lưu / Load danh sách điểm ra file JSON
- Undo từng điểm
- Tất cả phím tắt **có thể tùy chỉnh** trong `config.toml`
- Hỗ trợ DPI scaling (125%, 150%, v.v.)

---

## Yêu cầu

- Windows 10/11
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (trình quản lý package)

---

## Cài đặt

```powershell
# 1. Clone repo
git clone https://github.com/your-username/point-trace.git
cd point-trace

# 2. Cài dependencies
uv sync
```

---

## Chạy

```powershell
uv run point-trace
```

> **Lưu ý:** Nên chạy với quyền **Administrator** để hook bàn phím toàn hệ thống hoạt động ổn định.
> Click phải vào PowerShell → *Run as Administrator*, sau đó chạy lệnh trên.

Sau khi khởi động, icon đỏ xuất hiện ở **system tray** (góc phải taskbar).

---

## Hướng dẫn sử dụng

### Workflow cơ bản

```
[Bật overlay] → Đặt con trỏ vào điểm cần đánh dấu → Ctrl+D
             → Đặt điểm tiếp theo → Ctrl+D → ...
             → [Ẩn overlay khi cần vẽ tự do] → Ctrl+Shift+Space
             → [Bật lại] → Ctrl+Shift+Space
             → Lưu → Ctrl+Shift+S
```

### Hai chế độ hoạt động

| Trạng thái | Mô tả | Phím có tác dụng |
|---|---|---|
| **Overlay hiện** | Đang trace điểm | Tất cả hotkey |
| **Overlay ẩn** | Dùng app bình thường (vẽ, thiết kế...) | Chỉ `Ctrl+Shift+Space` để bật lại |

Khi overlay ẩn, **mọi phím tắt** (`Ctrl+Z`, `Ctrl+D`, v.v.) được trả lại hoàn toàn cho ứng dụng bên dưới.

---

## Phím tắt

| Tổ hợp phím | Chức năng |
|---|---|
| `Ctrl + D` | Thêm điểm tại vị trí con trỏ chuột |
| `Ctrl + Shift + Space` | Bật / tắt overlay |
| `Ctrl + Shift + O` | Bật / tắt đường nối giữa các điểm |
| `Ctrl + Z` | Xóa điểm cuối (undo) |
| `Ctrl + Shift + C` | Xóa toàn bộ điểm |
| `Ctrl + Shift + S` | Lưu điểm ra `points.json` |
| `Esc` | Thoát chương trình |

Tất cả phím tắt có thể đổi trong file `config.toml`.

---

## System Tray Menu

Click phải vào icon đỏ ở taskbar để truy cập:

- **Bật/tắt đường nối** — ẩn/hiện đường cam nối các điểm
- **Ẩn/hiện overlay** — tương đương `Ctrl+Shift+Space`
- **Lưu điểm** — lưu ra `points.json`
- **Load điểm** — load lại từ `points.json`
- **Xóa hết** — xóa tất cả điểm
- **Thoát**

---

## Tùy chỉnh phím tắt

Chỉnh sửa file `config.toml` ở thư mục gốc:

```toml
[hotkeys]
add_point       = ["ctrl", "d"]
toggle_overlay  = ["ctrl", "shift", "space"]
toggle_lines    = ["ctrl", "shift", "o"]
undo            = ["ctrl", "z"]
clear           = ["ctrl", "shift", "c"]
save            = ["ctrl", "shift", "s"]
quit            = ["esc"]
```

Modifier hợp lệ: `ctrl`, `shift`, `alt`  
Phím thường: chữ thường `a`–`z`, `space`, `esc`, `enter`, `f1`–`f12`, v.v.

Thay đổi có hiệu lực ngay lần khởi động tiếp theo.

---

## Cấu trúc dự án

```
point-trace/
├── config.toml              ← cấu hình phím tắt
├── pyproject.toml           ← metadata & dependencies
├── docs/
│   └── idea.md
└── src/
    └── point_trace/
        ├── main.py          ← entry point, system tray
        ├── overlay.py       ← cửa sổ trong suốt, vẽ điểm
        ├── listener.py      ← hook bàn phím toàn hệ thống
        ├── store.py         ← quản lý điểm, lưu/load JSON
        └── config.py        ← đọc & parse config.toml
```

---

## Lưu ý

- **DPI Scaling:** Chương trình tự bật Per-Monitor DPI Awareness — điểm hiển thị đúng vị trí kể cả khi màn hình đặt 125%/150%.
- **Game / GPU apps:** Một số ứng dụng dùng exclusive fullscreen có thể che mất overlay.
- **UAC dialogs:** Hook bàn phím không hoạt động trên cửa sổ UAC (hành vi bảo mật của Windows).

---

## License

MIT
