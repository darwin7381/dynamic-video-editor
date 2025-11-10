# Elements 匯入功能實作文件

## 功能概述

在 JSON 直接導入編輯器中,新增了專門用於匯入 Elements 的功能,位於第二排按鈕。

## 功能特點

### 支援四種輸入格式

1. **格式1: 帶有 "elements" 的完整物件**
   ```json
   {
     "elements": [
       { "type": "text", ... }
     ]
   }
   ```

2. **格式2: 直接的陣列**
   ```json
   [
     { "type": "text", ... }
   ]
   ```

3. **格式3: 直接的 "elements": [...] 字串**
   ```json
   "elements": [
     { "type": "text", ... }
   ]
   ```

4. **格式4: 多個元素物件(用逗號分隔)**
   ```json
   { "type": "text", ... },
   { "type": "image", ... },
   { "type": "video", ... }
   ```

### 自動轉換為標準格式

無論輸入哪種格式,系統都會自動轉換為標準的 Creatomate 影像 JSON 格式:

```json
{
  "outputFormat": "mp4",
  "width": 1280,
  "height": 1280,
  "elements": [...]
}
```

## 技術實作

### 新增檔案

1. **`/components/json-test/ElementsImportModalComponent.tsx`**
   - 新的彈窗組件,專門處理 Elements 匯入
   - 提供清晰的格式說明
   - 使用統一的樣式系統

2. **測試文件**
   - `/test-elements-import.md` - 測試案例和使用說明

### 修改檔案

1. **`/utility/apiRequestHelpers.ts`**
   - 新增 `extractFromElementsInput()` 函數
   - 智能識別四種輸入格式
   - 格式3: 自動補完 `"elements": [...]` 為完整物件
   - 格式4: 自動偵測多個元素並包裝為陣列
   - 自動構建完整的 JSON 結構

2. **`/hooks/useImportExport.ts`**
   - 新增 Elements 匯入相關的狀態管理
   - 新增 `openElementsImportModal()` 函數
   - 新增 `handleImportElements()` 函數
   - 擴展 return 物件,暴露 Elements 相關功能

3. **`/components/json-test/JsonTestStyles.ts`**
   - 新增 `ImportElementsButton` 樣式組件
   - 使用青色 (#00bcd4) 作為主題色,與其他按鈕區分

4. **`/pages/tools/json-test.tsx`**
   - 導入新的 `ElementsImportModalComponent`
   - 導入 `ImportElementsButton` 樣式
   - 從 `useImportExport` hook 解構 Elements 相關功能
   - 在 UI 中添加第二排按鈕
   - 在頁面底部添加 Elements 匯入彈窗

## 使用方式

1. 訪問 JSON 直接導入編輯器 (`/tools/json-test`)
2. 在第一排按鈕下方找到「匯入 Elements」按鈕(青色)
3. 點擊按鈕打開彈窗
4. 貼入三種格式之一的 Elements 資料
5. 點擊「匯入」
6. 系統自動轉換並填入編輯器

## 錯誤處理

- JSON 解析錯誤會顯示明確的錯誤訊息
- 無法識別的格式會提示使用者
- 所有錯誤都會在頁面頂部顯示

## 程式碼品質

- ✅ 通過所有 TypeScript 檢查
- ✅ 通過所有 Linter 檢查
- ✅ 遵循專案現有的程式碼風格
- ✅ 使用 React Hooks 模式
- ✅ 完整的錯誤處理

## 與現有功能的整合

- 與「匯入 JSON 請求」功能並列,互不干擾
- 共用相同的樣式系統和錯誤處理機制
- 使用統一的 Hook 架構
- 完全相容現有的時間軸、預覽等功能

## 未來擴展可能性

1. 可以添加「複製 Elements」功能(與「複製 api 請求」對應)
2. 可以支援更多輸入格式驗證
3. 可以添加 Elements 預覽功能
4. 可以支援批量匯入多組 Elements

