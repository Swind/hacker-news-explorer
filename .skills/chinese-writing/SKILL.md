---
name: chinese-writing
description: Chinese report writing guide. Use when writing reports in Chinese, formatting Chinese output, or translating technical content.
---

# Chinese Report Writing Guide

## When to Use
- Before writing any report content
- When formatting Chinese output
- When translating technical terms

## Output Format

Reports use YAML frontmatter + Markdown content:

```yaml
---
story_id: 12345
hn_url: https://news.ycombinator.com/item?id=12345
title: "故事標題"
verdict: interesting  # Options: interesting, not_interesting, controversial, technical
created_at: 2026-02-02T14:30:00
---
```

## Report Structure

```markdown
# {日期}: [故事標題]

**來源：** Hacker News
**故事 ID：** 12345
**Hacker News 連結：** https://news.ycombinator.com/item?id=12345
**網址：** https://example.com
**分數：** 156 | **評論數：** 42

## 摘要
[簡短的 2-3 句話摘要，說明文章核心內容]

## 為什麼有趣
[解釋為什麼這個故事重要：技術意義、爭議性、創新點等]

## 主要討論點
[評論中的主題，例如爭論焦點、社群共識等]

## 評價
[有趣 / 值得閱讀 / 跳過 / 技術價值高]
```

## Verdict Options

| Verdict | Chinese | Meaning |
|---------|---------|---------|
| interesting | 有趣/值得閱讀 | Worth reading, engaging |
| not_interesting | 不感興趣 | Lower value, skip |
| controversial | 爭議性 | Polarizing, heated debate |
| technical | 技術價值高 | High technical significance |

## Writing Style Guidelines

**Language:**
- Use Traditional Chinese (繁體中文)
- Technical terms stay in English (API, SDK, Rust, Docker, etc.)

**Tone:**
- Professional but accessible
- Not too colloquial
- Clear structure and hierarchy

**Structure:**
- Use headings (##, ###) for organization
- Use bullet points for lists
- Use bold for emphasis

## Technical Term Translation Principles

**Keep in English (proper nouns):**
- GitHub, Docker, Kubernetes, React, Rust, Python
- Company names: Google, Microsoft, Apple
- Product names: AWS, Azure, GCP

**Can translate to Chinese (common concepts):**
- container → 容器
- deployment → 部署
- server → 伺服器
- database → 資料庫

**When uncertain:**
- Keep English term, add Chinese explanation in parentheses
- Example: "使用 Kubernetes (容器編排平台) 部署..."

## Common Translations

| English | Chinese |
|---------|---------|
| Hacker News | Hacker News (usually not translated) |
| comments | 評論 |
| score | 分數 |
| upvote | 按推/推文 |
| thread | 討論串 |
| submitter | 發文者 |
| original poster (OP) | 原發文者 |
| show HN | Show HN (not translated) |
| technical depth | 技術深度 |
| controversial | 爭議性 |
| significant | 顯著/重要 |

## Example Report

```markdown
---
story_id: 46851548
hn_url: https://news.ycombinator.com/item?id=46851548
title: "Notepad++ 遭國家資助行為者劫持"
verdict: interesting
created_at: 2026-02-02T14:30:00
---

# 2026-02-02: Notepad++ 遭國家資助行為者劫持

**來源：** Hacker News
**故事 ID：** 46851548
**Hacker News 連結：** https://news.ycombinator.com/item?id=46851548
**網址：** https://notepad-plus-plus.org/news/hijacked-incident-info-update/
**分數：** 293 | **評論數：** 135

## 摘要

Notepad++ 官方網站遭國家資助行為者入侵，攻擊者嘗試通過修改安裝程式來散布惡意軟體。這是一個嚴重的軟體供應鏈攻擊事件，影響全球數百萬用戶。

## 為什麼有趣

這是一個**重大安全事件**，因為：
1. Notepad++ 是廣泛使用的文字編輯器
2. 攻擊者成功入侵官方網站
3. 涉及國家級別的網路攻擊
4. 引發社群對開源軟體安全性的討論

## 主要討論點

- **供應鏈安全**：如何驗證下載的軟體未被篡改？
- **簽名驗證**：數位簽名的重要性
- **備份方案**：是否需要備份的官方下載來源？
- **政治因素**：軟體不應該成為政治目標

## 評價

**值得關注** - 這是一個重要的安全警訊，提醒我們：
- 從官方來源下載軟體後要驗證簽名
- 開源專案需要嚴格的安全流程
- 社群反應迅速，善意提醒其他用戶
```

## Quality Checklist

Before finalizing a report:

- [ ] Used Traditional Chinese
- [ ] Technical terms kept in English
- [ ] Proper YAML frontmatter format
- [ ] Clear structure with headings
- [ ] Accurate verdict selected
- [ ] Factual information (story ID, URL, etc.)
- [ ] Professional tone throughout
