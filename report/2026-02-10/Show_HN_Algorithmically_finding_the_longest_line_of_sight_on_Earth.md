---
story_id: 46943568
hn_url: https://news.ycombinator.com/item?id=46943568
title: "Show HN: Algorithmically finding the longest line of sight on Earth"
verdict: interesting
created_at: 2026-02-10T03:40:58
---

---
story_id: 46943568
hn_url: https://news.ycombinator.com/item?id=46943568
title: "Show HN: Algorithmically finding the longest line of sight on Earth"
verdict: interesting
created_at: 2026-02-10
---

# 2026-02-10: 算法尋找地球上最長視距

**來源：** Hacker News
**故事 ID：** 46943568
**Hacker News 連結：** https://news.ycombinator.com/item?id=46943568
**網址：** https://alltheviews.world
**分數：** 380 | **評論數：** 155

## 摘要

Tom Buckley-Houston 和 Ryan Berger 開發了一套名為 CacheTVS 的自訂算法，使用 Rust 和 SIMD 技術窮舉計算了地球上每一個點的視距（line of sight），最終確認最長的視距是從印度-中國邊境附近的興都庫什山脈到吉爾吉斯斯坦的 Pik Dankova，長達 **530 公里**。這項計算涉及約 10^15 次運算，輸出約 200GB 的數據，並提供了包含超過 10 億條最長視距的互動地圖。

## 為什麼有趣

這是一個**計算地理學與高效能計算**的完美結合：

1. **科學驗證**：首次實證證明了此前僅被推測為最長視距的觀點
2. **技術深度**：從 8 年前的想法到如今的實現，展示了算法優化、資料佈局、CPU cache 利用、SIMD 並行化等多項技術的深度應用
3. **開源精神**：所有程式碼公開於 GitHub，並計畫發表學術論文貢獻給該領域
4. **硬核計算**：使用數百個 AMD Turin 核心、數百 GB RAM、數 TB 磁碟空間，運行 2 天完成全球計算
5. **互動體驗**：提供互動地圖讓使用者探索任何點的最長視距

## 技術亮點

### 算法創新：Total Viewshed 計算

傳統的視距算法每次計算一個點的可見區域（viewshed），對於單一點尚可，但要計算全球每個點則不可行。他們開發的「Total Viewshed」算法：

- **空間旋轉技巧**：不為每個點繪製 360 條視線，而是旋轉整個高程網格 360 次
- **記憶體局部性**：旋轉確保記憶體順序讀取，大幅提升 cache 命中率
- **「巧克力棒」優化**：只旋轉中心矩形區域，而非整個網格

### 核心算法流程

```
對於每個觀察點：
1. 對高程資料進行方位角等距投影（Azimuthal Equidistant Projection）
2. 考慮地球曲率和光線折射調整高程值
3. 計算視線上每個點的仰角
4. 若當前仰角大於所有先前點的最大仰角，則該點可見
5. 記錄最遠的可見點
```

### 效能優化技術

1. **避免三角函數**：由於只需要比較仰角大小，不需實際計算 tan^-1，因為它是連續單調遞增函數
2. **Delta 取代指標**：使用位置無關的偏移量取代 linked list，減少記憶體跳躍
3. **SIMD 並行化**：使用 Rust 的 SIMD 指令同時處理多個資料點
4. **多執行緒處理**：充分利用多核 CPU
5. **Tile 打包策略**：將地球表面分割為 2,489 個不同大小的 tiles，每個 tile 獨立計算

### 資料處理管道

- **來源**：NASA 的 Shuttle Radar Topography Mission (SRTM)，70GB 的光柵資料
- **投影**：局部錨定的 tile 特定方位角等距投影（AEQD），最小化距離和角度誤差累積
- **輸出**：約 45 億條最長視距，壓縮後可用於互動地圖

## 主要發現

### 最長視距 Top 3

1. **興都庫什山脈 → Pik Dankova（吉爾吉斯斯坦）**：530km
2. **Antioquia（哥倫比亞）→ Pico Cristobal**：504km
3. **Elbrus 山（俄羅斯）→ 龐廷山脈（土耳其）**：483km

### 地理洞察

- 最長的視距往往聚集在高峰和山脊附近
- 俄羅斯與土耳其不接壤，但從 Elbrus 山可以看到土耳其的山脈
- 理論最長視距與實際最長視距有顯著差距（Everest 估算 670km，但實際未發現超過 530km 的視距）

## 主要討論點

### 技術討論

- **折射係數**：約 0.13 的折射係數如何影響計算結果
- **投影系統**：如何在球體表面上進行距離投影的複雜性
- **Cache 效率**：資料佈局對 CPU 效能的決定性影響
- **Rust 的優勢**：安全性與效能的平衡，適合高效能計算

### 實際應用

- **戶外探索**：幫助登山者找到最佳觀景點
- **科學研究**：氣象學、地質學、無線電通訊等領域的應用
- **教育用途**：幫助理解地球曲率、大氣折射等概念

### 資料與開源

- 程式碼已於 GitHub 開源：github.com/AllTheLines/CacheTVS
- 計畫撰寫學術論文發表算法
- 互動地圖：map.alltheviews.world

## 評價

**極度推薦閱讀** - 這是一個技術深度與實際應用完美結合的專案：

✅ **算法創新**：對 Total Viewshed 問題提出了顯著的改進
✅ **工程實踐**：從想法到全球規模實現的完整工程故事
✅ **開源貢獻**：程式碼開源，計畫發表論文
✅ **科學價值**：首次實證確定地球最長視距
✅ **互動體驗**：讓讀者能親自探索結果

Tom 的 8 年堅持從最初在印尼爪哇島的好奇心，到如今與 Ryan 合作實現全球計算，展現了個人專案如何透過技術創新和持續優化達成看似不可能的目標。這個故事對任何對高效能計算、地理資訊系統、Rust 程式設計或計算地理學感興趣的人都極具啟發性。

特別值得閱讀他們的技術部落格：
- Tom 的文章：https://tombh.co.uk/longest-line-of-sight
- Ryan 的技術解析：https://ryan.berge.rs/posts/total-viewshed-algorithm