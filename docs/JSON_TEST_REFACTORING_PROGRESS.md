# JSON Test 組件重構進度文檔

## 📋 重構目標

將 `pages/tools/json-test.tsx`（原 2585 行）拆分成多個可維護的模塊，確保代碼質量和功能完整性。

---

## ✅ 已完成項目

### 階段 1：樣式拆分（已完成 ✓）

**完成時間：** 2025-11-04

**成果：**
- ✅ 創建 `components/json-test/` 目錄
- ✅ 創建 `JsonTestStyles.ts`（751 行）
- ✅ 提取所有 58 個 styled-components
- ✅ 在主檔案中 import 樣式組件
- ✅ 刪除主檔案中的舊樣式定義
- ✅ 編譯測試通過（無新增錯誤）

**檔案變化：**
- `pages/tools/json-test.tsx`: 2585 → 1903 行（-26.4%）
- 新增：`components/json-test/JsonTestStyles.ts`: 751 行

**提取的樣式組件：**
- 基礎佈局：Container, Header, MainContent, LeftPanel, RightPanel
- 按鈕：CreateButton, ExampleButton, CopyApiButton, ImportApiButton
- 編輯器：JSONTextarea, AutoHighlightOverlay, ClickedHighlightOverlay, UrlHighlightOverlay
- 時間軸：TimelinePanel, TimelineElement, ElementTime, ElementInfo
- 彈窗：ModalOverlay, ModalContent, ModalHeader, ModalBody
- 素材：AssetsList, AssetItem, AssetInfo, AssetActions
- 其他 30+ 個樣式組件

---

## ✅ 已完成項目（續）

### 階段 3：拆分子組件（已完成 ✓）

**完成時間：** 2025-11-04

**成果：**
- ✅ 創建 `TimelinePanelComponent.tsx`（85 行）
- ✅ 創建 `ImportModalComponent.tsx`（75 行）
- ✅ 創建 `AssetsModalComponent.tsx`（135 行）
- ✅ 在主檔案中替換為新組件
- ✅ 編譯測試通過（無新增錯誤）

**檔案變化：**
- `pages/tools/json-test.tsx`: 1903 → 1778 行（-6.6%，相比原始 -31.2%）
- 新增：`TimelinePanelComponent.tsx`: 85 行
- 新增：`ImportModalComponent.tsx`: 75 行
- 新增：`AssetsModalComponent.tsx`: 135 行

**提取的組件：**
1. **TimelinePanelComponent** - 時間軸控制面板
   - 完整的時間軸元素列表
   - 活躍狀態高亮
   - 點擊跳轉功能
   - 視頻尺寸信息顯示

2. **ImportModalComponent** - JSON 匯入彈窗
   - API 請求格式解析
   - JSON 輸入處理
   - 錯誤處理

3. **AssetsModalComponent** - 素材庫彈窗
   - 類型篩選功能
   - 素材列表展示
   - 複製/載入操作

**型別定義：**
- 所有組件都有完整的 TypeScript Props 介面
- 匯出 `TimelineElementData` 型別供外部使用

---

### 階段 3.5：拆分 JSON 示例（已完成 ✓）

**完成時間：** 2025-11-04

**成果：**
- ✅ 創建 `data/json-examples/` 目錄
- ✅ 提取示例 1：歡迎示例（99 行）
- ✅ 提取示例 2：圖片輪播（75 行）
- ✅ 提取示例 3：專業視頻（87 行）
- ✅ 創建示例索引檔案（37 行）
- ✅ 在主檔案中替換為 import
- ✅ 編譯測試通過

**檔案變化：**
- `pages/tools/json-test.tsx`: 1778 → 1512 行（-14.9%，相比原始 -41.5%）
- 新增：`01-welcome-example.json`: 99 行
- 新增：`02-image-slideshow.json`: 75 行
- 新增：`03-professional-video.json`: 87 行
- 新增：`index.ts`: 37 行

**結構優勢：**
1. **一個示例一個檔案** - 清晰易管理
2. **JSON 格式** - 標準格式，易於編輯和驗證
3. **索引檔案** - 統一管理所有示例
4. **型別定義** - `JsonExample` 介面確保一致性
5. **易於擴展** - 新增示例只需加一個 JSON 檔案

---

## 📝 待辦事項（按優先級排序）

### 階段 2：拆分工具函數（待執行）

**預計減少：** ~300-400 行

**任務清單：**
- [ ] 創建 `utils/jsonTestHelpers.ts`
- [ ] 提取 `parseTimelineElements` 函數（~180 行）
- [ ] 提取 `detectCurrentElement` 函數（~190 行）
- [ ] 提取 `convertToSnakeCase` 函數（出現 4 次，可共用）
- [ ] 提取 `parseTime` 函數（時間字符串解析）
- [ ] 提取 `estimateDuration` 函數（持續時間估算）
- [ ] 添加完整的 TypeScript 型別定義
- [ ] 在主檔案中 import 並替換
- [ ] 刪除主檔案中的舊函數定義
- [ ] 單元測試（可選）
- [ ] 編譯測試

**預期結果：**
- `pages/tools/json-test.tsx`: ~1500-1600 行
- 新增：`utils/jsonTestHelpers.ts`: ~400 行

---

### 階段 3：拆分子組件（待執行）

**預計減少：** ~400-500 行

#### 3.1 TimelinePanel 組件
- [x] 創建 `components/json-test/TimelinePanel.tsx`
- [x] 提取時間軸面板 JSX（~100 行）
- [x] 定義 Props 介面
  ```typescript
  interface TimelinePanelProps {
    timelineElements: TimelineElement[];
    currentState?: PreviewState;
    activeElementIndices: number[];
    currentEditingElement: number;
    onSeekToTime: (time: number, index: number, path: string) => void;
  }
  ```
- [x] 測試時間軸互動功能

#### 3.2 ImportModal 組件
- [x] 創建 `components/json-test/ImportModal.tsx`
- [x] 提取匯入彈窗 JSX（~50 行）
- [x] 定義 Props 介面
  ```typescript
  interface ImportModalProps {
    show: boolean;
    jsonInput: string;
    onClose: () => void;
    onImport: (json: string) => void;
    onInputChange: (value: string) => void;
  }
  ```
- [x] 測試匯入功能

#### 3.3 AssetsModal 組件
- [x] 創建 `components/json-test/AssetsModal.tsx`
- [x] 提取素材彈窗 JSX（~100 行）
- [x] 定義 Props 介面
  ```typescript
  interface AssetsModalProps {
    show: boolean;
    selectedType: 'all' | CreatomateAsset['type'];
    filteredAssets: CreatomateAsset[];
    onClose: () => void;
    onTypeChange: (type: 'all' | CreatomateAsset['type']) => void;
    onCopyAsset: (asset: CreatomateAsset) => void;
    onLoadAsset: (asset: CreatomateAsset) => void;
  }
  ```
- [x] 測試素材選擇功能

#### 3.4 JsonEditor 組件（可選）
- [ ] 創建 `components/json-test/JsonEditor.tsx`（跳過，暫不拆分）
- [ ] 提取 JSON 編輯器 + 高亮層 JSX（~80 行）
- [ ] 整合三層高亮系統
- [ ] 測試編輯和高亮功能

**預期結果：**
- `pages/tools/json-test.tsx`: ~1000-1100 行
- 新增 3-4 個組件檔案

---

### 階段 4：拆分 Hooks（待執行）

**預計減少：** ~300-400 行

#### 4.1 usePreviewManager Hook
- [ ] 創建 `hooks/usePreviewManager.ts`
- [ ] 提取 Preview SDK 初始化邏輯
- [ ] 提取 `setUpPreview` 函數
- [ ] 提取 `loadJSON` 函數
- [ ] 提取 `createVideo` 函數
- [ ] 管理 preview ref 和 state
- [ ] 返回介面：
  ```typescript
  {
    previewRef,
    previewReady,
    isLoading,
    error,
    currentState,
    setUpPreview,
    loadJSON,
    createVideo
  }
  ```

#### 4.2 useTimeline Hook
- [ ] 創建 `hooks/useTimeline.ts`
- [ ] 提取時間軸管理邏輯
- [ ] 提取 `handleTimeChange` 函數
- [ ] 提取 `seekToTime` 函數
- [ ] 管理 timelineElements state
- [ ] 管理 activeElementIndices state
- [ ] 返回介面：
  ```typescript
  {
    timelineElements,
    activeElementIndices,
    currentEditingElement,
    handleTimeChange,
    seekToTime
  }
  ```

#### 4.3 useJsonProcessor Hook
- [ ] 創建 `hooks/useJsonProcessor.ts`
- [ ] 提取 JSON 處理邏輯
- [ ] 提取 URL 快取邏輯
- [ ] 提取 GIF 轉換邏輯
- [ ] 管理 processedSource state
- [ ] 管理 urlMapping state
- [ ] 管理 urlStatus state
- [ ] 返回介面：
  ```typescript
  {
    processedSource,
    urlMapping,
    urlStatus,
    processJson
  }
  ```

**預期結果：**
- `pages/tools/json-test.tsx`: ~600-700 行
- 新增 3 個 hooks 檔案

---

### 階段 5：最終優化（待執行）

- [ ] 代碼審查與優化
- [ ] 添加 JSDoc 註釋
- [ ] 性能優化（memo, useMemo）
- [ ] 錯誤處理改進
- [ ] 更新相關文檔
- [ ] 創建組件使用範例

---

## 📊 預期最終結構

```
pages/tools/json-test.tsx (~600-700 行)
├── components/json-test/
│   ├── JsonTestStyles.ts (751 行) ✅
│   ├── TimelinePanel.tsx (~150 行)
│   ├── ImportModal.tsx (~100 行)
│   ├── AssetsModal.tsx (~150 行)
│   └── JsonEditor.tsx (~120 行, 可選)
├── hooks/
│   ├── usePreviewManager.ts (~200 行)
│   ├── useTimeline.ts (~150 行)
│   └── useJsonProcessor.ts (~100 行)
└── utils/
    └── jsonTestHelpers.ts (~400 行)
```

**總行數：** 2600+ 行（與原始相同）  
**主檔案：** 600-700 行（減少 73%）  
**模塊化：** 10+ 個獨立檔案

---

## 🔒 安全原則

每個階段都遵循以下原則：

1. ✅ **先複製，後刪除**（不直接剪下）
2. ✅ **一次只拆一個部分**（不同時拆多個）
3. ✅ **每次拆分後立即測試**（不累積測試）
4. ✅ **保持 Git commit 顆粒度小**（方便回滾）
5. ✅ **使用 TypeScript 嚴格模式**（型別錯誤提前發現）
6. ✅ **編譯測試必須通過**（`npm run build`）
7. ✅ **功能測試必須通過**（實際運行頁面）

---

## 📝 測試檢查清單

每個階段完成後都需要檢查：

- [ ] `npm run build` 成功
- [ ] TypeScript 無新增錯誤
- [ ] ESLint 無新增警告
- [ ] 頁面正常渲染
- [ ] JSON 編輯功能正常
- [ ] 預覽功能正常
- [ ] 時間軸跳轉正常
- [ ] 高亮功能正常
- [ ] 彈窗開關正常
- [ ] API 請求功能正常

---

## 📅 時間記錄

| 階段 | 開始時間 | 完成時間 | 耗時 | 狀態 |
|------|----------|----------|------|------|
| 階段 1：樣式拆分 | 2025-11-04 | 2025-11-04 | ~20 分鐘 | ✅ 完成 |
| 階段 3：子組件 | 2025-11-04 | 2025-11-04 | ~25 分鐘 | ✅ 完成 |
| 階段 3.5：JSON 示例 | 2025-11-04 | 2025-11-04 | ~15 分鐘 | ✅ 完成 |
| 階段 2：工具函數 | - | - | - | 待執行 |
| 階段 4：Hooks | - | - | - | 待執行 |
| 階段 5：最終優化 | - | - | - | 待執行 |

---

## 🎯 下一步行動

**建議順序：**
1. ✅ 階段 1 已完成，先測試頁面運行
2. 執行階段 2（拆分工具函數）
3. 執行階段 3（拆分子組件）
4. 執行階段 4（拆分 Hooks）
5. 執行階段 5（最終優化）

**當前可執行命令：**
```bash
# 測試當前狀態
npm run dev

# 訪問測試頁面
open http://localhost:3000/tools/json-test
```

---

## 📌 注意事項

1. **不要急於一次完成所有拆分**，每個階段都要充分測試
2. **保持 Git 提交頻率**，每完成一個小步驟就 commit
3. **如果遇到問題**，立即 Git revert 回到上一個穩定狀態
4. **拆分過程中發現的 bug**，可以順便修復並記錄
5. **型別定義要完整**，避免使用 `any`

---

**文檔版本：** v1.0  
**最後更新：** 2025-11-04  
**維護者：** AI Assistant + User

