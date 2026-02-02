# Reddit Explorer

> 一個 LLM 驅動的自主探索 Agent 框架，以 Hacker News 探索為示範案例。

## 專案概述

這個專案的核心精神是：**將 LLM 不僅視為對話機器人，而是作為「推理引擎」來驅動自主任務執行。**

### 這個工具做什麼？

- 使用 Claude API 自動探索 Hacker News
- 識別有趣、具爭議性或技術上有意義的文章
- 將分析任務委派給專門的 SubAgent
- 生成結構化的中文報告並持續更新

### 為什麼這個專案有趣？

它展示了一個**可重用的 Agent 架構模式**——只要更換 tools 和 prompts，就能適配不同的探索任務（Reddit、其他新聞站、甚至企業內部知識庫）。

---

## LLM 互動流程

這個專案展示的關鍵模式是：**LLM 作為工具調度的「大腦」**。

### 資訊流向

```
┌─────────────────────────────────────────────────────────────────┐
│                        程式準備階段                               │
├─────────────────────────────────────────────────────────────────┤
│ 1. 定義 Tools (JSON Schema)    2. 建立 System Prompt            │
│    - tool name                   - Agent 角色                     │
│    - description                 - 目標與約束                      │
│    - input parameters            - 工作流程說明                    │
│                                   - 輸出格式模板                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     每次對話迭代 (Loop)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   程式 → LLM:                     LLM → 程式:                     │
│   ┌─────────────┐                ┌─────────────┐                │
│   │ Messages    │                │ Content     │                │
│   │ - System    │    Claude API  │ Blocks:     │                │
│   │ - User      │  ──────────→   │ 1. Text     │                │
│   │ - Assistant │                │ 2. tool_use │                │
│   │ - ToolResult│                │    blocks   │                │
│   └─────────────┘                └─────────────┘                │
│                                                                  │
│   [程式解析 tool_use]                                           │
│      ↓                                                          │
│   [執行對應的 Tool]                                             │
│      ↓                                                          │
│   [將結果包成 ToolResult]                                       │
│      ↓                                                          │
│   [加入 Messages，進入下一次迭代]                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [直到 stop_reason ≠ "tool_use"]
```

### 關鍵概念

**LLM 不直接「做事情」**——它只做兩件事：
1. **思考**：產生 text 回應（分析、判斷、規劃）
2. **決策**：請求呼叫工具（tool_use blocks）

**程式負責「執行」**：
- 解析 LLM 的 tool_use 請求
- 執行實際的邏輯（呼叫 API、讀檔案、寫檔案）
- 將執行結果回饋給 LLM
- 判斷何時停止

---

## Tool 架構

這個專案的核心設計模式是：**將所有能力抽象為 Tools**。

### Tool Schema 格式

每個 Tool 都需要提供一個 JSON Schema，告訴 LLM：
- 這個工具叫什麼名字
- 它做什麼事情
- 需要什麼參數
- 參數的類型和限制

```python
{
    "name": "get_hn_stories",                    # 工具名稱
    "description": "Fetch Hacker News stories...", # 工具描述
    "input_schema": {                            # 參數定義（JSON Schema 格式）
        "type": "object",
        "properties": {
            "story_type": {
                "type": "string",
                "enum": ["top", "new", "best", "ask", "show", "job"]
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 30
            }
        },
        "required": ["story_type"]               # 必填參數
    }
}
```

### LLM 如何呼叫 Tool

當 LLM 決定要使用某個工具時，它會回傳一個 `tool_use` block：

```javascript
// LLM 回傳的 Content Block
{
    "type": "tool_use",
    "id": "toolu_01A1B2C3D4E5F6G7H8I9J0K1",     // 工具呼叫的唯一 ID
    "name": "get_hn_stories",                    // 要呼叫的工具名稱
    "input": {                                   // 工具參數
        "story_type": "top",
        "limit": 10
    }
}
```

**程式接收到 tool_use 後的處理流程**：

```
┌─────────────────────────────────────────────────────────────────┐
│  1. 解析 tool_use block                                         │
│     - 提取 name: "get_hn_stories"                               │
│     - 提取 input: {story_type: "top", limit: 10}                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. 查找並執行對應的 Tool                                       │
│     - 根據 name 找到 GetHNStoriesTool                           │
│     - 呼叫 tool._execute(**input)                               │
│     - 傳入 context (workdir, hn_adapter, etc.)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. 取得執行結果                                                 │
│     # Tool 返回字串結果                                          │
│     "[42071655] Show HN: I made a map of... | score: 156 | ..." │
│     "[42071654] The Web Graph ... | score: 89 | ..."            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. 封裝成 tool_result message                                  │
│     {                                                           │
│       "type": "tool_result",                                    │
│       "tool_use_id": "toolu_01A1B2C3...",  # 對應原始呼叫       │
│       "content": "[42071655] Show HN:..."                      │
│     }                                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. 加入對話歷史，傳給 LLM                                       │
│     messages.append({                                           │
│         "role": "user",                                         │
│         "content": [tool_result]                                │
│     })                                                          │
└─────────────────────────────────────────────────────────────────┘
```

### BaseTool 抽象類

```python
class BaseTool(ABC):
    @classmethod
    def get_name(cls) -> str:      # 工具識別名稱

    @classmethod
    def get_schema(cls) -> dict:   # JSON Schema 給 LLM 理解

    def execute(self, **kwargs) -> str:     # 錯誤處理包裝
        try:
            return self._execute(**kwargs)
        except Exception as e:
            return f"Error: {e}"

    @abstractmethod
    def _execute(self, **kwargs) -> str:    # 實際實作
```

### 實際範例：get_hn_stories

**Schema（傳給 LLM）**：
```python
{
    "name": "get_hn_stories",
    "description": "Fetch Hacker News stories. Returns list with id, title, url, score, author, time, comment count.",
    "input_schema": {
        "type": "object",
        "properties": {
            "story_type": {
                "type": "string",
                "enum": ["top", "new", "best", "ask", "show", "job"]
            },
            "limit": {"type": "integer", "minimum": 1, "maximum": 30}
        },
        "required": ["story_type"]
    }
}
```

**LLM 呼叫時回傳**：
```json
{
    "type": "tool_use",
    "id": "toolu_012345",
    "name": "get_hn_stories",
    "input": {"story_type": "top", "limit": 5}
}
```

**Tool 執行後返回**：
```
[42071655] Show HN: I made a map of every indie hacker... (https://indiemap.tech) | score: 156 | comments: 42 | by: pj_vlieg
[42071654] The Web Graph (https://www.thewebgraph.de) | score: 89 | comments: 12 | by: _hosam
[42071653] Show HN: State of Developer Adoption 2025 (https://github.com/...) | score: 76 | comments: 28 | by: dww
```

這個字串結果會被包成 `tool_result` 傳回給 LLM，LLM 看到結果後決定下一步做什麼。

### 實際範例：create_report

**Schema（傳給 LLM）**：
```python
{
    "name": "create_report",
    "description": "Create a new story analysis report with frontmatter metadata.",
    "input_schema": {
        "type": "object",
        "properties": {
            "story_id": {"type": "integer", "description": "Hacker News story ID"},
            "hn_url": {"type": "string", "description": "URL to the HN story"},
            "title": {"type": "string", "description": "Story title"},
            "verdict": {
                "type": "string",
                "enum": ["interesting", "not_interesting", "controversial", "technical"],
                "description": "Analysis verdict"
            },
            "content": {"type": "string", "description": "Markdown content of the analysis"}
        },
        "required": ["story_id", "hn_url", "title", "verdict", "content"]
    }
}
```

**LLM 呼叫時回傳**：
```json
{
    "type": "tool_use",
    "id": "toolu_012346",
    "name": "create_report",
    "input": {
        "story_id": 42071655,
        "hn_url": "https://news.ycombinator.com/item?id=42071655",
        "title": "Show HN: I made a map of every indie hacker",
        "verdict": "interesting",
        "content": "## 分析\n\n這是一個收集獨立開發者地圖的專案..."
    }
}
```

**Tool 執行後返回**：
```
Created report at report/2025-01-30/Show_HN_I_made_a_map_of_every_indie_hacker.md
```

同時在檔案系統建立：
```markdown
---
story_id: 42071655
hn_url: https://news.ycombinator.com/item?id=42071655
title: "Show HN: I made a map of every indie hacker"
verdict: interesting
created_at: 2025-01-30T14:23:45
---

## 分析

這是一個收集獨立開發者地圖的專案...
```

### Tool 註冊與發現

所有 Tools 在 `tools/__init__.py` 註冊：

```python
ALL_TOOL_CLASSES = [
    GetHNStoriesTool,      # 取得 HN 故事列表
    GetHNCommentsTool,     # 取得特定故事的評論
    ReadWebpageTool,       # 讀取網頁內容
    CreateReportTool,      # 建立報告
    AppendReportTool,      # 追加報告內容
    TaskTool,              # ← 特殊：生成 SubAgent
    FinishExplorationTool, # 結束探索
    # ...
]
```

啟動時將所有 Tools 的 schema 傳給 LLM，讓它知道「我可以做什麼」。

### Context 注入

Tools 執行時會收到 context dict，包含依賴：

```python
context = {
    "workdir": "/path/to/work",      # 檔案操作路徑
    "hn_adapter": HackerNewsAdapter(),  # HN API 客戶端
    "web_reader": WebReaderAdapter(),   # 網頁讀取器
}
```

這實現了 **Dependency Injection**——Tools 不需要自己建立連線，只管執行邏輯。

### 特殊 Tool：Task

`TaskTool` 不執行實際操作，而是**生成新的 SubAgent**：

```python
# LLM 呼叫 Task("analyze_story", "分析這個故事", "...")
#
# 程式解析後：
# → 建立新的 SubAgent 實例
# → 用指定的 agent_type 和 prompt
# → SubAgent 獨立運作（有自己的對話循環）
# → 完成後回傳結果給 Main Agent
```

**Task 的 Schema**：
```python
{
    "name": "Task",
    "description": "Spawn a subagent for focused analysis...",
    "input_schema": {
        "type": "object",
        "properties": {
            "description": {"type": "string", "description": "Short task description (3-5 words)"},
            "prompt": {"type": "string", "description": "Detailed instructions for the subagent"},
            "agent_type": {
                "type": "string",
                "enum": ["analyze_story", ...],
                "description": "Type of subagent to spawn"
            }
        },
        "required": ["description", "prompt", "agent_type"]
    }
}
```

這實現了**任務委派模式**——Main Agent 專注協調，SubAgent 專注執行。

### 特殊 Tool：Skill

`SkillTool` 讓 LLM 可以**按需載入領域知識**：

```python
# LLM 呼叫 Skill("chinese-writing")
#
# 程式解析後：
# → 讀取 .skills/chinese-writing/SKILL.md
# → 將完整內容包在 <skill-loaded> 標籤中
# → 作為 tool_result 返回給 LLM
# → LLM 獲得中文寫作知識，後續遵循該風格
```

**漸進式披露 (Progressive Disclosure)**：
- **Layer 1**：啟動時只載入 skill 名稱和描述（~100 tokens/skill）
- **Layer 2**：呼叫 Skill 時才載入完整內容（~2000 tokens）
- **Cache 保留**：Skill 內容透過 tool_result 注入，不破壞 prompt cache

**SKILL.md 格式**：
```markdown
---
name: chinese-writing
description: 中文報告寫作。使用時機：寫報告前、格式化輸出時。
---

# 中文報告寫作指南

## 使用時機
- 準備撰寫任何報告內容時
...

## 輸出格式
...
```

這實現了**知識外部化**——將領域知識存在檔案中，而非鎖在模型參數裡。

---

## Agent/Subagent 層級架構

這個專案展示了**多 Agent 協作模式**——將複雜任務分解給專門的 Agent 處理。

### 架構層級

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Agent                               │
│                     (NewsExplorerAgent)                          │
├─────────────────────────────────────────────────────────────────┤
│  系統提示：完整探索指令、工作流程、輸出格式                        │
│  工具集：完整 access（HN API, Task, Report, Webpage）            │
│  職責：                                                          │
│    - 探索 HN，發現有趣故事                                        │
│    - 決定哪些故事需要深入分析                                     │
│    - 委派分析任務給 SubAgent                                      │
│    - 匯總結果，生成最終報告                                       │
│  停止條件：呼叫 finish_exploration 或不再請求工具                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Task("analyze_story", ...)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SubAgent                                  │
│                      (分析任務專用)                               │
├─────────────────────────────────────────────────────────────────┤
│  系統提示：專注於單一故事分析                                     │
│  工具集：白名單過濾（僅 Report + Webpage 工具）                  │
│  職責：                                                          │
│    - 讀取故事連結的網頁內容                                       │
│    - 分析並提取關鍵資訊                                           │
│    - 建立或更新報告檔案                                           │
│  停止條件：不再請求工具                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 返回分析摘要
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Main Agent 收到結果                          │
│                    繼續探索或委派下一個任務                        │
└─────────────────────────────────────────────────────────────────┘
```

### 為什麼需要 SubAgent？

**1. 上下文隔離**
- Main Agent 的對話記錄已經很長（探索過許多故事）
- 如果直接在 Main Agent 內分析，可能受到先前對話的 bias 影響
- SubAgent 從頭開始，專注於單一任務

**2. 工具權限控制**
```python
AGENT_TYPES = {
    "analyze_story": {
        "tools": [
            "create_report",
            "append_report",
            "read_report",
            "read_webpage",
            # ← 只有分析和報告工具
            # ← 沒有 HN API，不會「分心」去探索新故事
        ]
    }
}
```

**3. 獨立思考空間**
- SubAgent 有自己的系統提示，針對特定任務優化
- 可以反覆嘗試而不會汙染 Main Agent 的對話歷史

### 共享 BaseAgent

兩種 Agent 都繼承自 `BaseAgent`，共享核心循環——差別只在系統提示、停止條件和工具權限。

---

## 核心設計原則

這個專案體現了幾個重要的 LLM Agent 設計原則：

### 1. LLM 是推理引擎，不是執行引擎

```
LLM 決定「做什麼」          程式負責「怎麼做」
─────────────────          ─────────────────
分析 HN 故事列表    →    呼叫 HN API
發現有趣的故事      →    委派 SubAgent
判斷需要更多信息    →    讀取網頁內容
完成分析            →    寫入報告檔案
```

**關鍵洞察**：LLM 的價值在於**判斷和規劃**，不是在於執行。程式負責可靠的執行。

### 2. 結構化輸出 = 可程式化處理

報告使用 YAML frontmatter：

```markdown
---
hn_id: 42071653
title: "Show HN: ..."
url: https://...
created_at: 2025-01-28
---

## 分析內容
...
```

這讓報告可以被**程式讀取和處理**——例如增量更新、搜尋、匯總。

### 3. 增量工作流

探索前先檢查是否已有報告，避免重複勞動——Agent 可以記住之前的分析結果。

### 4. 可擴展性

新增功能只需：

| 想要新增 | 怎麼做 |
|---------|--------|
| 新的能力 | 繼承 `BaseTool`，加入 `ALL_TOOL_CLASSES` |
| 新的 Agent 類型 | 在 `AGENT_TYPES` 新增配置 |
| 新的探索目標 | 修改 system prompt，更換 tools |
| 新的輸出格式 | 修改 `templates.py` |

**不需要改動核心循環邏輯**——框架與功能分離。

### 5. 錯誤隔離

每個 Tool 的 `execute()` 方法都包裝了 try-catch，工具失敗不會讓整個 Agent 崩潰——LLM 收到錯誤訊息後可以決定如何處理。

---

## 總結

這個專案不只是一個 Hacker News 探索工具，它是**一個可重用的 LLM Agent 架構模式**的示範：

1. **Tool 抽象**——將能力統一介面化
2. **多 Agent 協作**——透過 Task 工具實現委派
3. **上下文管理**——隔離的 SubAgent 避免干擾
4. **結構化輸出**——frontmatter 讓結果可程式化
5. **增量工作流**——檢查現有結果再決定動作

將這些模式抽離出來，就可以構建各種 LLM 驅動的自動化工具——而不只是對話機器人。

---

## 安裝與使用

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定 API Key
export ANTHROPIC_API_KEY="your-api-key"

# 執行探索
python main.py
```

詳細的架構文檔請參考 [ARCHITECTURE.md](ARCHITECTURE.md)。
