# Creatomate API 知識庫

## 基於官方 GitHub 範例的學習記錄

> 此文件記錄從 Creatomate 官方 GitHub 範例庫學到的確切知識
> 來源：https://github.com/Creatomate/node-examples

## API 請求格式

### 正確的 API 請求結構

基於用戶提供的實際工作範例，Creatomate API 請求格式為：

```json
{
  "source": {
    "outputFormat": "mp4",
    "width": 1920,
    "height": 1080,
    "fillColor": "#262626",
    "elements": [...]
  },
  "output_format": "mp4"
}
```

### 關鍵發現

1. **混合命名規則**：
   - 外層使用蛇形命名：`output_format`
   - 內層 source 使用駝峰命名：`outputFormat`, `fillColor`
   - 這種混合命名是官方標準，不是錯誤

2. **結構特點**：
   - 輸入的 JSON 直接作為 `source` 的值
   - 外層添加 `output_format` 字段
   - 不需要進行命名轉換

## 修復經驗

### 問題：視頻播放卡頓和不正常

**原因**：之前錯誤地對 JSON 進行了不必要的屬性命名轉換

**解決方案**：
```javascript
// 錯誤的做法（會導致播放問題）
const convertedSource = convertToCamelCase(inputSource); // ❌

// 正確的做法
const apiRequest = {
  source: inputSource,  // 直接使用原始 JSON ✅
  output_format: inputSource.output_format || "mp4"
};
```

### 學到的教訓

1. **不要隨意轉換屬性命名**：Creatomate API 有特定的命名要求，任意轉換會導致 SDK 無法正確解析
2. **保持原始格式**：輸入的 JSON 應該直接作為 source 使用
3. **遵循官方範例**：始終以官方提供的實際工作範例為準

## JSON 格式支持

### 標準格式（之前支持的）
```json
{
  "output_format": "mp4",
  "width": 1280,
  "height": 720,
  "elements": [...]
}
```

### 新發現的格式（需要支持的）
```json
{
  "outputFormat": "mp4",  // 駝峰命名
  "width": 1920,
  "height": 1080,
  "fillColor": "#262626", // 駝峰命名
  "elements": [...]
}
```

## 重要發現：Preview SDK vs API 的格式差異

### Preview SDK 格式要求
Creatomate Preview SDK 只接受**蛇形命名**（snake_case）格式：
```json
{
  "output_format": "mp4",
  "fill_color": "#262626",
  "font_family": "Noto Sans TC"
}
```

### API 格式要求
Creatomate API 接受**駝峰命名**（camelCase）格式：
```json
{
  "outputFormat": "mp4",
  "fillColor": "#262626",
  "fontFamily": "Noto Sans TC"
}
```

### 解決方案
在使用 Preview SDK 時，需要將駝峰命名轉換為蛇形命名：

```javascript
const convertToSnakeCase = (obj: any): any => {
  if (Array.isArray(obj)) {
    return obj.map(item => convertToSnakeCase(item));
  } else if (obj !== null && typeof obj === 'object') {
    const newObj: any = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        // 轉換 camelCase 為 snake_case
        const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
        newObj[snakeKey] = convertToSnakeCase(obj[key]);
      }
    }
    return newObj;
  }
  return obj;
};

// 使用轉換後的格式
await preview.setSource(convertToSnakeCase(source));
```

### 修復結果
- ✅ 支援蛇形命名格式（`output_format`）
- ✅ 支援駝峰命名格式（`outputFormat`）
- ✅ 視頻播放控件正常顯示
- ✅ 時間軸解析正常工作

## 極限測試範例

### 複雜範例特性
基於官方 GitHub 範例庫創建的極限測試範例包含：

1. **多元素類型**：
   - 視頻背景
   - 複雜文字動畫
   - 圖片幻燈片
   - 形狀元素
   - 音頻軌道

2. **高級動畫效果**：
   - `text-slide` 逐字符動畫
   - `elastic-out` 彈性緩動
   - `scale` 縮放動畫
   - `rotate` 旋轉效果
   - `fade` 淡入淡出

3. **組合結構**：
   - `composition` 嵌套元素
   - 多軌道時間軸管理
   - 複雜的動畫序列

### 範例用途
- 測試系統的渲染能力極限
- 驗證複雜動畫的預覽效果
- 確保多元素同步播放
- 檢驗時間軸解析的準確性

## 參考資料

- Creatomate 官方 Node.js 範例：https://github.com/Creatomate/node-examples
- 用戶提供的實際工作範例
- 官方 API 文檔：https://creatomate.com/docs
