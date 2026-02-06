---
story_id: 46886440
hn_url: https://news.ycombinator.com/item?id=46886440
title: "A case study in PDF forensics: The Epstein PDFs"
verdict: technical
created_at: 2026-02-06T08:37:48
---

---
story_id: 46886440
hn_url: https://news.ycombinator.com/item?id=46886440
title: "A case study in PDF forensics: The Epstein PDFs"
verdict: technical
created_at: 2026-02-06T00:00:00
---

# 2026-02-06: PDF 取證案例研究：Epstein 文件

**來源：** Hacker News
**故事 ID：** 46886440
**Hacker News 連結：** https://news.ycombinator.com/item?id=46886440
**網址：** https://pdfa.org/a-case-study-in-pdf-forensics-the-epstein-pdfs/
**分數：** 397 | **評論數：** 224

## 摘要

PDF Association 發布了一份關於美國司法部根據「Epstein Files Transparency Act」釋出的 PDF 文件之技術取證分析。研究人員從純數位取證角度檢查了這些文件，發現 DoJ 的紅色塗銷（redaction）技術相當完善，並沒有如部分媒體報導所稱的可恢復隱藏文字，同時揭示了一些文件可能是「假掃描」（fake scans）──即從數位文件轉換為圖像以消除元數據。

## 為什麼有趣

這是一個**技術價值極高**的取證案例，因為：

1. **PDF 格式的複雜性展示**：文章深入探討 PDF 的二進位結構、增量更新（incremental updates）、xref 表、版本號等技術細節，說明為何 PDF 分析比其他文件格式更具挑戰性

2. **工具驗證的重要性**：研究顯示兩個不同的 `pdfinfo` 工具對同一組文件的 PDF 版本報告出現巨大差異（一個報告 3,817 個 PDF 1.3，另一個只報告 209 個），強調了「永遠不要信任單一工具」的數位取證原則

3. **假掃描檢測技術**：透過測量頁面傾斜度（skew）、檢查圖像雜訊（noise）、背景質地等特徵，識別出原本是數位文件卻被偽裝成掃描文件的案例，這在文件真偽鑑定中具有重要應用

4. **紅色塗銷技術的正確性**：確認 DoJ 在 EFTA 文件集中使用了正確的「黑盒式」塗銷，與早期其他 DoJ 文件中錯誤的塗銷方式形成對比

## 主要討論點

**PDF 格式技術深入分析：**
- **增量更新追蹤**：PDF 支援將修訂版本附加到原始文件的功能，通過分析 `%%EOF` 標記和 xref 表可以重建文件的編輯歷史
- **Bates Numbering 系統**：所有 EFTA 釋出的 PDF 都有以「EFTA」開頭的 Bates 編號，這是識別官方釋出文件的重要標記
- **文件有效性評估**：使用多個工具檢查發現僅有 109 個 PDF 有微小的 FontDescriptor Descent 值錯誤（應為負值），不影響整體有效性

**假掃描檔案的識別：**
- 部分文件「過於完美」──沒有真實掃描的隨機雜訊、背景質地，且多頁有完全相同的傾斜角度
- 社群成員分享使用 ImageMagick 製作假掃描的 one-liner 腳本，展示如何添加隨機旋轉、雜訊、線性拉伸等效果
- 討論這種「假掃描」行為的動機：可能是員工圖方便（laziness）以避免實際列印掃描，但也可能是有意消除元數據

**取證工具的差異：**
- 不同工具對 PDF 版本檢測的結果差異巨大，強調數位取證中交叉驗證的重要性
- Tool B 未正確處理增量更新中的 Version entry，導致統計錯誤

**Stylometry（筆跡學）討論：**
- 部分評論探討是否可透過寫作風格分析在 4chan 等平台上識別 Epstein 或 Maxwell 的匿名發文
- 社群分享 stylometry 的技術原理：結合寫作風格、詞彙、發文時間等多維度數據進行身份識別
- 有人提出使用 AI 瀏覽器助手隨機化寫作風格以抵抗 stylometry 分析的想法

**對媒體報導的澄清：**
- 文章澄清多家媒體（包括 Guardian、New York Times、Forbes）錯誤報導「可恢復的紅色塗銷」
- 這些錯誤報導混淆了 EFTA 文件集與其他早期 DoJ 釋出的文件（後者確實有塗銷問題）

## 評價

**技術價值高** - 這是一個極佳的 PDF 取證教學案例，展現了：
- 專業的數位取證方法論
- PDF 格式的技術深度
- 文件真偽鑑定的實務技術
- 取證工具交叉驗證的重要性

對於任何從事資安、數位取證、文件分析工作的人來說，這篇文章提供了寶貴的實戰經驗和技術見解。即使不專注於此領域，也展示了看似簡單的 PDF 文件背後隱藏的技術複雜性。