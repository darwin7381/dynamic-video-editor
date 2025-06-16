# Creatomate 視頻工具集

這個項目現在包含一個完整的 Creatomate 視頻工具集，提供多種即時Web界面的視頻創建和編輯功能。

## 🚀 快速開始

### 訪問工具集
在瀏覽器中訪問 `http://localhost:3000/tools` 來使用視頻工具集。

### 環境配置
確保在 `.env.local` 文件中設置了以下環境變數：

```env
CREATOMATE_API_KEY=your_api_key_here
NEXT_PUBLIC_CREATOMATE_PUBLIC_TOKEN=your_public_token_here
NEXT_PUBLIC_TEMPLATE_ID=your_template_id_here
```

## 🛠️ 可用工具

### 1. 視頻預覽工具 (`/tools/preview`)
- **功能**: 基於模板的實時視頻編輯和預覽
- **特點**: 
  - 實時預覽視頻修改
  - 可編輯文字、圖片、樣式
  - 支援動態添加幻燈片
  - 導出視頻功能

### 2. JSON 直接導入編輯器 (`/tools/json-test`)
- **功能**: 直接使用 JSON 格式創建和測試視頻
- **特點**:
  - 左側 JSON 編輯器，右側即時預覽
  - 內建多個示例模板
  - 支援 Creatomate 完整 JSON API
  - 自動載入和更新預覽

### 3. 生成字幕視頻 (`/tools/subtitle`)
- **功能**: 即時為視頻添加字幕
- **特點**:
  - 即時預覽字幕效果
  - 自定義字幕樣式（顏色、大小、位置）
  - 支援多行字幕文字
  - 自動時間軸分割

### 4. 生成基本視頻 (`/tools/generate`)
- **功能**: 可視化視頻編輯器
- **特點**:
  - 動態添加/編輯文字和圖片元素
  - 即時預覽所有修改
  - 可調整元素位置、大小、顏色
  - 支援背景色設置和動畫效果

## 📋 JSON API 格式

### 基本結構
```json
{
  "output_format": "mp4",
  "width": 1920,
  "height": 1080,
  "duration": "5 s",
  "elements": [
    {
      "type": "text",
      "text": "Hello World",
      "font_family": "Arial",
      "fill_color": "#ffffff"
    }
  ]
}
```

### 支援的元素類型
- **text**: 文字元素
- **image**: 圖片元素
- **video**: 視頻元素
- **audio**: 音頻元素
- **shape**: 形狀元素
- **composition**: 組合元素

### 支援的屬性
- **位置**: `x`, `y`, `width`, `height`
- **對齊**: `x_alignment`, `y_alignment`
- **時間**: `time`, `duration`
- **樣式**: `fill_color`, `font_family`, `font_size`
- **動畫**: `animations` 數組

## 🎯 使用範例

### 簡單文字視頻
```json
{
  "output_format": "mp4",
  "width": 1280,
  "height": 720,
  "elements": [
    {
      "type": "text",
      "text": "Hello Creatomate!",
      "font_family": "Arial",
      "font_size": "5 vh",
      "fill_color": "#ffffff",
      "x": "50%",
      "y": "50%",
      "x_alignment": "50%",
      "y_alignment": "50%"
    }
  ]
}
```

### 圖片+文字組合
```json
{
  "output_format": "mp4",
  "width": 1920,
  "height": 1080,
  "duration": "5 s",
  "elements": [
    {
      "type": "image",
      "track": 1,
      "source": "https://example.com/image.jpg"
    },
    {
      "type": "text",
      "text": "圖片標題",
      "font_family": "Arial",
      "font_size": "8 vh",
      "fill_color": "#ffffff",
      "x": "50%",
      "y": "20%",
      "x_alignment": "50%",
      "y_alignment": "50%"
    }
  ]
}
```

## 🔧 開發和擴展

### 添加新工具
1. 在 `pages/tools/` 目錄下創建新頁面
2. 更新 `pages/tools.tsx` 中的工具列表
3. 如需 API 支援，在 `pages/api/` 下創建對應路由

### API 端點
- `GET /api/json-test` - 獲取 API 狀態和示例
- `POST /api/json-test` - 驗證和渲染 JSON
- `POST /api/videos` - 原有的視頻渲染 API

## 📚 相關文檔

- [Creatomate API 文檔](https://creatomate.com/docs)
- [Creatomate JSON 格式](https://creatomate.com/docs/json/introduction)
- [官方 Node.js 範例](https://github.com/creatomate/node-examples)

## 🐛 問題和建議

如果遇到問題或有改進建議，請檢查：
1. 環境變數是否正確設置
2. API 密鑰是否有效
3. JSON 格式是否符合 Creatomate 規範

## 📄 授權

本項目遵循 MIT 授權條款。 