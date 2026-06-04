#!/usr/bin/env python3
"""
万鸿科技 — 本地API服务器
支持: 图片上传, 订单管理, 收款设置
启动: python3 server.py
访问: http://localhost:8090
后台: http://localhost:8090/admin
"""

import http.server
import json
import os
import sys
import uuid
import shutil
import cgi
from datetime import datetime
from pathlib import Path
from io import BytesIO

PORT = 8090
ROOT = Path(__file__).parent.resolve()
DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "assets"
UPLOADS_DIR = ASSETS_DIR / "uploads"
PAYMENT_DIR = ASSETS_DIR / "payment"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
PAYMENT_DIR.mkdir(parents=True, exist_ok=True)

# ---- Data helpers ----
def read_json(path):
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)

def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def gen_id(prefix="ORD"):
    return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

# ---- API handlers ----
def handle_upload(form):
    """Handle image upload. Expects multipart form with 'file' field."""
    if 'file' not in form:
        return 400, {"error": "No file field"}

    file_item = form['file']
    if isinstance(file_item, list):
        file_item = file_item[0]

    filename = file_item.filename
    if not filename:
        return 400, {"error": "No filename"}

    # Generate safe filename
    ext = Path(filename).suffix.lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'):
        return 400, {"error": f"Unsupported format: {ext}"}

    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOADS_DIR / safe_name

    with open(dest, 'wb') as f:
        f.write(file_item.file.read())

    relative_path = f"assets/uploads/{safe_name}"
    return 200, {
        "success": True,
        "path": relative_path,
        "filename": safe_name,
        "url": "/" + relative_path
    }

def handle_get_orders():
    path = DATA_DIR / "orders.json"
    data = read_json(path) or {"orders": []}
    return 200, data

def handle_post_order(body):
    path = DATA_DIR / "orders.json"
    data = read_json(path) or {"orders": []}

    order = {
        "id": gen_id("ORD"),
        "customerName": body.get("customerName", ""),
        "company": body.get("company", ""),
        "phone": body.get("phone", ""),
        "email": body.get("email", ""),
        "address": body.get("address", ""),
        "productId": body.get("productId", ""),
        "productName": body.get("productName", ""),
        "quantity": body.get("quantity", 1),
        "totalAmount": body.get("totalAmount", 0),
        "message": body.get("message", ""),
        "status": "pending",
        "adminNotes": "",
        "createdAt": now_ts(),
        "read": False
    }

    data["orders"].insert(0, order)
    write_json(path, data)

    return 201, {"success": True, "order": order}

def handle_update_order(order_id, body):
    path = DATA_DIR / "orders.json"
    data = read_json(path)
    if not data:
        return 404, {"error": "No orders found"}

    for order in data["orders"]:
        if order["id"] == order_id:
            if "status" in body:
                order["status"] = body["status"]
            if "adminNotes" in body:
                order["adminNotes"] = body["adminNotes"]
            if "read" in body:
                order["read"] = body["read"]
            write_json(path, data)
            return 200, {"success": True, "order": order}

    return 404, {"error": f"Order {order_id} not found"}

def handle_get_payment():
    path = DATA_DIR / "payment.json"
    data = read_json(path) or {
        "bank": {"enabled": False, "accountName": "", "accountNumber": "", "bankName": ""},
        "wechat": {"enabled": False, "qrImage": ""},
        "alipay": {"enabled": False, "qrImage": ""}
    }
    return 200, data

def handle_save_payment(body):
    path = DATA_DIR / "payment.json"
    write_json(path, body)
    return 200, {"success": True}

def handle_save_settings(body):
    """Save settings to products.json's settings section"""
    path = DATA_DIR / "products.json"
    data = read_json(path)
    if not data:
        return 404, {"error": "products.json not found"}

    data["settings"] = body
    write_json(path, data)
    return 200, {"success": True}

def handle_save_products(body):
    """Save full products + settings to products.json"""
    path = DATA_DIR / "products.json"
    data = {"products": body.get("products", []), "settings": body.get("settings", {})}
    write_json(path, data)
    return 200, {"success": True}

def safe_read_json(rfile, content_len):
    """Safely parse JSON body, returning {} on error"""
    if content_len <= 0:
        return {}
    try:
        return json.loads(rfile.read(content_len))
    except (json.JSONDecodeError, Exception):
        return {}

class APIHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with API endpoints + static file serving."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _api_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        if self.path == '/api/upload':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']}
            )
            status, data = handle_upload(form)
            self._api_response(status, data)
        elif self.path == '/api/orders':
            content_len = int(self.headers.get('Content-Length', 0))
            body = safe_read_json(self.rfile, content_len)
            status, data = handle_post_order(body)
            self._api_response(status, data)
        elif self.path == '/api/payment':
            content_len = int(self.headers.get('Content-Length', 0))
            body = safe_read_json(self.rfile, content_len)
            status, data = handle_save_payment(body)
            self._api_response(status, data)
        elif self.path == '/api/settings':
            content_len = int(self.headers.get('Content-Length', 0))
            body = safe_read_json(self.rfile, content_len)
            status, data = handle_save_settings(body)
            self._api_response(status, data)
        elif self.path == '/api/save-products':
            content_len = int(self.headers.get('Content-Length', 0))
            body = safe_read_json(self.rfile, content_len)
            status, data = handle_save_products(body)
            self._api_response(status, data)
        else:
            super().do_POST()

    def do_PUT(self):
        if self.path.startswith('/api/orders/'):
            order_id = self.path.split('/api/orders/')[1]
            if not order_id:
                self.send_response(404)
                self.end_headers()
                return
            content_len = int(self.headers.get('Content-Length', 0))
            body = safe_read_json(self.rfile, content_len)
            status, data = handle_update_order(order_id, body)
            self._api_response(status, data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/api/orders':
            status, data = handle_get_orders()
            self._api_response(status, data)
        elif self.path == '/api/payment':
            status, data = handle_get_payment()
            self._api_response(status, data)
        elif self.path.startswith('/api/orders/'):
            status, data = handle_get_orders()
            self._api_response(status, data)
        elif self.path == '/api/upload-list':
            files = []
            for d in [UPLOADS_DIR, PAYMENT_DIR]:
                if d.exists():
                    for f in sorted(d.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:50]:
                        if f.suffix.lower() in ('.jpg','.jpeg','.png','.gif','.webp','.svg'):
                            rel = str(f.relative_to(ROOT))
                            files.append({"name": f.name, "path": rel, "url": "/"+rel})
            self._api_response(200, {"files": files})
        else:
            # Serve static files
            super().do_GET()

    def log_message(self, format, *args):
        # Cleaner logging
        timestamp = datetime.now().strftime("%H:%M:%S")
        path = args[0] if args else ''
        if '/api/' in path:
            sys.stdout.write(f"[{timestamp}] API {args[0]} {args[1]} {args[2]}\n")
        else:
            sys.stdout.write(f"[{timestamp}] GET {args[0]}\n")

if __name__ == '__main__':
    # Kill any existing server on the port
    os.chdir(ROOT)

    server = http.server.HTTPServer(('0.0.0.0', PORT), APIHandler)

    print(f"""
╔══════════════════════════════════════════════╗
║       惠州市万鸿科技有限公司 — 本地服务器       ║
╠══════════════════════════════════════════════╣
║  网站首页:  http://localhost:{PORT}              ║
║  后台管理:  http://localhost:{PORT}/admin        ║
║                                              ║
║  API 端点:                                    ║
║  POST /api/upload    图片上传                  ║
║  GET  /api/orders    查看订单                  ║
║  POST /api/orders    提交订单                  ║
║  PUT  /api/orders/:id 更新订单                 ║
║  GET  /api/payment   获取收款设置              ║
║  POST /api/payment   保存收款设置              ║
║  POST /api/settings  保存系统设置              ║
║                                              ║
║  按 Ctrl+C 停止服务器                          ║
╚══════════════════════════════════════════════╝
""")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已关闭")
        server.shutdown()
