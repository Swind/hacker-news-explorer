---
name: chinese-writing
description: 中文報告寫作。使用時機：寫報告前、格式化輸出時、翻譯技術內容時。
---

# 中文報告寫作指南

## 使用時機
- 準備撰寫任何報告內容時
- 需要格式化中文輸出時
- 翻譯技術術語時

## 輸出格式

報告使用 YAML frontmatter + Markdown 內容：

```yaml
---
story_id: 12345
hn_url: https://news.ycombinator.com/item?id=12345
title: "故事標題"
verdict: interesting  # 選項: interesting, not_interesting, controversial, technical
created_at: 2026-02-02T14:30:00
---
```

## 報告結構

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

## Verdict 選項說明

- **interesting**: 有趣、值得閱讀的文章
- **not_interesting**: 不感興趣、價值較低
- **controversial**: 引發爭議、討論熱烈
- **technical**: 技術價值高、值得深入研究

## 寫作風格

- 使用繁體中文
- 技術術語保留原文（如 API, SDK, Rust）
- 專業但易懂的語氣
- 避免過於口語化
- 結構清晰，層次分明

## 技術術語翻譯原則

- 專有名詞保留原文：GitHub, Docker, Kubernetes
- 通用概念可翻譯：container → 容器，deployment → 部署
- 不確定時保留原文並加註解釋
