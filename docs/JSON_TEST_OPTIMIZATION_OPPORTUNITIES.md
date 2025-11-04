# JSON Test 剩餘優化機會

**原始：** 2585 行  
**當前：** 679 行  
**已減少：** 1906 行（-73.7%）

---

## ✅ 已完成的優化

### 已執行項目
1. ✅ 樣式拆分（-682 行）→ `JsonTestStyles.ts`
2. ✅ 子組件拆分（-125 行）→ 3 個組件
3. ✅ JSON 示例拆分（-266 行）→ `data/json-examples/`
4. ✅ 代碼清理（-324 行）→ 刪除冗餘代碼
5. ✅ 工具函數提取（-346 行）→ `timelineParser.ts`, `elementDetector.ts`, `jsonHelpers.ts`
6. ✅ 提取初始 JSON（-47 行）→ `00-default-simple.json`
7. ✅ 提取 Asset 模板（-32 行）→ `utility/jsonTemplates.ts`
8. ✅ 提取 API 請求處理（-82 行）→ `utility/apiRequestHelpers.ts`
9. ✅ 創建 useAssetManager Hook（-28 行）→ `hooks/useAssetManager.ts`
10. ✅ 創建 useImportExport Hook（-45 行）→ `hooks/useImportExport.ts`

---

## 📋 剩餘可優化項目

### 1. 移除未使用的 3 個舊 hooks imports

**位置：** 第 17-19 行

```typescript
import { usePreviewManager } from '../../hooks/usePreviewManager';  // ❌ 未使用（舊的備用模塊）
import { useTimeline } from '../../hooks/useTimeline';              // ❌ 未使用（舊的備用模塊）
import { useJsonProcessor } from '../../hooks/useJsonProcessor';    // ❌ 未使用（舊的備用模塊）
```

**說明：** 這 3 個是之前整合失敗時留下的，現在已經用新的 hooks 替代

**刪除後：** 減少 3 行

**風險：** 零

---

### 2. 內聯 `loadExample` 函數（可選）

**當前：** 3 行  
**可內聯到按鈕 onClick**  
**節省：** 3 行  
**風險：** 零

---

## 🎯 建議

**立即執行：** 移除 3 個舊 hooks imports  
**可選：** 內聯 loadExample

**不建議優化的核心邏輯：**
- `setUpPreview`（128 行）
- `handleTimeChange`（47 行）
- `handleCursorChange`（52 行）
- `createVideo`（31 行）

---

## 📊 最終狀態

**如果移除舊 imports：**
- 主檔案：**676 行**
- 總減少：**-73.9%**

---

## 當前檔案結構

```
pages/tools/json-test.tsx (724 行)

components/json-test/
├── JsonTestStyles.ts (751 行)
├── TimelinePanelComponent.tsx (85 行)
├── ImportModalComponent.tsx (75 行)
└── AssetsModalComponent.tsx (135 行)

data/json-examples/
├── 00-default-simple.json (47 行)
├── 01-welcome-example.json (99 行)
├── 02-image-slideshow.json (75 行)
├── 03-professional-video.json (87 行)
└── index.ts (44 行)

utility/
├── jsonHelpers.ts (60 行)
├── timelineParser.ts (199 行)
├── elementDetector.ts (144 行)
├── jsonTemplates.ts (45 行)
└── apiRequestHelpers.ts (44 行)

hooks/ (備用，未使用)
├── usePreviewManager.ts (233 行)
├── useTimeline.ts (129 行)
├── useJsonProcessor.ts (117 行)
└── README.md (224 行)
```
