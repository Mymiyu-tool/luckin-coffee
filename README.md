<p align="center">
  <img src="assets/icon.png" width="128" alt="Luckin Coffee">
</p>

<h1 align="center">Luckin Coffee · 瑞幸咖啡</h1>

<p align="center">查门店、看菜单、预览订单、下单、查单、取消——走本机 luckin CLI 的登录态。</p>

---

## 前置条件

这个包**不直接连瑞幸接口**，它调用你机器上的 `luckin` 命令行工具：

```bash
# 需要 ~/.local/bin/luckin 存在，并且已经登录
luckin --version
```

用一个 action 检查状态：

```json
{ "action": "status" }
```

## 安装

```bash
git clone https://github.com/miyu-packages/luckin-coffee.git
miyu pkg install ./luckin-coffee
```

装好后出现 `luckin_coffee` 工具。

## 用法

```jsonc
// 1. 找一个附近门店（先拿到 deptId）
{ "action": "store", "lat": 31.2304, "lon": 121.4737 }

// 2. 看这家店卖什么
{ "action": "menu", "dept_id": "123456", "keyword": "拿铁" }

// 3. 预览价格和优惠（不会下单）
{ "action": "order_preview", "dept_id": "123456", "products": ["PRODUCT_ID:SKU_CODE:1"] }

// 4. 确认后下单
{ "action": "order_create", "dept_id": "123456", "products": ["PRODUCT_ID:SKU_CODE:1"], "coupons": ["COUPON_CODE"] }

// 5. 查单 / 取消
{ "action": "order_detail", "order_id": "ORDER_ID" }
{ "action": "order_cancel", "order_id": "ORDER_ID" }
```

### 参数

| 参数 | 说明 |
|---|---|
| `action` | `store` / `menu` / `product` / `order_preview` / `order_create` / `order_detail` / `order_cancel` / `status` |
| `lat` `lon` | 门店查询的经纬度 |
| `store_name` | 按门店名过滤 |
| `dept_id` | 门店 id，来自 `store` 结果 |
| `keyword` | 菜单/商品关键词 |
| `products` | `productId:skuCode[:数量]` |
| `coupons` | 预览返回的优惠券 code |
| `order_id` | 订单 id |

## 安全提醒

- **`order_create` 会真的花钱**。先跑 `order_preview`，确认门店、商品、券、实付金额，再下单。
- 这个包不保存你的账号密码，只复用本地 CLI 的登录态。

## 许可

MIT © 2026 yxxbc
