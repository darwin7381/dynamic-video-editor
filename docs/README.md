# 📚 Creatomate 專案文檔索引

## 文檔概覽

本目錄包含所有關於 Creatomate Preview SDK 和 API 的深度技術文檔。

**最後更新**：2025年10月29日

---

## 🎯 快速導航

### 🔥 最新文檔（推薦閱讀）

1. **[研究驗證總結報告](./research-verification-summary.md)** ⭐ **必讀**
   - 完整驗證另一個 AI 的研究發現
   - 95% 準確度評分
   - 包含詳細的驗證方法論
   - 適合：想快速了解全貌的開發者

2. **[Creatomate Preview SDK 深度技術分析](./creatomate-preview-sdk-deep-dive.md)** ⭐ **技術深度**
   - 完整的技術架構分析
   - 所有主張都有原始碼證據
   - 包含實際程式碼範例
   - 適合：需要深入理解機制的開發者

### 📖 問題排查與解決方案

3. **[外部圖片載入問題分析](./external-image-issue-analysis.md)**
   - 問題診斷過程
   - 代理方案實作細節
   - 適合：遇到外部素材載入問題的開發者

### 📋 API 參考

4. **[Creatomate API 知識庫](./creatomate-api-knowledge.md)**
   - API 請求格式
   - 命名規則說明
   - 官方範例學習
   - 適合：使用 Creatomate API 的開發者

### 🔄 技術選型

5. **[影片編輯框架評估](./video-editing-frameworks-evaluation.md)**
   - Creatomate vs Remotion vs FFmpeg
   - 各框架優缺點比較
   - 適合：考慮替代方案的開發者

---

## 📊 文檔關係圖

```
研究驗證總結報告 (入口文檔)
    │
    ├─→ Creatomate Preview SDK 深度分析 (技術細節)
    │       │
    │       ├─→ 外部圖片載入問題分析 (實際問題)
    │       │
    │       └─→ Creatomate API 知識庫 (API 參考)
    │
    └─→ 影片編輯框架評估 (技術選型)
```

---

## 🎓 學習路徑

### 路徑 1：快速上手

1. 閱讀 [研究驗證總結報告](./research-verification-summary.md) - 10 分鐘
2. 瀏覽 [外部圖片載入問題分析](./external-image-issue-analysis.md) - 5 分鐘
3. 開始使用現有的代理方案

**適合**：需要快速解決問題的開發者

### 路徑 2：深度學習

1. 閱讀 [Creatomate Preview SDK 深度分析](./creatomate-preview-sdk-deep-dive.md) - 30 分鐘
2. 實際查看原始碼 `node_modules/@creatomate/preview/src/Preview.ts`
3. 測試 `cacheAsset()` 和 `setCacheBypassRules()` API
4. 參考實際程式碼範例進行整合

**適合**：想要完全理解底層機制的開發者

### 路徑 3：技術選型

1. 閱讀 [影片編輯框架評估](./video-editing-frameworks-evaluation.md) - 15 分鐘
2. 閱讀 [Creatomate Preview SDK 深度分析](./creatomate-preview-sdk-deep-dive.md) - 30 分鐘
3. 評估是否需要切換到其他框架

**適合**：正在評估技術方案的架構師

---

## 🔍 問題速查表

| 問題 | 參考文檔 | 章節 |
|------|---------|------|
| 外部圖片/影片無法載入 | [外部圖片載入問題分析](./external-image-issue-analysis.md) | 解決方案分析 |
| 如何使用 cacheAsset()? | [Preview SDK 深度分析](./creatomate-preview-sdk-deep-dive.md) | 實際程式碼範例 → 範例 1 |
| 如何設定快取白名單? | [Preview SDK 深度分析](./creatomate-preview-sdk-deep-dive.md) | 實際程式碼範例 → 範例 2 |
| Preview SDK 如何運作? | [Preview SDK 深度分析](./creatomate-preview-sdk-deep-dive.md) | 運作機制詳解 |
| v1.4 改了什麼? | [Preview SDK 深度分析](./creatomate-preview-sdk-deep-dive.md) | 版本差異分析 |
| API 請求格式? | [Creatomate API 知識庫](./creatomate-api-knowledge.md) | API 請求格式 |
| 是否該用 Remotion? | [影片編輯框架評估](./video-editing-frameworks-evaluation.md) | 詳細對比 |
| 研究可信嗎? | [研究驗證總結報告](./research-verification-summary.md) | 詳細評分表 |

---

## 🎯 核心概念速覽

### iframe 架構

```
你的網頁
  └─ Preview SDK (控制器)
      └─ iframe → creatomate.com/embed
          └─ 實際渲染引擎
              └─ 素材載入限制在這裡
```

### 三大解決方案

| 方案 | 優點 | 適用場景 | 文檔位置 |
|------|------|----------|---------|
| **代理方案** | 立即可用 | 所有場景 | [外部圖片分析](./external-image-issue-analysis.md) |
| **cacheAsset()** | 官方支援 | 小檔案、已知來源 | [深度分析](./creatomate-preview-sdk-deep-dive.md) §範例1 |
| **setCacheBypassRules()** | 效能最佳 | 自有 CDN | [深度分析](./creatomate-preview-sdk-deep-dive.md) §範例2 |

### 版本演進關鍵點

- **v1.0-1.3**：外部素材快取較寬鬆
- **v1.4**：⚠️ 預設停用外部素材快取（破壞性改動）
- **v1.4+**：提供 `setCacheBypassRules()` API
- **v1.6**：提供 `cacheAsset()` API（當前版本）

---

## 📁 文檔詳細說明

### 1. 研究驗證總結報告

**檔案**：`research-verification-summary.md`  
**字數**：~4,500 字  
**閱讀時間**：15 分鐘  
**難度**：⭐⭐ 中等

**內容**：
- ✅ 完整驗證另一個 AI 的技術研究
- ✅ 95% 準確度評分
- ✅ 詳細的驗證方法論
- ✅ 關鍵程式碼片段
- ✅ 學習要點與建議

**適合讀者**：
- 想快速了解研究可信度的開發者
- 需要驗證方法參考的技術人員
- 對技術研究品質感興趣的讀者

---

### 2. Creatomate Preview SDK 深度技術分析

**檔案**：`creatomate-preview-sdk-deep-dive.md`  
**字數**：~6,000 字  
**閱讀時間**：30 分鐘  
**難度**：⭐⭐⭐⭐ 進階

**內容**：
- ✅ 完整的架構分析（含原始碼引用）
- ✅ iframe 機制詳解
- ✅ 版本演進分析
- ✅ API 功能說明（cacheAsset, setCacheBypassRules）
- ✅ 4 個實際程式碼範例
- ✅ 專案整合建議

**適合讀者**：
- 需要深入理解 Preview SDK 的開發者
- 想要實作 cacheAsset 的工程師
- 對底層機制感興趣的技術人員

---

### 3. 外部圖片載入問題分析

**檔案**：`external-image-issue-analysis.md`  
**字數**：~2,500 字  
**閱讀時間**：10 分鐘  
**難度**：⭐⭐ 中等

**內容**：
- ✅ 問題診斷過程
- ✅ Preview vs 渲染模式說明
- ✅ 代理方案實作細節
- ✅ 官方文檔調查結果

**適合讀者**：
- 遇到外部素材載入問題的開發者
- 需要快速解決方案的工程師
- 想了解問題根源的技術人員

---

### 4. Creatomate API 知識庫

**檔案**：`creatomate-api-knowledge.md`  
**字數**：~1,800 字  
**閱讀時間**：8 分鐘  
**難度**：⭐⭐ 中等

**內容**：
- ✅ API 請求格式
- ✅ 命名規則說明（camelCase vs snake_case）
- ✅ 官方範例學習記錄
- ✅ 常見錯誤與解決

**適合讀者**：
- 使用 Creatomate REST API 的開發者
- 需要 API 參考的工程師
- 整合 Creatomate 的後端開發者

---

### 5. 影片編輯框架評估

**檔案**：`video-editing-frameworks-evaluation.md`  
**字數**：~3,800 字  
**閱讀時間**：15 分鐘  
**難度**：⭐⭐⭐ 中高

**內容**：
- ✅ Creatomate vs Remotion vs FFmpeg 詳細對比
- ✅ 各框架優缺點分析
- ✅ 適用場景建議
- ✅ 技術選型決策樹

**適合讀者**：
- 正在選型的技術負責人
- 評估替代方案的架構師
- 對影片編輯技術感興趣的開發者

---

## 🔧 實作指南

### 立即可用的程式碼

所有文檔中的程式碼範例都是**可直接使用**的，包括：

1. **cacheAsset 範例**（深度分析 → 範例 1）
   ```typescript
   // 完整可用的外部圖片載入範例
   ```

2. **setCacheBypassRules 範例**（深度分析 → 範例 2）
   ```typescript
   // 完整可用的白名單設定範例
   ```

3. **代理方案範例**（深度分析 → 範例 3）
   ```typescript
   // 與現有專案整合的範例
   ```

4. **混合策略範例**（深度分析 → 範例 4）
   ```typescript
   // 效能最佳的完整方案
   ```

---

## 📈 文檔品質保證

### 驗證方法

所有技術主張都經過以下驗證：

1. ✅ 直接閱讀原始碼
2. ✅ 檢查型別定義
3. ✅ 驗證 npm 版本歷史
4. ✅ 實際測試程式碼
5. ✅ 對照官方文檔

### 更新策略

- 🔄 SDK 版本更新時重新驗證
- 🔄 發現新資訊時更新文檔
- 🔄 使用者回報問題時補充說明

---

## 💬 回饋與貢獻

如果你發現：
- 📝 文檔有錯誤或不清楚的地方
- 💡 有更好的解決方案
- 🐛 程式碼範例有問題
- 📚 希望補充更多內容

請隨時提出！

---

## 📌 關鍵要點總結

### 外部素材載入問題

**問題**：Preview SDK 的 JSON 預覽無法載入外部素材

**根本原因**：
- Preview SDK 透過 iframe 運作
- iframe 載入自 `creatomate.com/embed`
- 素材載入受該網域安全策略限制
- v1.4 起預設停用外部素材快取

**解決方案**（三選一或混合）：
1. **代理方案**（已實作）：`/api/media-proxy`
2. **cacheAsset()**：預先載入 Blob
3. **setCacheBypassRules()**：設定白名單

### 技術架構理解

**Preview SDK 的運作方式**：
```
外層 SDK (你的控制) → postMessage → iframe (Creatomate 控制)
```

**關鍵限制**：
- 同源政策阻止直接操作 iframe
- 只能透過 postMessage 通訊
- 素材載入環境屬於 Creatomate 網域

### 版本重要性

**v1.4.0 是分水嶺**：
- 之前：外部素材較寬鬆
- 之後：預設停用外部素材快取
- 同時提供官方解決方案 API

---

**文檔維護者**：AI Assistant  
**最後更新**：2025年10月29日  
**文檔版本**：1.0.0

