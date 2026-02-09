---
story_id: 46903616
hn_url: https://news.ycombinator.com/item?id=46903616
title: "We tasked Opus 4.6 using agent teams to build a C Compiler"
verdict: interesting
created_at: 2026-02-07T09:24:39
---

---
story_id: 46903616
hn_url: https://news.ycombinator.com/item?id=46903616
title: "We tasked Opus 4.6 using agent teams to build a C Compiler"
verdict: interesting
created_at: 2026-02-07T00:00:00
---

# 2026-02-07: 使用 Opus 4.6 Agent 團隊建構 C 編譯器

**來源：** Hacker News
**故事 ID：** 46903616
**Hacker News 連結：** https://news.ycombinator.com/item?id=46903616
**網址：** https://www.anthropic.com/engineering/building-c-compiler
**分數：** 709 | **評論數：** 690

## 摘要

Anthropic 研究員 Nicholas Carlini 發表了一項突破性實驗：使用 16 個 Claude Opus 4.6 AI agent 並行工作，在近乎無人監督的情況下，從頭建構了一個能編譯 Linux 6.9 核心的 C 編譯器。這個專案歷經近 2,000 次 Claude Code sessions，花費約 $20,000 API 成本，產生了 10 萬行程式碼，成功在 x86、ARM 和 RISC-V 架構上建構出可開機的 Linux 核心。

## 技術方法論

### Agent Team 架構

**無限循環機制 (Ralph-loop 類似)**：
```bash
while true; do
  COMMIT=$(git rev-parse --short=6 HEAD)
  LOGFILE="agent_logs/agent_${COMMIT}.log"
  claude --dangerously-skip-permissions \
    -p "$(cat AGENT_PROMPT.md)" \
    --model claude-opus-X-Y &> "$LOGFILE"
done
```

**並行工作流程**：
- 每個 agent 在獨立 Docker 容器中運作
- 共享 git repository (upstream)
- 透過「鎖定文件」同步機制避免重複工作
- Agent 自行決定下一個任務並持續執行

**同步算法**：
1. Agent 通過寫入 `current_tasks/` 目錄中的文件來鎖定任務
2. 完成任務後從 upstream 拉取更新、合併、推送、移除鎖定
3. 衝突頻繁發生，但 Claude 能夠自行解決

### 關鍵設計原則

**1. 高品質測試為核心**
- 使用 GCC 作為「預言者」(oracle) 進行比對驗證
- 採用 GCC torture test suite 作為基準測試
- 編譯多個開源專案 (SQLite、Redis、libjpeg、QuickJS、Lua) 作為驗證
- 建立 CI pipeline 確保新提交不破壞現有功能

**2. 為 AI 設計的測試環境**
- 減少 context window 污染：測試輸出簡潔，重要資訊記錄到文件
- 克服「時間盲點」：提供 `--fast` 選項隨機採樣 1-10% 測試
- ERROR 標記統一格式，便於 grep 搜尋
- 維護詳細的 README 和進度文件

**3. 並行化的挑戰與解決**
- 初期：多個 agent 處理不同的失敗測試 (容易並行)
- 後期：編譯 Linux 核心時遇到瓶頸 (單一大任務)
- 解決方案：使用 GCC 混合編譯，隨機分配文件給不同 agent 處理

**4. Agent 專業化分工**
- 重構 agent：消除重複程式碼
- 效能 agent：改善編譯器本身的效能
- 優化 agent：輸出更有效率的編譯後程式碼
- 設計審查 agent：從 Rust 開發者角度批判並改善架構
- 文件 agent：維護專案文件

## 成果與限制

### 成就
- **10 萬行程式碼** (使用 Rust 撰寫)
- **支援多架構**：x86、ARM、RISC-V
- **可開機 Linux 6.9**：核心能夠成功啟動
- **零依賴設計**：不依賴現有編譯器工具鏈

### 限制
1. **編譯後程式碼效率低**：即使開啟所有優化，仍不如 GCC 關閉優化的效率
2. **16-bit x86 支援問題**：無法產生符合 Linux 32KB 限制的程式碼，需呼叫 GCC 處理
3. **無法建構組譯器與連結器**：缺乏測試套件導致難以實現
4. **Opus 4.6 是關鍵**：早期版本 (4.0-4.5) 幾乎無法完成此任務

## 社群討論焦點

### 1. 技術評價兩極

**正面評價**：
- 「這項測試證明了 AI 是真實的」
- 從「能運作」到「可實用」是巨大跨越
- Agent 協作模式展現了 AI 軟體工程的新範式

**質疑聲音**：
- $20,000 成本 vs 人工開發的效益比較
- 10 萬行是否過度膨脹 (TCC 僅 1.5 萬行)
- 隱藏的 catastrophic bug 風險
- 依賴 GCC 處理 16-bit 部分被視為「作弊」

### 2. 測試驅動開發的關鍵角色

多位 HN 用戶指出此專案成功的原因：
- **高度規範化的任務**：編譯器有明確規格和測試
- **完整測試套件**：GCC torture tests 提供閉環驗證
- **可自動化驗證**：不需要人工介入判斷正確性

「對於擁有極其全面測試套件和詳細規格的專案，AI 是理想選擇」

### 3. 組譯器 (Assembler) 的困難度

討論中反駁了「組譯器很簡單」的說法：
- x86 指令有多種編碼方式
- 變動長度指令導致地址計算的「雞蛋問題」
- 需要多趟掃描才能找到最佳編碼
- 這解釋了為何 Claude 能建構編譯器卻無法完成組譯器

### 4. 成本效益辯論

熱烈討論 $20,000 的成本是否合理：
- **支持方**：遠低於人工開發同樣專案的成本
- **反對方**：傳統開發更具可預測性
- **中立方**：這是研究性質的壓力測試，非生產環境方案

### 5. AI 能力的演進

從 Opus 4.0 到 4.6 的對比：
- 4.0-4.5：勉強能產生功能性編譯器
- 4.5：首次成功
- 4.6：顯著提升，但仍有明顯限制

這展現了 AI 模型快速演進的軌跡。

## 為什麼有趣

這是一個**里程碑式的研究**，因為：

1. **Agent 協作的新範式**：證明了多 agent 並行工作可以解決超大型軟體問題
2. **近乎無人監督的自主性**：設計適當的環境後，AI 能夠自我導向、自我修正
3. **能力邊界的探測**：作為能力基準測試，幫助我們理解當前 AI 的極限與未來潛力
4. **軟體工程啟示**：展示了「測試驅動 + AI」的強大組合
5. **實質性突破**：不是 toy project，而是能編譯真實作業系統核心的工具

## 技術意義

這項研究對 AI 輔助軟體開發有深遠影響：

- **Methodology > Model**：適當的 harness 設計比模型本身更重要
- **測試是 AI 的指南針**：高品質測試讓 AI 知道「什麼是正確的」
- **並行化的挑戰**：從獨立任務到整合任務的轉換是關鍵難點
- **專業化的價值**：不同 agent 扮演不同角色比單一 agent 更有效
- **Context 管理的重要性**：如何讓 AI 在大型專案中保持方向感

## 評價

**值得關注** - 這是一項重要的能力基準研究，展示了 AI agent 團隊的潛力與極限。雖然產生的編譯器在效率上仍遜於傳統工具，但能夠編譯並啟動 Linux 核心本身就是重大成就。這項研究為未來 AI 輔助軟體開發提供了寶貴的方法論洞察，特別是在如何設計環境讓 AI 自主工作這一關鍵課題上。

對軟體工程師而言，這既是挑戰也是啟示：AI 正在從「程式碼生成工具」演進為「自主問題解決者」，但如何正確引導和管理這種能力，將是未來的重要課題。