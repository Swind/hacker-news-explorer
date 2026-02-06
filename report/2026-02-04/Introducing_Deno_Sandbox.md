---
story_id: 46874097
hn_url: https://news.ycombinator.com/item?id=46874097
title: "Introducing Deno Sandbox"
verdict: technical
created_at: 2026-02-04T03:56:17
updated_at: 2026-02-04T11:28:38
---


---
story_id: 46874097
hn_url: https://news.ycombinator.com/item?id=46874097
title: "Introducing Deno Sandbox"
verdict: technical
created_at: 2026-02-04
---

# 2026-02-04: Deno 推出 Sandbox 安全沙盒服務

**來源：** Hacker News
**故事 ID：** 46874097
**Hacker News 連結：** https://news.ycombinator.com/item?id=46874097
**網址：** https://deno.com/blog/introducing-deno-sandbox
**分數：** 349 | **評論數：** 122

## 摘要

Deno 推出了 **Deno Sandbox**，這是一個輕量級 Linux microVM 沙盒服務，專門為執行不受信任的程式碼而設計。其核心特色是**不可洩露的秘密管理**（Secrets）與**網路出口控制**（Network Egress Control），特別針對 AI/LLM 生成的程式碼執行場景，可在 1 秒內啟動沙盒，並直接部署至 Deno Deploy。

## 為什麼這個技術重要

這是 Deno 在 **AI 程式碼執行安全**領域的重大技術發布，解決了幾個關鍵問題：

1. **AI 生成程式碼的安全執行**：LLM 生成的程式碼通常未經審查即執行，需要更強的安全隔離
2. **秘密保護機制**：API 金鑰以佔位符形式存在於沙盒中，只有向外發送請求時才會被替換為真實值
3. **從開發到生產的一鍵部署**：沙盒程式碼可直接部署至 Deno Deploy，無需重建
4. **輕量級 microVM**：啟動時間 < 1 秒，提供 2 vCPUs 和 768MB-4GB 記憶體

## 技術核心功能

### 不可洩露的秘密管理（Non-Exfiltratable Secrets）

```typescript
import { Sandbox } from "@deno/sandbox";
await using sandbox = await Sandbox.create({
  secrets: {
    OPENAI_API_KEY: {
      hosts: ["api.openai.com"],
      value: process.env.OPENAI_API_KEY,
    },
  },
});
```

沙盒內的程式碼只能看到 `DENO_SECRET_PLACEHOLDER_xxx` 這樣的佔位符，真正的金鑰只在向外發送請求到**經授權的主機**時才會由 proxy 替換。這意味著即使程式碼嘗試將金鑰傳送到惡意網站，得到的也只是無用的佔位符。

### 網路出口控制

```typescript
await using sandbox = await Sandbox.create({
  allowNet: ["api.openai.com", "*.anthropic.com"],
});
```

可以明確限制沙盒只能與特定網域通訊，其他請求會在 VM 邊界被阻擋。

### 部署與持久化

- **`sandbox.deploy()`**：直接從沙盒部署到 Deno Deploy
- **Volumes**：提供讀寫儲存空間
- **Snapshots**：建立唯讀映像，可預裝工具鏈

## 社群討論焦點

### 1. 安全模型的質疑與討論

**佔位符替換的漏洞**：多位使用者指出，如果惡意程式碼找到一個會將輸入值回顯的 API endpoint，可能繞過保護：

```
攻擊者 → 詢問 API → API 回應 "Hello {input}" → 回應被 proxy 替換回金鑰
```

Deno 團隊回應表示，proxy 只會在**經過授權的 HTTP 標頭**中替換金鑰，且會在回應中將真實金鑰替換回佔位符。但社群認為仍需更多細節才能評估安全性。

### 2. 與現有方案的比較

**Tokenizer（fly.io）**：多位使用者提到 fly.io 的 [tokenizer](https://github.com/fly-apps/tokenizer) 專案，它採用類似的 proxy 模式來處理第三方 API 金鑰。Deno 團隊承認受到這個專案的啟發。

**其他競品**：
- **eBPF-based solutions**：更底層的核心級監控
- **OCI-based containers**：更標準化的容器格式
- **gVisor/Firecracker**：傳統的沙盒隔離方案

### 3. 非 HTTP 連線的處理

使用者詢問：**資料庫連線（TCP）如何處理金鑰？**

HTTP 標頭的替換機制無法用於直接的 TCP 連線（如 PostgreSQL、MySQL）。Deno 團隊表示未來可能會新增類似 Vault 的功能來處理這類場景。

### 4. 文章寫作風格的討論

部分使用者質疑這篇文章是否由 **LLM 撰寫**，指出：
- 大量使用冒號引導的從句結構
- 過度使用"And"作為句首
- 特定的修辭模式

Deno 團隊成員回應表示這確實是人工撰寫，但也反映了 LLM 時代對寫作風格的影響。

### 5. 權限模型的深入討論

**Object Capabilities**：有使用者提出使用 **Capability-based security** 模型來進一步限制資料存取：
- 沙盒程式碼只能執行特定租戶範圍的 SQL 查詢
- 限制沙盒程式碼無法傳送 PII 資料到已授權的 API

這是一個比單純控制網路出口更細緻的安全模型。

## 技術規格

| 項目 | 規格 |
|------|------|
| 區域 | Amsterdam, Chicago |
| vCPUs | 2 |
| 記憶體 | 768 MB - 4 GB |
| 生命週期 | 預設暫時性，可延長 |
| 最長生命週期 | 30 分鐘 |
| 啟動時間 | < 1 秒 |

## 定價模式

- **CPU 時間**：$0.05/小時（Pro 方案包含 40 小時）
- **記憶體**：$0.016/GB-小時（Pro 方案包含 1000 GB-小時）
- **儲存空間**：$0.20/GiB-月（Pro 方案包含 5 GiB）

僅按**計算時間**收費，非牆上時鐘時間。

## 適用場景

1. **AI agents 執行程式碼**：LLM 生成的程式碼需要安全環境執行
2. **Vibe-coding 環境**：即時程式碼編輯與執行
3. **安全的 plugin 系統**：使用者提供的程式碼插件
4. **暫時性 CI runners**：短命的建置環境
5. **客戶提供的程式碼**：使用者自訂邏輯的安全執行

## 評價

**技術價值高** - 這是針對 AI時代程式碼執行安全問題的重要嘗試：

### 優點
- 創新的秘密保護機制，降低了 API 金鑰洩露的風險
- 快速啟動時間（< 1 秒）適合互動式開發場景
- 與 Deno Deploy 深度整合，開發到生產流程順暢
- 網路出口控制提供了基本的防禦深度

### 限制與挑戰
- 佔位符替換機制的安全保證仍需更詳細的說明
- 非 HTTP 連線（如資料庫）的金鑰管理尚未完全解決
- 無法防止惡意程式碼**使用**金鑰進行破壞（如刪除資源）
- 需要與更細緻的權限模型（如 Object Capabilities）結合才能提供完整防護

### 總結

Deno Sandbox 是一個**務實的解決方案**，針對 LLM 生成程式碼執行這個新興問題提供了工具。雖然安全模型還有改進空間，但它為 AI 應用開發者提供了一個重要的起點，特別是秘密管理的創新方法值得關注。

對於正在建構 AI 平台、需要執行使用者或 LLM 生成程式碼的開發者來說，這是一個值得評估的選項。

---

## 深度技術分析

### Secrets 管理機制的技術細節

Deno Sandbox 的 secrets 管理採用 **HTTP Proxy 層替換** 方案：

```javascript
應用程式 → Proxy (注入真實金鑰) → 外部 API
```

**運作流程：**
1. 沙盒內程式碼只能看到 `DENO_SECRET_PLACEHOLDER_xxx`
2. 當程式碼發送 HTTP 請求到 approved host 時，proxy 會檢查請求中的 placeholder
3. Proxy 將 placeholder 替換為真實金鑰後發送請求
4. 回應經過 proxy 時，真實金鑰會被替換回 placeholder

**安全保證與限制：**
- ✅ 防止直接的環境變數洩露（`console.log(process.env.KEY)`）
- ✅ 防止透過非授權網域傳輸（請求到 evil.com 會被阻擋）
- ⚠️ 如果 API endpoint 會回顧請求內容，金鑰可能間接洩露
- ⚠️ 需要仔細定義哪些 HTTP 欄位可以包含金鑰

**社群專業意見：**
多位安全專家指出，類似方案已在業界使用：
- **Tokenizer**：fly.io 的開源實作
- **PCI-DSS SaaS**：15 年前就有 tokenization 服務
- **AWS IAM Conditions**：基於來源 IP/VPC 限制權限

### 與其他沙盒技術的對比

| 技術 | 隔離機制 | 啟動時間 | Secrets 管理 | 適用場景 |
|------|---------|---------|--------------|---------|
| **Deno Sandbox** | Linux microVM | < 1 秒 | Proxy 注入 | AI 程式碼執行 |
| **Firecracker** | microVM | ~125ms | 無內建 | 通用 serverless |
| **gVisor** | User-space kernel | 中等 | 無內建 | 容器強化 |
| **eBPF** | Kernel-level 監控 | 快 | 可自訂 | 系統監控與審計 |
| **WebAssembly** | Runtime isolation | 極快 | 可自訂 | 客戶端與伺服器 |

### 網路出口控制的實現

Deno 使用 **outbound proxy** 實現網路控制，類似 `coder/httpjail`：

```typescript
// 配置允許的主機
allowNet: ["api.openai.com", "*.anthropic.com"]

// 未授權請求被阻擋在 VM 邊界
fetch("https://evil.com") // Error: Connection blocked
```

**未來擴展計畫：**
- 分析 outbound connections
- 程式化 hooks 讓受信任程式碼檢查或修改請求
- 更細緻的權限控制（如限制 HTTP 方法、路徑）

### 部署流程的創新

```typescript
const build = await sandbox.deploy("my-app", {
  production: true,
  build: { mode: "none", entrypoint: "server.ts" },
});
const revision = await build.done;
console.log(revision.url);
```

**優勢：**
- 無需在 CI 系統重建
- 無需重新認證不同工具
- 開發環境直接轉換為生產部署
- 自動擴展的 serverless 基礎架構

### 持久化選項

**Volumes：**
- 讀寫儲存空間
- 用於快取、資料庫、用戶資料

**Snapshots：**
- 唯讀映像
- 預裝工具鏈
- 從 snapshot 建立的 volume 可快速創建新環境

```bash
# 一次性安裝
apt-get install tools
# 建立 snapshot
# 未來沙盒啟動時已預裝所有工具
```

## 對 JavaScript/TypeScript 生態系的影響

### 1. AI 應用開發的標準化

Deno Sandbox 可能成為執行 LLM 生成程式碼的**標準方案**：
- 與 JavaScript/TypeScript 生態系深度整合
- 原生支援 TypeScript
- 與 Deno Deploy 無縫整合

### 2. 與其他執行環境的競爭

**Node.js 生態系：**
- 需要類似方案來支援 AI 應用
- 可能出現第三方的實作

**Cloudflare Workers：**
- 已有 V8 isolates
- 可能增加類似的 secrets 管理

**AWS Lambda：**
- 已有 IAM-based 權限
- 可結合 Lambda Layers 實現類似功能

### 3. 安全最佳實踐的影響

Deno Sandbox 推動的安全模式可能影響：
- Secrets 管理的最佳實踐
- 沙盒執行的標準
- AI 應用的安全架構

## 實際應用建議

### 適合使用 Deno Sandbox 的場景

✅ **LLM 生成的程式碼執行**
- AI 輔助程式設計工具
- 自動化腳本生成

✅ **使用者提供的程式碼**
- Plugin 系統
- 使用者自訂邏輯

✅ **即時代碼執行**
- 線上程式設計教學
- 互動式教學環境

### 需要額外考慮的場景

⚠️ **需要直接資料庫連線**
- 目前 HTTP proxy 模式不適用
- 需等待 Vault 功能或自行實作

⚠️ **需要處理 PII 資料**
- 需要更細緻的資料存取控制
- 考慮 Object Capabilities 模型

⚠️ **需要長時間執行的任務**
- 最長生命週期 30 分鐘
- 需要架構調整

## 總結評價

**技術價值：⭐⭐⭐⭐ (4/5)**

Deno Sandbox 是一個**針對 AI 時代問題的務實解決方案**：

**創新點：**
1. Secrets 的 proxy 注入機制是重要的安全創新
2. 從沙盒到生產的一鍵部署簡化了開發流程
3. < 1 秒啟動時間適合互動式場景

**挑戰：**
1. 安全模型的完整保證仍需更多文檔
2. 非 HTTP 連線的 secrets 管理尚未完全解決
3. 無法防止惡意程式碼使用金鑰進行破壞

**推薦指數：**
- 正在建構 AI 平台的開發者：**強烈推薦評估**
- 需要執行不受信任程式碼的專案：**值得考慮**
- 一般 Web 應用開發：**非必需**

這是一個**技術價值高**的發布，為 JavaScript/TypeScript 生態系在 AI 時代的安全執行環境提供了重要的基礎設施。