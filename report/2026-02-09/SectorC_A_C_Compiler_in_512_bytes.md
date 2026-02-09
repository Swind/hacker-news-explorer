---
story_id: 46925741
hn_url: https://news.ycombinator.com/item?id=46925741
title: "SectorC: A C Compiler in 512 bytes"
verdict: technical
created_at: 2026-02-09T10:46:13
---

# 2026-02-09: SectorC: A C Compiler in 512 bytes

**來源：** Hacker News
**故事 ID：** 46925741
**Hacker News 連結：** https://news.ycombinator.com/item?id=46925741
**網址：** https://xorvoid.com/sectorc.html
**分數：** 378 | **評論數：** 79

## 摘要

SectorC 是一個用 x86-16 assembly 編寫的 C compiler，能夠完全容納在 x86 機器的 512 byte boot sector 中。它支援相當大的 C subset，足夠編寫真實且有趣的程式，被認為可能是史上最小的 C compiler。這個專案展現了極致的程式碼優化與創意的編譯器設計技巧。

## 為什麼有趣

這是一個**極致的技術成就**，原因如下：

1. **極限挑戰**：在 512 bytes（0.5KB）的空間內實作完整的 C compiler，幾乎是不可能的任務
2. **創意解決方案**：使用獨特的技術克服限制：
   - 使用 `atoi()` 作為 hash function 來識別 tokens
   - 設計 "Barely C" 語言，使用空格作為主要 delimiter
   - 利用 byte-threaded code 概念（最終未採用但記錄了想法）
   - 大量使用 assembly 優化技巧（fall-through、tail-calls、stosw/lodsw 等）

3. **教育價值**：展示了 C 語言的核心本質有多麼簡潔，以及編譯器的基本架構

4. **懷舊情懷**：讓人回想起早期計算時代，程式設計更接近機器層面的魔法時期

## 主要討論點

**技術深入：**
- Hash collision 問題：使用 `atoi()` 作為 hash function 可能導致不同 identifiers 碰撞，作者選擇忽視這個問題
- Boot sector magic：512 bytes 是傳統硬碟 boot sector 的大小，是 x86 架構的歷史遺產
- 語言 subset vs 完整 C：這是一個 C subset compiler，但能夠編譯真正的 C 程式

**設計決策：**
- Barely C 語法：`int(main)(){while(!done){` 使用空格創造 "mega-tokens"
- 操作符實作：使用 4-byte table entries（16-bit token + 16-bit machine code）支援 14 種操作符
- 符號表：變數使用 hash value 直接存取 64K segment，沒有傳統符號表

**社群反應：**
- 讚嘆極致優化的精神：「這種專案提醒你現代開發與實際機器有多麼遙遠」
- 懷舊共鳴：「boot sector programming 有種懷舊的魔法，當程式設計真正有趣且展現技巧」
- 實用性討論：可能用於 bootstrapping chains，從極小的平台特定 binary 逐步構建複雜工具

**幽默評論：**
- 「如果這個實作存在於 1980 年代，C 標準會有一個規則：不同 tokens hash 到相同 16-bit 值會觸發 undefined behavior」
- 「現代 Hello World 需要 200MB 的 node_modules，有人卻把 C compiler 放進 512 bytes」

## 評價

**技術價值極高** ⭐⭐⭐⭐⭐

這是一個令人驚嘆的工程成就：
- 展現了對 x86-16 architecture 的深度理解
- 創新的編譯器設計思維，用非常規手段解決不可能的問題
- 優秀的文件說明，詳細記錄設計過程與失敗嘗試
- 真正可用的 compiler，能編譯複雜程式（如 sine wave animation）
- 高教育價值，是理解編譯器原理的絕佳案例

這種專案代表了程式設計最純粹的樂趣：在極限限制下，用創意與技巧創造看似不可能的成果。