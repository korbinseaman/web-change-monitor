---
name: web-change-monitor
description: 网页变化监控 - 定期轮询检测网页内容变化。当用户需要监控价格变化、公告更新、信息公开网站数据变化时使用此技能。支持多目标监控、自定义选择器、定时轮询、变化检测。
---

# Web Change Monitor - 网页变化监控

监控网页内容变化，支持价格跟踪、公告更新、数据变化检测。

## 何时使用

**使用此技能当：**
- 需要监控电商网站价格变化（淘宝、京东、拼多多等）
- 需要跟踪政府公告、学校通知等信息更新
- 需要监控多个网页的数据变化
- 需要定时轮询并检测内容变化

**不要使用此技能：**
- 只需一次性抓取网页（使用 `web_fetch` 或 `browser`）
- 需要截图或复杂浏览器自动化（使用 `browser`）

## 核心功能

### 1. 多目标监控
支持同时监控多个 URL，每个目标可独立配置：
- URL（必填）
- CSS 选择器或 XPath
- 搜索关键词
- 自定义请求头和参数
- 独立轮询间隔

### 2. 灵活提取
- **CSS 选择器** - 精准提取页面元素
- **XPath** - 复杂结构提取
- **关键词搜索** - 在页面中搜索特定文本
- **智能提取** - 自动识别主要内容区域

### 3. 变化检测
- **SHA256 哈希比对** - 精确检测内容变化
- **差异高亮** - 显示具体变化内容
- **历史记录** - 保存每次抓取结果

### 4. 定时轮询
- **可配置间隔** - 全局或独立设置（最小 10 秒）
- **后台运行** - 不阻塞主会话
- **智能通知** - 仅变化时返回（可配置）

## 输入参数

### targets (必填)
监控目标列表，每个目标包含：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | str | ✅ | 完整 URL |
| `selector` | str | ❌ | CSS 选择器（如 `.price`） |
| `xpath` | str | ❌ | XPath 表达式（优先级高于 selector） |
| `keyword` | str | ❌ | 页面内搜索关键词 |
| `headers` | dict | ❌ | 自定义 HTTP 头 |
| `method` | str | ❌ | HTTP 方法（默认 GET） |
| `payload` | dict | ❌ | POST 请求体 |
| `interval` | int | ❌ | 独立轮询间隔（秒） |

### interval (可选)
全局轮询间隔（秒），默认 30，最小建议值 10。

### return_on_change_only (可选)
是否仅在变化时返回，默认 `true`。

## 输出格式

```json
{
  "results": [
    {
      "url": "https://example.com/product",
      "timestamp": "2026-03-16T00:30:00+08:00",
      "content": "¥3499.00",
      "changed": true,
      "hash": "a1b2c3d4e5f6...",
      "previous_hash": "x9y8z7w6v5u4..."
    }
  ]
}
```

## 使用示例

### 示例 1：监控商品价格

```json
{
  "targets": [
    {
      "url": "https://shop.example.com/item/1001",
      "selector": ".current-price"
    },
    {
      "url": "https://market.example.org/product?id=205",
      "xpath": "//div[@id='price']/span"
    }
  ],
  "interval": 60,
  "return_on_change_only": true
}
```

### 示例 2：监控学校通知

```json
{
  "targets": [
    {
      "url": "https://school.edu.cn/notice",
      "selector": "#notice-board",
      "keyword": "放假"
    }
  ],
  "return_on_change_only": false
}
```

### 示例 3：监控搜索结果

```json
{
  "targets": [
    {
      "url": "https://search.example.com",
      "method": "POST",
      "payload": {"q": "DJI Pocket 3"},
      "selector": ".result-item"
    }
  ],
  "interval": 300
}
```

## 脚本使用

### 启动监控
```bash
python scripts/monitor.py --config config.json
```

### 添加监控目标
```bash
python scripts/add_target.py --url "https://..." --selector ".price"
```

### 查看状态
```bash
python scripts/status.py
```

### 停止监控
```bash
python scripts/stop.py
```

## 数据存储

**配置：** `data/config.json`
**历史：** `data/history/<url_hash>.jsonl`
**缓存：** `data/cache/<url_hash>.html`

## 依赖

```bash
pip install requests beautifulsoup4 lxml
```

## 注意事项

1. **礼貌轮询** - 间隔不低于 10 秒，避免被封禁
2. **robots.txt** - 遵守目标网站的爬虫协议
3. **选择器稳定性** - 使用稳定的 class/id
4. **错误处理** - 网络异常不影响其他目标
5. **隐私合规** - 仅监控公开数据

## 相关文件

- `scripts/monitor.py` - 主监控程序
- `scripts/add_target.py` - 添加目标
- `scripts/status.py` - 查看状态
- `references/selectors.md` - 选择器指南
- `references/api.md` - API 文档
