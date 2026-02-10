---
story_id: 46935791
hn_url: https://news.ycombinator.com/item?id=46935791
title: "I put a real-time 3D shader on the Game Boy Color"
verdict: technical
created_at: 2026-02-10T03:39:18
---

---
story_id: 46935791
hn_url: https://news.ycombinator.com/item?id=46935791
title: "I put a real-time 3D shader on the Game Boy Color"
verdict: technical
created_at: 2026-02-10T00:00:00
---

# 2026-02-10: 在 Game Boy Color 上實現即時 3D 著色器

**來源：** Hacker News
**故事 ID：** 46935791
**Hacker News 連結：** https://news.ycombinator.com/item?id=46935791
**網址：** https://blog.otterstack.com/posts/202512-gbshader/
**分數：** 329 | **評論數：** 60

## 摘要

作者開發了一個在 Game Boy Color 上執行的即時 3D 著色器遊戲。玩家可以控制環繞的光源並旋轉 3D 物件（茶壺和 Game Boy Color 本身）。這個專案克服了 GBC 硬體的極致限制——沒有乘法指令、沒有浮點運算、只有 8MHz CPU——透過對數查表法和自修改代碼技巧實現了每像素的 Lambert 著色計算。

## 為什麼這是技術成就

**極限硬體限制下的創新解法：**

1. **沒有乘法指令的解決方案**：Game Boy 的 SM83 CPU 不支援乘法和浮點運算，作者使用對數將乘法轉換為加法，透過查表法完成計算。

2. **數學優化**：使用球坐標系統重寫點積公式，固定 L-theta 為常數，讓玩家只能控制 L-phi（軌道光源效果）。

3. **8-bit 分數運算**：所有數值限制在單一位元組，使用對數空間編碼，利用 XOR 運算處理正負號。

4. **自修改代碼**：將硬編碼的數值直接寫入指令中，避免從記憶體載入變數，每像素節省 12 週期。

5. **效能數據**：
   - 每像素約 130 週期
   - 每幀處理 15 個 tiles
   - 使用 89% 的可用 CPU 時間
   - 60 FPS 運行

## 技術細節

### Normal Map 編碼

ROM 中每個像素儲存為 3-byte tuple `(cosθ, cosφ, sinφ)`，預先計算常數係數 α 和 β。

### 核心著色計算

```
結果 = α × cos(L_θ - N_θ) + β × cos(L_φ - N_φ)
```

每像素需要：
- 1 次減法
- 1 次 cos_log 查表
- 1 次加法
- 1 次 pow 查表
- 1 次加法

共 3 次加減法、2 次查表。

### 視覺優化

- 故意的 tearing 效果（分幀渲染不同部分）
- 利用 LCD ghosting 掩蓋撕裂
- 透明/空行像素僅需 3 週期處理

## 主要討論點

**技術評論：**
- 這是「假 3D」嗎？社群指出這與現代 deferred rendering 類似——著色器在 2D buffer 上運算，幾何來源不重要
- 與 90 年代 Mac 遊戲的 2D 紋理光照技術類似，但在 GBC 上實現更令人印象深刻
- 有人提到 imposter 技術在現代遊戲引擎中也有應用

**AI 與手工編程：**
- 作者嘗試使用 AI 編寫 Game Boy assembly 但失敗了
- 95% 的代碼是手工編寫
- 引發了關於 AI 代碼使用披露的討論
- 作者認為披露 AI 使用是誠信問題，但社群意見分歧

**硬體 vs. 模擬器：**
- 讚賞這是在真實 CGB 硬體上運行，不是「外接 FPGA 的假 GBC」
- 有人提到 ModRetro Clone 等現代替代品
- 討論了真實硬體收藏與模擬器的便利性取捨

**Demoscene 文化：**
- 有人建議作者將這個作品提交到 demoparty 比賽
- 這種極限優化的精神正是 demoscene 的核心

## 評價

**技術價值極高** (⭐⭐⭐⭐⭐)

這是一個**傑出的逆向工程和優化範例**：
- 在不可能的硬體上實現了不可能的效果
- 展現了對底層系統的深度理解
- 創造性地應用數學解決硬體限制
- 完整的技術文檔和開源代碼

雖然評論數量中等（60），但這是因為技術門檻高，討論質量很高。這類 retro-computing 極限挑戰正是 Hacker News 社群最欣賞的技術成就之一。

**值得學習的地方：**
- 對數空間乘法的巧妙應用
- 自修改代碼的性能優化
- 在限制下的創造性問題解決
- 完整的技術分享精神