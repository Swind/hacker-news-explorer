# prompts/templates.py
"""Output format templates."""

CHINESE_OUTPUT_TEMPLATE = """# {TODAY}: [故事標題]

**來源：** Hacker News
**故事 ID：** {{id}}
**Hacker News 連結：** https://news.ycombinator.com/item?id={{id}}
**網址：** {{url}}
**分數：** {{score}} | **評論數：** {{count}}

## 摘要
[簡短的 2-3 句話摘要]

## 為什麼有趣
[解釋為什麼這個故事重要：技術意義、爭議等]

## 主要討論點
[評論中的主題]

## 評價
[有趣 / 值得閱讀 / 跳過]
"""
