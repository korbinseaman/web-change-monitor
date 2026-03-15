# Web Change Monitor 网页变化监控

监控网页内容变化，支持价格跟踪、公告更新、数据变化检测。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 添加监控目标

```bash
# 添加商品价格监控
python scripts/monitor.py --add '{
  "url": "https://shop.example.com/item/1001",
  "selector": ".price",
  "interval": 60
}'

# 添加多个目标
python scripts/monitor.py --add '{
  "url": "https://example.com/notice",
  "selector": "#notice-board"
}'
```

### 3. 启动监控

```bash
# 后台运行监控
python scripts/monitor.py --start

# 或只检查一次
python scripts/monitor.py --once
```

### 4. 查看状态

```bash
python scripts/monitor.py --status
```

### 5. 停止监控

```bash
python scripts/monitor.py --stop
```

## 功能特点

- ✅ **多目标监控** - 同时监控多个网页
- ✅ **灵活提取** - CSS 选择器、XPath、关键词搜索
- ✅ **变化检测** - SHA256 哈希比对
- ✅ **定时轮询** - 可配置间隔（最小 10 秒）
- ✅ **智能通知** - 仅变化时返回
- ✅ **历史记录** - 保存每次抓取结果

## 配置示例

编辑 `data/config.json`：

```json
{
  "targets": [
    {
      "url": "https://shop.example.com/item/1001",
      "selector": ".current-price",
      "interval": 60
    },
    {
      "url": "https://school.edu.cn/notice",
      "selector": "#notice-board",
      "keyword": "放假"
    }
  ],
  "interval": 30,
  "return_on_change_only": true
}
```

## 输出格式

```json
{
  "url": "https://shop.example.com/item/1001",
  "timestamp": "2026-03-16T00:30:00+08:00",
  "content": "¥3499.00",
  "changed": true,
  "hash": "a1b2c3d4e5f6...",
  "previous_hash": "x9y8z7w6v5u4..."
}
```

## 完整文档

- [SKILL.md](SKILL.md) - 技能详细说明
- [references/selectors.md](references/selectors.md) - 选择器指南
- [data/config.example.json](data/config.example.json) - 配置示例

## 许可证

MIT License
