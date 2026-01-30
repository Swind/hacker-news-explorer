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

這實現了**任務委派模式**——Main Agent 專注協調，SubAgent 專注執行。

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
