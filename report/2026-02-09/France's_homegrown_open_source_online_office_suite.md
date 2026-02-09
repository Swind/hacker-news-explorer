---
story_id: 46923736
hn_url: https://news.ycombinator.com/item?id=46923736
title: "France's homegrown open source online office suite"
verdict: interesting
created_at: 2026-02-09T10:44:25
---

# 2026-02-09: France's homegrown open source online office suite

**來源：** Hacker News
**故事 ID：** 46923736
**Hacker News 連結：** https://news.ycombinator.com/item?id=46923736
**網址：** https://github.com/suitenumerique
**分數：** 800 | **評論數：** 334

## 摘要

法國政府部門 DINUM 和 ANCT 推出「La Suite numérique」（簡稱 La Suite），一個 100% 開源（MIT 授權）的數位協作辦公套件。該專案是法國、德國和荷蘭的跨國合作成果，旨在實現歐洲數位主權，減少對 Microsoft Office 和 Google Workspace 等美國科技巨頭產品的依賴。

## 為什麼有趣

這是一個**具有重要意義的數位主權倡議**：

1. **政府主導的開源專案**：由法國、德國政府部門直接投資開發，而非單純採購或贊助現有專案
2. **歐洲跨國合作**：法國（DINUM/ANCT）、德國（ZenDiS）、荷蘭共同參與，建立統一的歐洲開源辦公解決方案
3. **MIT 授權策略**：採用寬鬆的 MIT 授權，邀請私營企業使用、銷售和貢獻，與典型的 GPL 授權政府專案不同
4. **完整生態系統**：包含 Docs（協作文件）、Visio（視訊會議，基於 Matrix 和 LiveKit）等工具
5. **實際規模部署**：已在法國多個市政機構日常使用

## 主要討論點

### 技術爭論

**「這算是真正的 Office Suite 嗎？」**
- 部分用戶質疑：La Suite Docs 更像 Notion/Confluence 等協作工具，而非傳統的 Word 替代品
- 專案回應：定位為「Content over Form」，專注於結構化內容協作，而非文件格式排版
- 未來計劃：可能整合 LibreOffice 以處理複雜文件編輯需求

**技術棧選擇**
- Docs 使用 Django + React + BlockNote.js + Yjs（CRDT 協作引擎）
- 社群擔憂：Python/Django 的效能問題，認為應採用 Go 等語言以媲美商業產品

**專案完整度**
- 缺乏試算表（Spreadsheet）、簡報（Presentation）等核心 Office 元件
- 目前更像是「協作套件」而非完整的「辦公套件」

### 政治與經濟討論

**數位主權的成本**
- 歐洲若認真追求獨立，應投入「數百億歐元級別」的資金
- 現有的 10k 歐元規模黑客松活動遠遠不足
- 真正的獨立需要提高稅收，當前政黨可能因此失去選舉

**公部門軟體開發模式**
- 法國採用「內部開發」模式，在歐洲屬於特例
- 德國採「重新包裝」法國專案的模式
- 各國策略不同，沒有一體適用的方案

**開源商業模式**
- MIT 授權允許私營公司銷售和商業化
- 專案團隊認為這有利於生態發展
- 部分社群成員擔憂被商業公司「白嫖」後不回饋

### 社群反應

**正面看法**
- 稱讚歐洲政府投入數位主權的嘗試
- BlockNote.js 和 Yjs 開發者感謝法國政府贊助功能開發
- 認為這是「Public Money, Public Code」政策的實際案例

**負面看法**
- 質疑專案規模太小，無法與美國科技巨頭競爭
- 批評技術選擇（Python/Django）可能導致效能問題
- 認為應投入資金支援 LibreOffice 等成熟專案，而非重造輪子

**中立/理性聲音**
- 指出「數位主權」不僅是技術問題，也是政治決策
- 建議關注政府相關活動（如 Hackdays）以推動開源採用
- 歐洲各國需求不同，需要靈活的合作模式

## 技術細節

### Docs 專案架構
- **後端**：Django Rest Framework
- **前端**：Next.js + BlockNote.js
- **即時協作**：Hocuspocus + Yjs（CRDT）
- **部署**：支援 Kubernetes 和 Docker Compose

### 功能特色
- 協作編輯（類似 Google Docs）
- Markdown 語法支援
- AI 功能（重寫、摘要、翻譯等）
- 匯出為 .odt、.docx、.pdf
- 細粒度存取控制

### 授權注意
- 核心專案採用 MIT 授權
- 部分 PDF 匯出功能依賴 GPL 授權的 BlockNote 套件
- 可設定 `PUBLISH_AS_MIT=true` 建構純 MIT 授權版本

## 評價

**值得關注** - 這是一個具有**重要政治意義和潛在技術影響**的專案：

**為什麼重要：**
1. **數位主權實驗**：歐洲首次由政府主導的大規模開源辦公套件合作
2. **MIT 授權策略**：採用對商業友善的授權，可能加速私營部門採用
3. **跨國合作模式**：法德荷合作模式可能成為其他歐洲國家的參考
4. **開源生態贊助**：法國政府贊助 Yjs 和 BlockNote.js 等基礎設施，回饋社群

**需要觀察的風險：**
1. **專案完整性**：目前缺少試算表和簡報工具，能否發展為完整 Office Suite
2. **技術挑戰**：Python/Django 技術棧能否支撐大規模部署
3. **資金持續性**：政府項目能否在政黨輪替後持續獲得資金支持
4. **社群參與**：專案能否吸引外部開發者貢獻，避免成為「閉門造車」的政府專案

**總結：**
這個故事同時涉及**技術開發**、**政府政策**和**地緣政治**三個層面，討論熱度高（800 分、334 評論），且呈現明顯的意見分歧（政治立場、技術選擇）。雖然專案技術完整度尚有爭議，但其代表的「歐洲數位主權」趨勢值得長期關注。