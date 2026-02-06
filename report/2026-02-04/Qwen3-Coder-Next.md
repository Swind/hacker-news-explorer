---
story_id: 46872706
hn_url: https://news.ycombinator.com/item?id=46872706
title: "Qwen3-Coder-Next"
verdict: interesting
created_at: 2026-02-04T03:43:31
updated_at: 2026-02-04T11:32:14
---


---
story_id: 46872706
hn_url: https://news.ycombinator.com/item?id=46872706
title: "Qwen3-Coder-Next"
verdict: interesting
created_at: 2026-02-04T00:00:00
---

# 2026-02-04: Qwen3-Coder-Next

**來源：** Hacker News
**故事 ID：** 46872706
**Hacker News 連結：** https://news.ycombinator.com/item?id=46872706
**網址：** https://qwen.ai/blog?id=qwen3-coder-next
**分數：** 592 | **評論數：** 368

## 摘要

Qwen3-Coder-Next 是阿里巴巴 Qwen 團隊推出的新一代程式碼生成模型。從社群討論來看，這是一款專注於程式碼生成任務的開放權重模型，提供多種規格（包括 30B 等參數量級），支援本地部署與量化版本，目標是與 Claude、GPT-4 等閉源模型競爭。

## 為什麼有趣

這個故事具有重要意義，原因如下：

1. **技術價值**：Qwen3-Coder-Next 代表了開放權重模型在程式碼生成領域的最新進展，提供一個可本地運作的 Claude/GPT 替代方案

2. **本地 AI 討論深化**：評論區深入探討了「本地模型」的定義、硬體需求、成本效益等實務議題，反映了開發者社群對 AI 自主性的強烈關注

3. **高參與度**：368 則評論顯示社群對開源程式碼模型有高度興趣，討論內容包含硬體配置、量化技術、成本比較等實戰經驗

4. **開源 vs 閉源辯論**：觸發了對 AI 供應商依賴風險的深入討論，涉及開發者職業生涯、平台鎖定等根本性議題

## 主要討論點

### 1. 本地模型的定義與硬體需求

社群對「本地模型」有不同理解：

- **狹義定義**：在同一台實體機器上運行（使用 ollama、llama.cpp 等工具）
- **廣義定義**：在本地網路（LAN）內運行，可能包含多台機器
- **成本考量**：有開發者提出「megapenny」單位，認為本地模型應定義為「低於 1 萬美元」的硬體配置

常見配置討論：
- **高階 PC**：NVIDIA 5090 + Threadripper + 256GB RAM ≈ $10,000
- **Mac 路線**：M3 Ultra (60 核心, 256GB) ≈ $6,000

### 2. Qwen3-Coder 的實際使用經驗

多位開發者分享了實測經驗：

- **硬體需求**：有開發者在 16GB RAM + 6GB RTX 2060 mobile GPU 的舊筆電上成功運行 Qwen3-Coder-30B-A3B-Instruct gguf 版本
- **效能評估**：可達到「usable」（可用）水平，適合小型專案、腳手架生成、基本 bug 修復
- **限制**：大型專案可能會遇到困難，需要將問題分解

### 3. 成本效益分析

評論區詳細比較了本地模型與 cloud API 的成本：

**Cloud API 成本（以 Claude Sonnet 為例）**：
- 價格：$3/$15 per 1M tokens
- 典型 agent 任務：≈ $0.05-0.10 per task
- 1000 tasks/day：≈ $1,500-3,000/month
- **隱藏成本**：重試率（retry overhead）可能使實際成本高出 40-60%

**本地模型成本**：
- 硬體投資：$6,000-10,000 一次性
- 電力成本：≈ $0.15/hour（以 30¢/kWh 計算）
- 優勢：零邊際成本，適合高吞吐量、延遲容忍的工作負載

### 4. 開放權重 vs 閉源模型的戰略辯論

討論上升到更深層次的戰略思考：

**支持開放權重的觀點**：
- 避免依賴單一供應商（Anthropic、OpenAI）
- 維護開發者職業自主性
- 防止「個人電腦之死」
- 建構開放基礎設施

**實用主義觀點**：
- 大模型持續領先小模型
- 應該專注於與大型模型競爭，而非「手工自釀」的小模型
- 租用 H100 等雲端資源也是可行的開放方案

### 5. 技術細節討論

- **量化技術**：Q4_K_M 等量化方案的記憶體使用與載入速度
- **稀疏模型**：從 SSD 使用 mmap() 串流權重的可行性
- **評測需求**：社群呼籲建立標準化的本地模型評測基準，包含 time-to-first-token、tokens-per-second、memory-used 等指標
- **架構差異**：參數數量不是唯一指標，內部架構、活躍參數數量等都很重要

## 評價

**值得關注** - 這則故事不僅是關於一個新模型發布，更反映了開發者社群對 AI 未來方向的深度思考。討論從技術實現延伸到產業戰略、開放性、自主性等根本議題，具有很高的技術價值與社會意義。

Qwen3-Coder-Next 作為開放權重的程式碼模型，提供了 Claude/GPT 之外的實際可行選擇，推動了本地 AI 生態的發展。368 則高品質評論顯示這個話題觸及了開發者社群的核心關切。

---

## 補充分析：Qwen3-Coder-Next 技術細節與競爭格局

### 更新技術規格

根據 Hugging Face 模型卡片，Qwen3-Coder-Next 的關鍵技術特點：

| 技術項目 | 規格 |
|---------|------|
| **總參數 / 激活參數** | 80B 總參數，僅 3B 激活 |
| **隱藏維度** | 2048 |
| **層數** | 48 層 |
| **混合架構** | 12 × (3 × (Gated DeltaNet → MoE) → 1 × (Gated Attention → MoE)) |
| **Mixture of Experts** | 512 專家，每次激活 10 專家 + 1 共享專家 |
| **Gated Attention** | 16 個 Q attention heads, 2 個 KV heads |
| **Gated DeltaNet** | 32 個 V heads, 16 個 QK heads |
| **Context Window** | 262,144 tokens (256K) |
| **最佳採樣參數** | temperature=1.0, top_p=0.95, top_k=40 |

### 核心技術優勢

1. **極高效參數效率**：僅激活 3B 參數卻達到 10-20x 參數模型的性能
2. **DeltaNet + Attention 混合**：DeltaNet 提供高效記憶體處理，Attention 處理複雜依賴
3. **專家網路稀疏激活**：512 專家中僅選用 10 個，大幅降低推理成本
4. **超長上下文**：256K tokens 支援大型專案完整代碼庫分析

### Agentic Coding 能力

Qwen3-Coder-Next 針對 coding agents 特化訓練：

- **長期推理**：支援跨多步驟的複雜任務
- **工具使用**：優化的 function calling 能力
- **錯誤恢復**：從執行失敗中學習並重試
- **IDE 整合**：支援 Claude Code、Qwen Code、Qoder、Kilo、Trae、Cline 等平台

### 與 Claude 3.7 Sonnet 的競爭對比

| 特性 | Qwen3-Coder-Next | Claude 3.7 Sonnet |
|------|------------------|-------------------|
| **部署方式** | 開放權重，本地/自託管 | 僅 API (Anthropic) |
| **參數透明度** | 80B/3B 已公開 | 未公開 |
| **成本模式** | 一次性硬體投資 + 電費 | $3/$15 per 1M tokens |
| **Context 長度** | 256K tokens | 200K tokens |
| **推理模式** | 標準模式 (無 thinking blocks) | 標準 + 擴展思考模式 |
| **工具支援** | SGLang, vLLM, llama.cpp, MLX-LM | Claude API, Claude Code CLI |

### 部署選項

**本地部署：**
```bash
# SGLang (推薦，需要 v0.5.8+)
pip install 'sglang[all]>=v0.5.8'
python -m sglang.launch_server --model Qwen/Qwen3-Coder-Next \
    --port 30000 --tp-size 2 --tool-call-parser qwen3_coder

# vLLM
pip install 'vllm>=0.15.0'
vllm serve Qwen/Qwen3-Coder-Next --port 8000 \
    --tensor-parallel-size 2 --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder
```

**消費級應用：**
- Ollama
- LM Studio
- MLX-LM (Mac 原生支援)
- llama.cpp
- KTransformers

### 中國 AI 發展的戰略意義

Qwen3-Coder-Next 的推出反映了中國 AI 生態的快速發展：

1. **技術追趕**：在編碼 AI 領域與 OpenAI、Anthropic 等美國領先公司競爭
2. **開放權重策略**：與美國公司的閉源 API 模式形成對比，提供全球開發者更多選擇
3. **克服限制**：在美國 GPU 出口限制下仍能發展競爭模型
4. **全球化布局**：在 Hugging Face、GitHub 等平台積極發布英文文檔和工具

### 社羣關注的未來議題

評論中反覆出現的主題：

1. **AI 供應商多樣化**：避免單一供應商鎖定的重要性
2. **本地計算的復興**：個人電腦作為 AI 計算節點的可行性
3. **成本透明化**：需要更精確的本地 vs 雲端成本比較工具
4. **標準化評測**：建立統一的本地模型效能 benchmark
5. **開發者自主性**：維護職業自由度，不被特定 AI 供應商束縛

### 總結更新

Qwen3-Coder-Next 不僅是一個新的程式碼模型，更代表了 AI 產業的重要轉折點：

- **技術層面**：Mixture-of-Experts + DeltaNet 混合架構展示了高效模型的新方向
- **商業層面**：開放權重 vs 閉源 API 的競爭加劇
- **戰略層面**：全球 AI 競爭版圖重組，中國公司成為重要力量
- **哲學層面**：本地計算 vs 雲端集中的辯論持續升溫

669 分數和 389 則評論顯示這個話題觸及了開發者社群的核心關切，值得持續關注其後續發展。