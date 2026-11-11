#!/usr/bin/env python3
# Description: Luckin Coffee via the local `luckin` CLI and its saved MCP token. Look up nearby stores, read a store menu, and preview/create/detail/cancel orders. Needs the luckin CLI at ~/.local/bin/luckin (already logged in).
# Display name: Luckin Coffee
# 显示名称: 瑞幸咖啡
# 描述: 查附近门店、看菜单、预览/下单/查单/取消，走本地 luckin CLI 的登录态
# Timeout: 90
# Parameters:
# {"type": "object", "properties": {
#   "action": {"type": "string", "enum": ["store", "menu", "product", "order_preview", "order_create", "order_detail", "order_cancel", "status"], "description": "What to do"},
#   "lat": {"type": "number", "description": "Latitude, for store lookup"},
#   "lon": {"type": "number", "description": "Longitude, for store lookup"},
#   "store_name": {"type": "string", "description": "Optional store name filter"},
#   "dept_id": {"type": "string", "description": "Store deptId from store lookup"},
#   "keyword": {"type": "string", "description": "Drink keyword filter for menu/product"},
#   "products": {"type": "array", "items": {"type": "string"}, "description": "Order items as productId:skuCode[:amount]"},
#   "coupons": {"type": "array", "items": {"type": "string"}, "description": "Coupon codes returned by order_preview"},
#   "order_id": {"type": "string", "description": "Order id for detail/cancel"}
# }, "required": ["action"]}
import json
import os
import shutil
import subprocess
import sys

ARGS = json.loads(os.environ.get("MIYU_ARGS_JSON", "{}"))
STATE_DIR = os.environ.get("MIYU_STATE_DIR") or os.path.expanduser("~/.luckin")
CACHE = os.path.join(STATE_DIR, "last_location.json")


def fail(msg, extra=None):
    out = {"ok": False, "error": msg}
    if extra:
        out.update(extra)
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(1)


def cli_path():
    p = os.path.expanduser("~/.local/bin/luckin")
    if os.access(p, os.X_OK):
        return p
    found = shutil.which("luckin")
    if found:
        return found
    fail("luckin CLI not found; expected ~/.local/bin/luckin")


def remember_location(lat, lon):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump({"lat": lat, "lon": lon}, f)
    except OSError:
        pass


def recall_location():
    try:
        with open(CACHE, encoding="utf-8") as f:
            d = json.load(f)
        return d.get("lat"), d.get("lon")
    except (OSError, ValueError):
        return None, None


def run(argv):
    exe = cli_path()
    try:
        p = subprocess.run(
            [exe] + argv,
            capture_output=True,
            text=True,
            timeout=80,
            env={**os.environ, "PATH": os.path.expanduser("~/.local/bin") + ":" + os.environ.get("PATH", "")},
        )
    except subprocess.TimeoutExpired:
        fail("luckin CLI timed out")
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    if p.returncode != 0 and not out:
        fail(err or f"luckin exited {p.returncode}", {"stderr": err})
    return out, err


def parse(text):
    """CLI prints JSON on success; pass it through, else wrap the text."""
    try:
        return json.loads(text)
    except ValueError:
        return {"raw": text}


action = (ARGS.get("action") or "").strip()
if not action:
    fail("action is required")

if action == "status":
    token = os.path.expanduser("~/.luckin/.env")
    exists = os.path.exists(token)
    cfg = os.path.expanduser("~/.luckin/config.json")
    print(json.dumps({
        "ok": exists,
        "cli": cli_path(),
        "token_env": exists,
        "config": os.path.exists(cfg),
    }, ensure_ascii=False))
    sys.exit(0)

if action == "store":
    lat, lon = ARGS.get("lat"), ARGS.get("lon")
    if lat is None or lon is None:
        lat, lon = recall_location()
    if lat is None or lon is None:
        fail("lat and lon are required for store lookup")
    lat = float(lat)
    lon = float(lon)
    remember_location(lat, lon)
    argv = ["store", str(lat), str(lon)]
    if ARGS.get("store_name"):
        argv.append(str(ARGS["store_name"]))
    out, err = run(argv)
    print(json.dumps(parse(out), ensure_ascii=False))

elif action in ("menu", "product"):
    dept = ARGS.get("dept_id")
    if not dept:
        fail("dept_id is required; get it from the store action")
    argv = [action, str(dept)]
    kw = ARGS.get("keyword")
    if kw:
        argv.extend(str(kw).split())
    out, err = run(argv)
    print(json.dumps(parse(out), ensure_ascii=False))

elif action in ("order_preview", "order_create"):
    dept = ARGS.get("dept_id")
    if not dept:
        fail("dept_id is required")
    sub = "preview" if action == "order_preview" else "create"
    argv = ["order", sub, str(dept)]
    for item in ARGS.get("products") or []:
        argv += ["-p", str(item)]
    if sub == "create":
        for c in ARGS.get("coupons") or []:
            argv += ["--coupon", str(c)]
        lat, lon = ARGS.get("lat"), ARGS.get("lon")
        if lat is None or lon is None:
            lat, lon = recall_location()
        if lat is not None and lon is not None:
            argv += ["--lat", str(lat), "--lng", str(lon)]
    out, err = run(argv)
    print(json.dumps(parse(out), ensure_ascii=False))

elif action in ("order_detail", "order_cancel"):
    oid = ARGS.get("order_id")
    if not oid:
        fail("order_id is required")
    out, err = run(["order", "detail" if action == "order_detail" else "cancel", str(oid)])
    print(json.dumps(parse(out), ensure_ascii=False))

else:
    fail(f"unknown action: {action}")
