# JSON 直接導入編輯器 - 完整技術指南

**創建時間**：2025年11月2日  
**頁面路徑**：`/tools/json-test`  
**核心檔案**：`pages/tools/json-test.tsx`  
**狀態**：✅ 生產就緒

---

## 📋 功能概述

### 核心功能

**JSON 直接導入編輯器** 是一個專業的影片編輯工具，允許使用者：

1. **直接編輯 Creatomate JSON**
   - 即時預覽（< 1秒響應）
   - 語法驗證
   - 自動格式轉換

2. **支援所有外部素材**
   - 任意圖片來源
   - 任意影片來源
   - GIF 動畫（可轉換）

3. **視覺化時間軸控制**
   - 多元素同時顯示
   - 點擊跳轉
   - 時間同步

4. **三向聯動**
   - JSON ⇄ 預覽
   - JSON ⇄ 時間軸
   - 預覽 ⇄ 時間軸

5. **即時視覺回饋**
   - 素材處理狀態（黃/綠/紅）
   - 當前元素高亮（淡藍）
   - 播放中元素（淡綠）

---

## 🏗️ 系統架構

### 整體架構圖

```
┌─────────────────────────────────────────────────┐
│                JSON 直接導入編輯器                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐        ┌─────────────────┐   │
│  │ JSON 編輯器   │◄──────►│  Preview SDK    │   │
│  │              │        │  (即時預覽)      │   │
│  │ - 四層高亮    │        │                 │   │
│  │ - 語法驗證    │        │  - iframe       │   │
│  │ - 自動同步    │        │  - postMessage  │   │
│  └──────┬───────┘        └────────┬────────┘   │
│         │                         │            │
│         │    ┌────────────────────┤            │
│         │    │                    │            │
│         ▼    ▼                    ▼            │
│  ┌──────────────────────────────────────┐      │
│  │      中間處理層                       │      │
│  │  - URL 映射                          │      │
│  │  - 素材快取                          │      │
│  │  - GIF 轉換                          │      │
│  │  - 狀態追蹤                          │      │
│  └──────────────────────────────────────┘      │
│         │                    │                 │
│         ▼                    ▼                 │
│  ┌──────────────┐    ┌─────────────────┐      │
│  │ 時間軸控制    │    │  後端 API       │      │
│  │              │    │                 │      │
│  │ - 複數選中    │    │ - Media Proxy   │      │
│  │ - 元素跳轉    │    │ - Convert GIF   │      │
│  └──────────────┘    └─────────────────┘      │
└─────────────────────────────────────────────────┘
```

---

## 💻 核心組件

### 1. JSON 編輯器（左側）

**結構**：
```jsx
<EditorContainer>
  {/* 層1: 自動播放高亮 */}
  <AutoHighlightOverlay />
  
  {/* 層2: 點擊選中高亮 */}
  <ClickedHighlightOverlay />
  
  {/* 層3: URL 狀態高亮 */}
  <UrlHighlightOverlay />
  
  {/* 層4: Textarea */}
  <JSONTextarea />
</EditorContainer>
```

**功能**：
- ✅ 即時編輯 JSON
- ✅ 防抖更新（800ms）
- ✅ 四層視覺回饋
- ✅ 滾動同步
- ✅ 不影響複製/選取

**State 管理**：
```typescript
const [jsonInput, setJsonInput] = useState(初始 JSON);  // 使用者輸入
const [processedSource, setProcessedSource] = useState(null);  // 處理後（給 SDK）
const [urlStatus, setUrlStatus] = useState(new Map());  // URL 處理狀態
const [autoHighlightRanges, setAutoHighlightRanges] = useState([]);  // 播放中
const [clickedHighlightRange, setClickedHighlightRange] = useState(null);  // 點擊
```

---

### 2. 預覽播放器（右上）

**技術**：Creatomate Preview SDK v1.6.0

**初始化**：
```typescript
const preview = new Preview(
  htmlElement, 
  'player', 
  CREATOMATE_PUBLIC_TOKEN
);

preview.onReady = async () => {
  // 設定影片快取規則
  await preview.setCacheBypassRules([/.*/]);
  
  // 快取外部素材
  const result = await cacheExternalAssets(preview, source, onStatusChange);
  
  // 設定來源
  await preview.setSource(processedSource);
};

preview.onTimeChange = handleTimeChange;  // 時間同步
```

**功能**：
- ✅ 即時預覽
- ✅ 播放控制
- ✅ 時間跳轉
- ✅ 自動同步到 JSON 和時間軸

---

### 3. 時間軸控制（右下）

**結構**：
```jsx
<TimelinePanel>
  <TimelineElementsContainer>
    {timelineElements.map((element, index) => (
      <TimelineElement
        $isActive={activeElementIndices.includes(index)}  // 播放中（淡綠）
        $isClicked={index === currentEditingElement}  // 點擊（藍框）
      >
        <ActiveIndicator>{點擊時顯示 ●}</ActiveIndicator>
        <ElementTime>{element.time}s</ElementTime>
        <ElementInfo>
          <ElementType>{element.name}</ElementType>
          <ElementText>{element.text}</ElementText>
        </ElementInfo>
        <TypeBadge>{element.type}</TypeBadge>
      </TimelineElement>
    ))}
  </TimelineElementsContainer>
</TimelinePanel>
```

**功能**：
- ✅ 顯示所有元素（包括嵌套）
- ✅ 複數選中（播放中的多個元素）
- ✅ 點擊跳轉到指定時間
- ✅ 同步到 JSON 高亮

---

## 🔄 數據流

### 輸入流程

```
使用者輸入 JSON
  ↓
jsonInput state 更新
  ↓
防抖 800ms
  ↓
┌─────────────────────────────────┐
│ 中間處理層                       │
│                                 │
│ 1. 解析 JSON                    │
│ 2. 提取外部素材 URL + type      │
│ 3. 去重（相同 URL 只處理一次）   │
│ 4. 平行處理所有素材：            │
│    - 下載（直接或代理）          │
│    - GIF 轉換（如果需要）        │
│    - cacheAsset                 │
│    - 狀態回調（黃→綠/紅）        │
│ 5. URL 映射（原始 → 處理後）     │
│ 6. 替換 JSON 中的 URL           │
│ 7. 轉換為 snake_case            │
└─────────────────────────────────┘
  ↓
Preview SDK.setSource(處理後的 JSON)
  ↓
預覽更新
  ↓
解析時間軸元素
  ↓
時間軸控制更新
```

### 互動流程

**A. JSON → 預覽 + 時間軸**
```
點擊 JSON 中的元素
  ↓
detectCurrentElement(cursorPosition)
  ↓
找到對應的時間軸元素
  ↓
seekToTime(time, index, path)
  ↓
- 預覽跳轉到該時間
- 時間軸高亮該元素（藍框 + 藍點）
- JSON 高亮該元素（淡藍 + 藍線）
```

**B. 時間軸 → JSON + 預覽**
```
點擊時間軸元素
  ↓
seekToTime(time, index, path)
  ↓
- 預覽跳轉
- JSON 高亮（使用 path 精確定位）
- 時間軸高亮（藍框 + 藍點）
```

**C. 預覽播放 → JSON + 時間軸**
```
影片播放（時間變化）
  ↓
preview.onTimeChange(time)
  ↓
handleTimeChange(time)
  ↓
找到所有活躍元素（time 在範圍內）
  ↓
過濾 composition（只要具體元素）
  ↓
- JSON 高亮所有活躍元素（淡藍背景）
- 時間軸高亮所有活躍元素（淡綠背景）
```

---

## 🎨 視覺回饋系統

### 四層高亮架構

**JSON 編輯器**：

```
┌────────────────────────────────────┐
│ 層4: 文字顯示（z-index: 4）        │
│ - Textarea                         │
│ - 背景透明                         │
│ - 接收輸入                         │
├────────────────────────────────────┤
│ 層3: URL 狀態（z-index: 3）        │
│ - 🟨 黃色：處理中                  │
│ - 🟩 綠色：成功                    │
│ - 🟥 紅色：失敗                    │
│ - <span inline>                   │
├────────────────────────────────────┤
│ 層2: 點擊選中（z-index: 2）        │
│ - 💙 淡藍背景                      │
│ - 💙 4px 藍色左側線                │
│ - <div block>（整行）              │
│ - 單個元素                         │
├────────────────────────────────────┤
│ 層1: 自動播放（z-index: 1）        │
│ - 💙 淡藍背景                      │
│ - 無邊線                           │
│ - <div block>（整行）              │
│ - 多個元素                         │
└────────────────────────────────────┘
```

**時間軸控制**：

```
普通元素：
┌────────────────────────────────┐
│     0.5s  headline    TEXT  🔵 │ 灰色背景
└────────────────────────────────┘

播放中（被動）：
┌────────────────────────────────┐
│     0.5s  headline    TEXT  🔵 │ 🟢 淡綠背景
└────────────────────────────────┘

點擊選中（主動）：
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ 💙 藍色粗框
┃  ●  0.5s  headline    TEXT  🔵 ┃ 🟢 淡綠背景 + 藍點
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## ⚙️ 中間處理層

### 設計理念

**分離關注點**：
- 使用者看到：原始 JSON（易讀）
- SDK 使用：處理後 JSON（可運作）
- 映射記錄：追蹤所有轉換

### State 架構

```typescript
// 使用者輸入
const [jsonInput, setJsonInput] = useState(原始);

// 處理後
const [processedSource, setProcessedSource] = useState(null);

// 映射記錄
const [urlMapping, setUrlMapping] = useState(new Map());
// 例如：
// "https://example.com/animation.gif" → "https://cloudconvert.com/.../converted.mp4"
// "https://no-cors-site.com/video.mp4" → "http://localhost:3000/api/media-proxy?url=..."
```

### 處理流程

**步驟 1：提取素材**
```typescript
const medias = extractMediaUrlsWithType(json);
// 結果：[
//   { url: "...", type: "image" },
//   { url: "...", type: "video" },
//   { url: "...", type: "video" }  // 可能重複
// ]
```

**步驟 2：去重**
```typescript
const uniqueMedias = Array.from(
  new Map(medias.map(m => [m.url, m])).values()
);
// 結果：只保留唯一 URL
```

**步驟 3：平行處理**
```typescript
const processingPromises = uniqueMedias.map(async (media) => {
  // 每個素材獨立處理
  onUrlStatusChange(url, 'processing');  // 🟨
  
  try {
    // 下載
    const blob = await downloadMedia(url);
    
    // 特殊處理
    if (isGif && type === 'video') {
      // 轉換為 MP4
      const result = await convertGif(url);
      cacheUrl = result.mp4Url;
      urlMapping.set(url, cacheUrl);
    } else if (noCORS) {
      // 使用代理
      cacheUrl = getAbsoluteProxyUrl(url);
      urlMapping.set(url, cacheUrl);
    }
    
    // 快取
    await preview.cacheAsset(cacheUrl, blob);
    
    onUrlStatusChange(url, 'success');  // 🟩
  } catch {
    onUrlStatusChange(url, 'error');  // 🟥
  }
});

await Promise.all(processingPromises);
```

**步驟 4：URL 替換**
```typescript
const processedSource = replaceUrls(source, urlMapping);
// 原始：{ "source": "animation.gif" }
// 處理：{ "source": "converted.mp4" }
```

**步驟 5：格式轉換**
```typescript
const snakeCaseSource = convertToSnakeCase(processedSource);
// camelCase → snake_case（SDK 需要）
```

**步驟 6：設定來源**
```typescript
await preview.setSource(snakeCaseSource);
```

---

## 🔍 元素定位系統

### Path 機制

**什麼是 Path？**

Path 是元素在 JSON 中的位置路徑：

```json
{
  "elements": [
    { "type": "image" },              // path = "0"
    { "type": "composition",          // path = "1"
      "elements": [
        { "type": "shape" },          // path = "1.0"
        { "type": "text" },           // path = "1.1"
        { "type": "composition",      // path = "1.2"
          "elements": [
            { "type": "image" }       // path = "1.2.0"
          ]
        }
      ]
    },
    { "type": "video" }               // path = "2"
  ]
}
```

**為什麼需要 Path？**
- 時間軸是平面陣列（索引 0, 1, 2...）
- JSON 是嵌套結構
- Path 橋接兩者

**如何使用？**
```typescript
// 時間軸元素
const element = {
  index: 3,  // 時間軸中的第 3 個
  path: "1.1",  // JSON 中的第 1 個 composition 的第 1 個子元素
  name: "text-element"
};

// 點擊時
const range = findElementRangeByPath(jsonInput, "1.1");
// 返回：{ start: 234, end: 456 }（text-element 在 JSON 中的字元位置）

// 高亮 JSON 中的 234-456 字元
```

### findElementRangeByPath 算法

**輸入**：
- `jsonText`：JSON 字串
- `path`：如 `"1.2.0"`

**輸出**：
- `{ start: 位置1, end: 位置2 }`

**算法**：
```
1. 分解 path: ["1", "2", "0"]
2. 對於每一層：
   a. 找到 "elements": [
   b. 遍歷，計數大括號
   c. 找到第 N 個元素
   d. 如果還有下一層：
      - 更新 searchStart
      - 繼續深入
   e. 如果是最後一層：
      - 返回 { start, end }
```

**時間複雜度**：O(M)，M = JSON 長度

---

## 🎯 關鍵功能實作

### 1. 即時預覽更新

**觸發**：jsonInput 改變

**流程**：
```typescript
useEffect(() => {
  if (!previewReady) return;
  
  const timeoutId = setTimeout(async () => {
    // 防抖 800ms
    
    const source = JSON.parse(jsonInput);
    
    // 中間處理層
    const cacheResult = await cacheExternalAssets(...);
    const processedSource = replaceUrls(source, cacheResult.urlMapping);
    const snakeCaseSource = convertToSnakeCase(processedSource);
    
    // 更新預覽
    await preview.setSource(snakeCaseSource);
    
    // 更新時間軸
    const elements = parseTimelineElements(source);
    setTimelineElements(elements);
    
  }, 800);
  
  return () => clearTimeout(timeoutId);
}, [jsonInput, previewReady]);
```

### 2. 三向聯動

**機制**：

**JSON → 其他**：
```typescript
// 游標移動時
const handleCursorChange = () => {
  const elementIndex = detectCurrentElement(cursorPosition, jsonInput);
  
  if (elementIndex !== -1) {
    // 跳轉預覽
    seekToTime(element.time, elementIndex, element.path);
    
    // 高亮時間軸
    setCurrentEditingElement(elementIndex);
  }
};
```

**時間軸 → 其他**：
```typescript
// 點擊時間軸元素
onClick={() => seekToTime(element.time, index, element.path)}

const seekToTime = (time, index, path) => {
  // 跳轉預覽
  await preview.setTime(time);
  
  // 高亮 JSON
  const range = findElementRangeByPath(jsonInput, path);
  setClickedHighlightRange(range);
  
  // 高亮時間軸
  setCurrentEditingElement(index);
};
```

**預覽播放 → 其他**：
```typescript
preview.onTimeChange = handleTimeChange;

const handleTimeChange = (time) => {
  // 找到所有活躍元素
  const activeElements = timelineElements.filter(el =>
    time >= el.time && 
    time < el.time + el.duration &&
    el.type !== 'composition'  // 排除 composition
  );
  
  // 高亮 JSON（多個）
  const ranges = activeElements.map(a => 
    findElementRangeByPath(jsonInput, a.path)
  );
  setAutoHighlightRanges(ranges);
  
  // 高亮時間軸（多個）
  const indices = activeElements.map(a => a.index);
  setActiveElementIndices(indices);
};
```

### 3. 素材處理狀態追蹤

**State**：
```typescript
const [urlStatus, setUrlStatus] = useState<Map<string, UrlStatus>>(new Map());

type UrlStatus = 'processing' | 'success' | 'error';
```

**更新時機**：
```typescript
// 在 cacheExternalAssets 中
for (const media of medias) {
  onUrlStatusChange(media.url, 'processing');  // 開始
  
  try {
    await processMedia(media);
    onUrlStatusChange(media.url, 'success');  // 成功
  } catch {
    onUrlStatusChange(media.url, 'error');  // 失敗
  }
}
```

**視覺呈現**：
```typescript
// 層3: URL 狀態高亮
<UrlHighlightOverlay>
  {generateHighlightedText(jsonInput, urlStatus)}
</UrlHighlightOverlay>

// 生成 HTML：
// 🟨 處理中的 URL：rgba(255, 193, 7, 0.3)
// 🟩 成功的 URL：rgba(76, 175, 80, 0.3)
// 🟥 失敗的 URL：rgba(244, 67, 54, 0.3)
```

---

## 🔧 關鍵技術細節

### 1. 閉包陷阱的解決

**問題場景**：
```typescript
// setUpPreview 只執行一次
const setUpPreview = (element) => {
  const preview = new Preview(...);
  
  preview.onTimeChange = (time) => {
    const elements = timelineElements;  // ← 捕獲初始值（空陣列）
    // ...
  };
};
```

**解決方案**：
```typescript
// 獨立 useCallback，依賴最新 state
const handleTimeChange = useCallback((time) => {
  const elements = timelineElements;  // 直接使用，永遠最新
  // ...
}, [timelineElements, jsonInput]);

// 每次更新時重新綁定
useEffect(() => {
  if (previewRef.current) {
    previewRef.current.onTimeChange = handleTimeChange;
  }
}, [handleTimeChange]);
```

### 2. 相同 URL 元素的區分

**問題**：
```json
{
  "elements": [
    { "time": "0s", "source": "same.gif" },
    { "time": "4s", "source": "same.gif" }
  ]
}
```

點擊第 2 個 → 錯誤跳到第 1 個

**原因**：只用 source 匹配

**解決**：
```typescript
// source + time 雙重匹配
if (elementSource === timelineElement.source && 
    Math.abs(elementTime - timelineElement.time) < 0.01) {
  return true;
}
```

### 3. 多範圍 HTML 生成

**錯誤方式**：
```typescript
ranges.map(r => generate(text, r)).join('')
// 每個都包含全文 → 文字重複
```

**正確方式**：
```typescript
let lastIndex = 0;
ranges.forEach(r => {
  result += text.substring(lastIndex, r.start);  // 只取未處理的部分
  result += `<div>...</div>`;
  lastIndex = r.end;
});
result += text.substring(lastIndex);  // 剩餘
```

### 4. Composition 的精確定位

**挑戰**：
- Composition 是容器，不應高亮
- 要高亮的是內部的具體元素

**解決**：
```typescript
// 過濾 composition
const activeElements = elements.filter(el => 
  inTimeRange(el) && 
  el.type !== 'composition'  // 排除
);

// 使用 path 精確定位
const range = findElementRangeByPath(jsonInput, "1.2.0");
// 直接定位到 composition 內部的具體元素
```

---

## 📊 效能指標

### 處理速度

| 場景 | 素材數 | 時間 | 說明 |
|------|-------|------|------|
| 單張圖片 | 1 | < 1秒 | 即時 |
| 10 張圖片 | 10 | 1-2秒 | 流暢 |
| 30 張圖片 | 30 | 2-3秒 | 可接受 |
| 5 個 GIF (video) | 5 | 15-25秒 | 需等待 |
| 10 個相同 URL | 1 次處理 | 1秒 | 已去重 |

### 視覺回饋延遲

| 動作 | 回饋時間 | 說明 |
|------|---------|------|
| 輸入 JSON | 800ms | 防抖延遲 |
| URL 狀態變化 | < 10ms | 即時 |
| 點擊元素 | < 50ms | 流暢 |
| 播放同步 | < 100ms | 可接受 |

---

## 🐛 已知問題與解決

### 1. 長 URL 換行對齊

**問題**：URL 很長，textarea 自動換行，但 overlay 不換行 → 錯位

**解決**：escapeHtml 不使用 `&nbsp;`，保留正常空格

### 2. 多個 `<div>` 的累積換行

**問題**：每個 `<div>` 後自動換行，多個 div → 累積錯位

**解決**：把元素後的逗號和換行也包在 div 內

### 3. Composition 整體被高亮

**問題**：composition 整個區塊很大，高亮沒意義

**解決**：
- 過濾 `type === 'composition'`
- 只高亮內部具體元素
- 使用 path 精確定位

### 4. 時間軸只能單選

**問題**：同一時間多個元素活躍，但只高亮一個

**解決**：
- State 分離（auto 多個 + clicked 單個）
- 視覺分層（淡綠背景 + 藍色外框）

---

## 🎓 最佳實踐

### JSON 編寫建議

**好的設計**（重複使用素材）：
```json
{
  "elements": [
    { "source": "logo.png" },  // 0秒
    { "source": "logo.png" },  // 5秒，相同 URL
    { "source": "logo.png" }   // 10秒
  ]
}
```
→ 自動去重，只下載 1 次

**避免**（不必要的 query 參數）：
```json
{
  "elements": [
    { "source": "logo.png?v=1" },  // 被視為不同 URL
    { "source": "logo.png?v=2" },
    { "source": "logo.png?v=3" }
  ]
}
```
→ 處理 3 次

### Composition 使用

**建議**：
- Composition 用於邏輯分組
- 內部元素會被正確處理
- 點擊時只高亮具體元素（不是整個 composition）

### GIF 使用

**type="image"**（靜態，快速）：
```json
{ "type": "image", "source": "animation.gif" }
```
→ 顯示第一幀，無需轉換

**type="video"**（動畫，需轉換）：
```json
{ "type": "video", "source": "animation.gif" }
```
→ 自動轉換為 MP4（3-5秒），需要 CloudConvert API Key

---

## 🔗 相關文檔

**深入理解**：
- `COMPLETE_SOLUTION_SUMMARY.md` - 完整總結
- `URL_HIGHLIGHT_IMPLEMENTATION.md` - 高亮系統
- `PERFORMANCE_OPTIMIZATIONS.md` - 效能優化

**設定指南**：
- `QUICK_START.md` - 快速開始
- `convertapi-setup.md` - GIF 轉換設定

**技術細節**：
- `creatomate-preview-sdk-deep-dive.md` - SDK 架構
- `cacheasset-investigation.md` - 深度調查

---

**文件完成時間**：2025年11月2日  
**維護者**：AI Team  
**狀態**：✅ 完整且最新

