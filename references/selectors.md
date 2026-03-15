# 选择器参考指南

常用网站的 CSS 选择器和 XPath 表达式参考。

## 电商网站

### 淘宝/天猫
```css
/* 价格 */
.tb-price
.price
.emphasize

/* 标题 */
.tb-detail-h1
.item-title

/* 库存 */
.stock-status
```

### 京东
```css
/* 价格 */
.p-price .price
.summary-price

/* 标题 */
.sku-name

/* 促销 */
.promises
```

### 拼多多
```css
/* 价格 */
.price
.normal-price
```

## 政府信息公开

### 中央政府网站
```css
/* 最新公告 */
#content_list
.list-item

/* 标题 */
.article-title
```

### 教育部
```css
/* 通知列表 */
.list_news
.news_list
```

## 学校网站

### 通知公告
```css
#notice-board
.notice-list
.list-item
```

## 新闻网站

### 头条新闻
```css
/* 第一条新闻 */
.headline
.news-item:first-child
```

## XPath 示例

```xpath
//div[@class='price']
//span[contains(text(), '价格')]
//a[@class='title'][1]
```

## 使用建议

1. **优先使用 class/id** - 更稳定
2. **避免索引** - `:first-child` 可能变化
3. **测试选择器** - 在浏览器控制台验证
4. **备份方案** - 提供多个选择器
