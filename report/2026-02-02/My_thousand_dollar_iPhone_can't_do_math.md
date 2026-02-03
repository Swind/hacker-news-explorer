---
story_id: 46849258
hn_url: https://news.ycombinator.com/item?id=46849258
title: "My thousand dollar iPhone can't do math"
verdict: interesting
created_at: 2026-02-02T13:44:53
---

---
story_id: 46849258
hn_url: https://news.ycombinator.com/item?id=46849258
title: "My thousand dollar iPhone can't do math"
verdict: interesting
created_at: 2026-02-02T14:30:00
---

# 2026-02-02: iPhone 16 Pro Max 執行 MLX LLM 產生錯誤輸出

**來源：** Hacker News
**故事 ID：** 46849258
**Hacker News 連結：** https://news.ycombinator.com/item?id=46849258
**網址：** https://journal.rafaelcosta.me/my-thousand-dollar-iphone-cant-do-math/
**分數：** 156 | **評論數：** 152

## 摘要

一位開發者發現他的 iPhone 16 Pro Max 在執行 Apple 的 MLX 框架運行 LLM 時產生完全錯誤的輸出，而同樣的程式碼在 iPhone 15 Pro 和 MacBook Pro 上都能正常運作。經過詳細的 debug 過程，他發現問題來自於硬體缺陷——iPhone 16 Pro Max 的 Neural Engine 或相關 ML 系統存在數值計算錯誤，張量（tensor）輸出的數值相差數個數量級。後續更新顯示 Apple 發布了修復，且作者在 iPhone 17 Pro Max 上測試確認一切正常。

## 為什麼有趣

這是一個**技術偵探故事**，具有重要的工程啟示：

1. **硬體除錯的挑戰**：作者花了 3 天時間懷疑自己的程式碼和能​​力，最後才發現是 $1,400 手機的硬體問題
2. **Apple ML 生態問題**：揭示了 Apple Intelligence 下載失敗（12 頁用戶投訴）可能與此硬體問題相關
3. **科學除錯方法**：作者使用 breakpoint 比較不同裝置的 tensor 值，發現 iPhone 16 Pro Max 的數值完全偏離正常範圍
4. **Apple 的回應**：Apple 在文章發布後一天（1 月 29 日）發布了修復，顯示這是裝置偵測問題，而非普遍硬體缺陷

## 主要討論點

### 技術根因分析

評論中的技術深度分析指出：

- **裝置偵測錯誤**：iPhone 16 Pro SKU 被錯誤偵測為支援 Neural Accelerator (NAX)，導致錯誤結果
- **GPU 架構差異**：A19 Pro 的 GPU 架構為 17，包含 GPU tensor cores，與舊款不同
- **MLX 的優化策略**：MLX 嘗試利用每個平台優勢，但在特定裝置上做出了錯誤選擇
- **Apple 文檔問題**：Apple 的文檔被評論者批評為「垃圾」，MLX 使用了許多未記錄的 Metal 屬性

### Apple Neural Engine vs Neural Accelerator

社群澄清了兩個不同的概念：

- **Apple Neural Engine (ANE)**：存在多年，專門用於小型、省電模型（如文字提取、深度建模），不適合 LLM
- **Neural Accelerator (NAX)**：較新的 GPU 區塊內的神經加速支援，用於更通用的神經網路運算
- MLX 目前不支援 ANE，因為其 API 是封閉的

### 浮點數計算的討論

評論中展開了深入的技術辯論：

- **浮點數不確定性**：不同裝置、編譯器優化、記憶體對齊都會導致浮點數結果不同
- **IEEE 754 規範**：關於 NaN 傳播的保證引發了技術辯論
- **除錯教訓**：「永遠不要假設浮點函式在不同電腦上會評估出相同結果」

### 開發者心理與除錯哲學

- **冒名頂替症候群**：作者認為自己無能，實際上是硬體缺陷
- **物理層考量**：除錯時應該總是考慮實體層面的可能性
- **Apple 支援體驗**：討論了重新安裝 OS 的痛苦流程（需要重新加入銀行卡、Face ID、所有應用程式登入）

## 技術細節

作者使用的除錯方法：

```
1. 使用已知的可靠模型（量化版 Gemma，適合記憶體）
2. 簡單提示："What is 2+2?"
3. 溫度設為 0.0 以消除變異性
4. 在模型層疊代中設置 breakpoint
5. 比較不同裝置的 MLXArray/Tensor 值
```

關鍵發現：

- **iPhone 15 Pro（正常）**：`[[[[53.875, 62.5625, -187.75, ..., 42.625, 6.25, -21.5625]]]]`
- **iPhone 16 Pro Max（異常）**：`[[[[191.5, 23.625, 173.75, ..., 1298, -147.25, -162.5]]]]`

數值相差數個數量級，但輸入相同，證明中途計算出現嚴重錯誤。

## 後續發展

1. **Apple 修復**：1 月 29 日發布修復，限制了 NAX kernel 只在 iPhone 17 Pro 或更新機型上使用
2. **作者驗證**：2 月 1 日使用 iPhone 17 Pro Max 測試，確認一切正常
3. **結論**：這是特定 iPhone 16 Pro Max 實例的硬體/韌體問題，非普遍缺陷

## 評價

**值得關注 / 有趣**

這是一個極佳的技術除錯案例研究，展示了：

✅ **系統性除錯方法**：從懷疑程式碼到懷疑編譯器到最終發現硬體問題
✅ **工程素養**：使用科學方法比較不同裝置的輸出
✅ **Apple 生態挑戰**：Apple Intelligence 普遍失敗可能與此相關
✅ **硬體品質控制**：高價裝置也可能出現嚴重缺陷
✅ **社群價值**：技術深度討論（浮點數、GPU 架構、裝置偵測）

對於 Apple 平台 ML 開發者和關注硬體可靠性的工程師來說，這是一個重要的警訊和學習案例。