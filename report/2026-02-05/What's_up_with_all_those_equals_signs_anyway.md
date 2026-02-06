---
story_id: 46868759
hn_url: https://news.ycombinator.com/item?id=46868759
title: "What's up with all those equals signs anyway?"
verdict: interesting
created_at: 2026-02-05T04:20:52
---

---
story_id: 46868759
hn_url: https://news.ycombinator.com/item?id=46868759
title: "What's up with all those equals signs anyway?"
verdict: interesting
created_at: 2026-02-05T14:30:00
---

# 2026-02-05: What's up with all those equals signs anyway?

**來源：** Hacker News
**故事 ID：** 46868759
**Hacker News 連結：** https://news.ycombinator.com/item?id=46868759
**網址：** https://lars.ingebrigtsen.no/2026/02/02/whats-up-with-all-those-equals-signs-anyway/
**分數：** 667 | **評論數：** 189

## 摘要

這篇文章解釋了最近在 Twitter 上流傳的舊郵件截圖中出現大量等號的技術原因。這不是什麼神秘代碼或 OCR 掃描錯誤，而是由於「quoted-printable」編碼處理不當所造成的格式損壞。

## 為什麼有趣

這篇文章在 Hacker News 引起熱烈討論是因為它結合了以下元素：

**技術深度：** 深入解釋了 quoted-printable 編碼的工作原理，這是電子郵件傳輸中重要的編碼標準。作者詳細說明了：
- 軟換行（soft line break）使用 `=CRLF` 標記
- 非ASCII字符使用 `=XX` 十六進位編碼
- CRLF (Windows) 與 LF (Unix) 換行符號的差異

**歷史連結：** 文章提到的這些舊郵件截圖在 Twitter 上廣泛流傳，是當前的網路熱門話題。Hacker News 用戶可能對這些郵件的背景或內容感興趣。

**偵探分析：** 作者像技術偵探一樣，透過分析格式損壞的模式，推斷出處理工具的錯誤邏輯。這種逆向工程的分析方式是工程師喜愛的。

**幽默風格：** 作者以幽默的語氣評論「 whoever processed these mails are incompetent」，並自嘲對 Caribbean islands 的誤解。

## 主要討論點

**Quoted-Printable 編碼：**
- 許多人分享對 quoted-printable 的回憶和經驗
- 討論這個編碼標準在現代郵件系統中的應用
- 有人提到這是「我們為了支援 7-bit 傳輸而做的一些蠢事」

**處理工具的錯誤：**
- 許多人猜測是使用 `sed` 或其他簡單的文字處理工具造成的損壞
- 討論 CRLF 與 LF 轉換時的常見陷阱
- 有人分享類似的格式損壞經驗

**歷史背景：**
- 討論這些郵件的來源和重要性
- 有人提到可能與政治人物或政府相關
- 討論舊郵件保存和轉換的挑戰

**替代解釋：**
- 有人提出其他可能的技術解釋
- 討論是否可能是其他編碼標準（如 base64）的混合使用

**幽默回應：**
- 許多人對作者「專家」身分的幽默來源（ Caribbean islands 與實際技術專業的對比）感到有趣
- 對於「 rock döts」（重音符號）的討論

## 評價

**值得閱讀** — 這是一個完美的技術偵探故事：
- ✅ **技術深度適中：** 解釋了實用的編碼知識，但不會過於理論化
- ✅ **貼近實務：** 許多工程師可能會遇到類似的格式轉換問題
- ✅ **歷史價值：** 讓人理解為什麼現代郵件系統會這樣設計
- ✅ **幽默風格：** 作者的寫作風格生動有趣
- ✅ **實用啟示：** 提醒我們在處理文字轉換時要小心編碼問題

即使你不在乎那些 Twitter 流傳的郵件截圖，這篇文章對 quoted-printable 的解釋也值得一讀，特別是當你需要處理舊的郵件格式或進行文字編碼轉換時。

**技術亮點：** 文章對於 `=CRLF`（軟換行）和 `=XX`（字符編碼）兩種用途的區別解釋得非常清楚，並且正確指出了處理工具在 CRLF → LF 轉換時的錯誤邏輯。這顯示了作者對電子郵件標準的深入理解。