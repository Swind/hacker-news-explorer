# Skill System Design

## 概述

為 reddit-explorer agent 加入 Skill 功能，參考 `v4_skills_agent.py` 的實作模式，使用漸進式披露機制來節省 token 並支援 prompt cache。

## 核心設計

### 資料流

```
啟動階段：
  SkillLoader 掃描 .skills/ 目錄
  → 解析 SKILL.md 的 YAML frontmatter
  → 提取 name + description (Layer 1, ~100 tokens)
  → 生成 skill 清單加入系統提示

運行階段：
  LLM → tool_use: Skill(name="chinese-writing")
  → 程式執行 run_skill()
  → 讀取完整 SKILL.md 內容 (Layer 2)
  → 回傳 <skill-loaded>...</skill-loaded>
  → LLM 獲得知識後續使用
```

### 檔案結構

```
reddit-explorer/
├── .skills/                    # 技能檔案（與程式碼分離）
│   ├── chinese-writing/       # 中文報告寫作
│   │   └── SKILL.md
│   ├── incremental-update/    # 增量更新流程
│   │   └── SKILL.md
│   ├── hn-analysis/           # HN 分析技巧
│   │   └── SKILL.md
│   └── web-extraction/        # 網頁內容提取
│       └── SKILL.md
├── skills/                     # 程式碼（loader 邏輯）
│   └── loader.py              # SkillLoader 類
├── agents/
│   ├── base.py                # 新增 SKILL_TOOL 和 run_skill
│   ├── main.py                # 使用 retry_api_call
│   ├── subagent.py            # 使用 retry_api_call
│   └── config.py              # 不變
├── prompts/
│   ├── system.py              # 新增 skill 清單
│   ├── subagent.py            # 新增 skill 清單
│   └── templates.py           # 部分內容移到 skill
└── main.py
```

## 元件設計

### skills/loader.py

```python
from pathlib import Path
import re

class SkillLoader:
    """載入和管理 skills 從 .skills/ 目錄"""

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills = {}
        self.load_skills()

    def parse_skill_md(self, path: Path) -> dict:
        """解析 SKILL.md 為 {name, description, body, path, dir}"""

    def load_skills(self):
        """掃描目錄，載入所有 SKILL.md metadata"""

    def get_descriptions(self) -> str:
        """Layer 1: 返回 skill 清單（name + description）"""

    def get_skill_content(self, name: str) -> str:
        """Layer 2: 返回完整 skill 內容"""

    def list_skills(self) -> list:
        """返回 skill 名稱列表"""
```

### agents/base.py - 新增 Skill tool

```python
from skills.loader import SKILLS

SKILL_TOOL = {
    "name": "Skill",
    "description": f"載入技能以獲得專門知識\n\n可用技能：\n{SKILLS.get_descriptions()}",
    "input_schema": {
        "type": "object",
        "properties": {
            "skill": {"type": "string"}
        },
        "required": ["skill"]
    }
}

def run_skill(skill_name: str) -> str:
    content = SKILLS.get_skill_content(skill_name)
    if content is None:
        available = ", ".join(SKILLS.list_skills()) or "none"
        return f"Error: Unknown skill '{skill_name}'. Available: {available}"
    return f"<skill-loaded name=\"{skill_name}\">\n{content}\n</skill-loaded>"
```

### 系統提示整合

**prompts/system.py:**
```python
from skills.loader import SKILLS

SYSTEM_PROMPT = f"""You are a News Exploration Agent at {WORKDIR}.

Loop: explore HN -> analyze interesting stories -> write reports in Chinese.

**Skills available** (invoke with Skill tool when task matches):
{SKILLS.get_descriptions()}

**Subagents available** (invoke with Task tool for story analysis):
{get_agent_descriptions()}

Rules:
- Use Skill tool IMMEDIATELY when a task matches a skill description
- Use Task("analyze_story") for focused story analysis
- Max 30 tool calls per session
- Call finish_exploration when done"""
```

**prompts/subagent.py:**
```python
from skills.loader import SKILLS

def get_subagent_prompt(agent_type: str, workdir: str) -> str:
    return f"""You are a {agent_type} subagent at {workdir}.

**Skills available** (invoke with Skill tool when task matches):
{SKILLS.get_descriptions()}

Rules:
- Use Skill tool IMMEDIATELY when a task matches a skill description

Complete the task and return a clear, concise summary."""
```

## SKILL.md 格式

```markdown
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
...
```

## 優先順序

1. **chinese-writing** - 中文報告寫作格式與風格
2. **incremental-update** - 增量更新流程
3. **hn-analysis** - HN 分析技巧
4. **web-extraction** - 網頁內容提取

## 錯誤處理

- Skill 不存在 → 返回錯誤訊息並列出可用 skills
- 格式錯誤 → 跳過該 skill，記錄警告
- 目錄不存在 → 啟動時創建，返回空清單

## Cache 策略

- 系統提示只在啟動時生成（保持前綴不變）
- Skill 內容透過 tool_result 注入（不破壞 cache）
- 前綴不變 = prompt cache 命中 = 成本降低 20-50x
