# Custom Hooks 使用說明

## 📁 已創建的 Hooks

本目錄包含為 `json-test.tsx` 準備的三個自定義 Hooks：

### 1. usePreviewManager.ts

**功能：** 管理 Creatomate Preview SDK 的所有邏輯

**包含：**
- Preview 實例初始化和管理
- JSON 處理和素材快取
- 狀態管理（loading, error, ready）
- 視頻創建功能

**返回值：**
```typescript
{
  previewRef,
  previewContainerRef,
  previewReady,
  isLoading,
  error,
  currentState,
  processedSource,
  urlMapping,
  urlStatus,
  setError,
  setUrlStatus,
  setUpPreview,
  createVideo,
}
```

---

### 2. useTimeline.ts

**功能：** 管理時間軸相關的所有邏輯

**包含：**
- 時間軸元素管理
- 活躍元素追蹤
- 時間跳轉功能
- JSON 高亮同步

**返回值：**
```typescript
{
  timelineElements,
  activeElementIndices,
  currentEditingElement,
  autoHighlightRanges,
  clickedHighlightRange,
  setTimelineElements,
  setCurrentEditingElement,
  handleTimeChange,
  seekToTime,
}
```

---

### 3. useJsonProcessor.ts

**功能：** 管理 JSON 處理相關的邏輯

**包含：**
- JSON 即時更新（防抖處理）
- 外部素材快取
- URL 映射處理
- snake_case 轉換

**無返回值**（透過 callbacks 更新狀態）

---

## ⚠️ 當前狀態

**Hooks 已創建但尚未整合到主檔案。**

### 為什麼沒有立即整合？

1. **重構規模大** - 需要重寫大量現有代碼
2. **風險較高** - 可能影響現有功能
3. **需要完整測試** - 每個 Hook 都需要獨立測試

### 建議的整合步驟

如果要整合這些 Hooks，建議分階段進行：

#### 第 1 步：測試獨立性
```bash
# 確保 Hooks 可以正常編譯
npm run build
```

#### 第 2 步：逐一整合（從最簡單開始）

1. **先整合 useTimeline**
   - 影響範圍較小
   - 邏輯相對獨立

2. **再整合 useJsonProcessor**
   - 需要配合 usePreviewManager
   - 處理防抖邏輯

3. **最後整合 usePreviewManager**
   - 影響最大
   - 需要重寫初始化邏輯

#### 第 3 步：測試每個階段
- 確保編譯通過
- 測試所有功能
- 確認無錯誤

---

## 📊 預期效益

完全整合後預期：

### 代碼減少
- 主檔案：**~400-500 行** 減少
- 最終主檔案：約 **1000-1100 行**

### 可維護性提升
- ✅ 邏輯分離清晰
- ✅ 易於測試
- ✅ 可重用性高
- ✅ 型別安全

### 結構改善
```
主檔案 (1000 行)
└── UI 渲染邏輯
    
hooks/ (700 行)
├── usePreviewManager (243 行)
├── useTimeline (117 行)
└── useJsonProcessor (103 行)
```

---

## 🚀 如何使用（示例）

### 在組件中使用這些 Hooks

```typescript
const JSONTest: React.FC = () => {
  const [jsonInput, setJsonInput] = useState('...');
  
  // 1. 使用 Preview Manager
  const {
    previewRef,
    previewContainerRef,
    previewReady,
    isLoading,
    error,
    currentState,
    setError,
    setUpPreview,
    createVideo,
    urlStatus,
    setUrlStatus,
  } = usePreviewManager({
    jsonInput,
    onTimelineElementsParsed: setTimelineElements,
    parseTimelineElements,
    onTimeChange: handleTimeChange,
  });
  
  // 2. 使用 Timeline
  const {
    timelineElements,
    activeElementIndices,
    currentEditingElement,
    autoHighlightRanges,
    clickedHighlightRange,
    setTimelineElements,
    handleTimeChange,
    seekToTime,
  } = useTimeline({
    jsonInput,
    previewRef,
    previewReady,
  });
  
  // 3. 使用 JSON Processor
  useJsonProcessor({
    jsonInput,
    previewRef,
    previewReady,
    parseTimelineElements,
    onTimelineElementsParsed: setTimelineElements,
    setProcessedSource,
    setUrlMapping,
    setUrlStatus,
    setError,
  });
  
  // ... 其他邏輯
};
```

---

## 📝 注意事項

1. **不要強制整合** - 如果現有代碼運作正常，可以保持現狀
2. **漸進式重構** - 如果要整合，一次只整合一個 Hook
3. **保持備份** - 整合前先 git commit
4. **完整測試** - 每次整合後都要測試所有功能

---

## 🎯 結論

這些 Hooks 已經準備好，可以在需要時使用。它們展示了如何更好地組織代碼，但不是必須立即使用。當前的代碼結構（2585 → 1512 行）已經有了很大改善。

**建議：** 等到有明確需求（如需要重用邏輯、遇到維護問題）時再考慮整合這些 Hooks。

