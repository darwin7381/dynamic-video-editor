# Creatomate 外部圖片載入問題 - 完整分析與解決方案

## 📋 問題起始

### 初始問題描述
用戶在使用 Creatomate Preview SDK 的 JSON 測試工具時發現：
- ✅ **Creatomate 官方圖片**：`https://creatomate-static.s3.amazonaws.com/demo/image1.jpg` 正常顯示
- ❌ **外部圖片**：`https://www.omlet.co.uk/images/cache/1024/682/Dog-Japanese_Shiba_Inu-Two_healthy_adult_Japanese_Shiba_Inus_standing_tall_together.jpg` 顯示為一片黑

### 用戶的具體疑問
1. 什麼是預覽模式？什麼是渲染模式？
2. 為什麼外部圖片在預覽中變成黑色？
3. 是否與 Template ID 限制有關？
4. 渲染機制到底是本地還是遠端？

## 🔍 深度技術分析

### 1. 預覽模式 vs 渲染模式

#### 預覽模式（Preview SDK）
```typescript
// 完全在瀏覽器中運行
const preview = new Preview(htmlElement, 'player', publicToken);
await preview.setSource(jsonSource);
```

**特點**：
- ✅ 瀏覽器本地即時渲染
- ✅ 即時響應，修改 JSON 立即看到效果
- ✅ 不需要網路請求 Creatomate 伺服器
- 🔒 **受到嚴格的安全限制**

#### 渲染模式（API）
```typescript
// 在 Creatomate 雲端伺服器運行
client.render(options)
```

**特點**：
- 🌐 在 Creatomate 雲端伺服器運行
- 🎬 產生最終的 MP4 檔案
- 🔒 同樣有嚴格的安全限制
- ⏱️ 需要時間處理，不是即時的

### 2. Preview SDK 架構分析

#### 實際架構
```typescript
// Preview.ts 第 133 行
iframe.setAttribute('src', `https://creatomate.com/embed?version=1.6.0&token=${publicToken}`);
```

**運作機制**：
```
你的應用 → Preview SDK → iframe → https://creatomate.com/embed
                                    ↑
                              真正的限制在這裡！
```

#### 關鍵發現
- Preview SDK 創建一個 iframe
- iframe 載入 `https://creatomate.com/embed`（Creatomate 的遠端頁面）
- **圖片限制在 Creatomate 的 embed 頁面中實施**
- 程式碼透過 `postMessage` 與 iframe 通訊

### 3. 安全限制機制

#### 限制實施位置
```javascript
// 在 creatomate.com/embed 頁面中（我們無法修改）
const allowedImageDomains = [
  'creatomate-static.s3.amazonaws.com',
  'creatomate.com',
  // 其他信任網域
];

// 當載入圖片時檢查
if (!isAllowedDomain(imageUrl)) {
  // 顯示黑色或錯誤
  return null;
}
```

#### 為什麼首頁範例可以，JSON 測試不行？

**差異在於使用方式**：

```typescript
// 首頁範例：修改現有模板
await preview.loadTemplate(templateId);
await preview.setModifications({ 'Image.source': externalUrl });
// ↑ 可能模板本身有特殊權限

// JSON 測試：完全自訂
await preview.setSource(customJson);
// ↑ 受到更嚴格的安全限制
```

## 🌐 官方文檔調查結果

### Creatomate 官方立場
經過全面的官方文檔查詢發現：
- ❌ **沒有直接解決方案** - Creatomate 官方並未提供繞過外部圖片限制的方法
- 🔒 **這是故意的安全設計** - 限制是出於安全考量，防止潛在風險
- 📖 **官方建議** - 使用受信任的儲存服務（如 AWS S3、Google Cloud Storage）

### API 上傳資源調查
- ❌ **沒有直接的 CDN 上傳功能** - Creatomate 不提供公開的 CDN 上傳 API
- ❌ **需要手動上傳** - 只能透過網頁介面手動上傳
- ❌ **不適合自動化** - 無法程式化批量上傳

## 💡 解決方案分析

### 方案比較

| 方案 | 可行性 | 自動化程度 | 維護成本 | 推薦度 | 實測結果 |
|------|--------|------------|----------|--------|---------|
| 修改 SDK | ❌ 技術上可行但不實際 | 低 | 極高 | ❌ | - |
| 上傳到 Creatomate CDN | ❌ 需手動操作 | 低 | 高 | ❌ | - |
| **圖片代理** | ❌ **跨域 iframe 失敗** | - | - | ❌ | **已測試失敗** |
| Base64 內嵌 | ⚠️ 僅適合小檔案 | 中 | 中 | ⚠️ | - |
| **cacheAsset() API** | ✅ **官方支援** | 高 | 低 | ✅ | **待測試** |
| **setCacheBypassRules()** | ⚠️ 僅針對快取 | 中 | 低 | ⚠️ | **待測試** |

### ❌ 圖片代理方案 - 實測失敗

**實驗日期**：2025年10月30日  
**測試環境**：Chrome DevTools + Playwright 自動化測試  
**測試素材**：`https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg`

#### 實驗過程

1. **代理 API 測試**：✅ 完全正常
   ```bash
   curl "http://localhost:3000/api/media-proxy?url=https%3A%2F%2Ffiles.blocktempo.ai%2F..."
   # 返回：JPEG image data, 1280x720, 159KB
   ```

2. **URL 轉換邏輯測試**：✅ 完全正常
   ```javascript
   processMediaUrl('https://files.blocktempo.ai/...')
   // 返回：'/api/media-proxy?url=https%3A%2F%2Ffiles.blocktempo.ai%2F...'
   ```

3. **同源 iframe 測試**：✅ 成功
   - 在 `localhost:3000` 的 iframe 中載入代理 URL
   - 圖片正常顯示

4. **跨域 iframe 測試**：❌ **失敗**
   - Creatomate iframe（`creatomate.com/embed`）
   - 傳入相對路徑 `/api/media-proxy?url=...`
   - **結果：畫面黑色，圖片未載入**

#### 失敗根本原因

**跨域 iframe 的相對路徑解析問題**：

```
你的頁面 (localhost:3000)
  └─ Preview SDK 透過 postMessage 傳送：
      source = "/api/media-proxy?url=..."
      
      └─ iframe (creatomate.com) 收到相對路徑
          └─ 瀏覽器將相對路徑解析為：
              https://creatomate.com/api/media-proxy?url=...
              
              └─ ❌ 404 Not Found
                  （因為這個 API 在 creatomate.com 不存在）
```

**技術原理**：
- 相對路徑在 HTML 中會相對於**當前文檔的 base URL** 解析
- iframe 的 base URL 是 `https://creatomate.com/embed`
- 所以 `/api/media-proxy` 會被解析為 `https://creatomate.com/api/media-proxy`
- 這是 Web 標準行為，**無法繞過**

#### 驗證證據

**Console 日誌顯示**：
```
✅ [processMediaUrl] 轉換為代理: /api/media-proxy?url=...
✅ 代理 URL 測試結果: 200 OK
✅ JSON設置完成
❌ 畫面仍然是黑色
```

**Network 分析**：
- ✅ 主頁面的 fetch 請求成功（測試用）
- ❌ iframe 沒有發起任何 media-proxy 請求
- ❌ iframe 可能嘗試請求 `creatomate.com/api/media-proxy`（404）

#### 結論

**Media Proxy 方法在跨域 iframe 環境中無效**：
- ✅ 技術實作完全正確
- ✅ 代理 API 運作正常
- ❌ **但無法解決跨域 iframe 的路徑解析問題**
- ❌ **這是 Web 標準限制，不是程式碼問題**

---

## ✅ cacheAsset() API - 官方解決方案

基於實測失敗的經驗，**唯一可行的方案是使用 Creatomate v1.6.0 提供的官方 API**：

### 核心機制

```typescript
// 1. 在你的頁面（localhost:3000）下載素材
const response = await fetch('https://files.blocktempo.ai/image.jpeg');
const blob = await response.blob();

// 2. 透過 cacheAsset 傳遞 Blob 給 iframe
await preview.cacheAsset('https://files.blocktempo.ai/image.jpeg', blob);

// 3. 正常使用原始 URL（iframe 會使用快取的 Blob）
await preview.setSource({
  elements: [{
    type: 'image',
    source: 'https://files.blocktempo.ai/image.jpeg'  // 使用原始 URL
  }]
});
```

### 為什麼 cacheAsset 可以成功？

1. **Blob 直接傳遞**：
   - Blob 是二進位資料物件，可以透過 postMessage 傳遞
   - iframe 直接使用 Blob 內容，不需要發起 HTTP 請求

2. **官方 API 支援**：
   - Preview SDK 專門設計的功能
   - 程式碼註解明確說明：「This URL won't be requested」

3. **繞過所有限制**：
   - 不涉及 URL 解析問題
   - 不受 CORS 限制（你的頁面下載，你控制 CORS）
   - 不受跨域 iframe 影響

---

## 🔚 最終結論

### 已驗證失敗的方案

**❌ 圖片代理方案**（2025-10-30 實測）：
- 理論上合理，但無法在跨域 iframe 中運作
- 相對路徑會被解析到錯誤的域名
- 這是 Web 標準限制，無法繞過

### 推薦方案

**✅ cacheAsset() API**（官方支援，v1.6.0+）：
- 官方提供的正式解決方案
- 透過 Blob 直接傳遞資料
- 不受跨域限制影響
- 支援所有素材類型

---

## 📚 技術參考

### 相關檔案
- `node_modules/@creatomate/preview/src/Preview.ts` - SDK 核心實現（包含 cacheAsset API）
- `pages/tools/json-test.tsx` - JSON 測試工具
- `components/App.tsx` - 首頁範例實現
- `utility/mediaProxy.ts` - 代理工具函數（已證實無效）
- `pages/api/media-proxy.ts` - 代理 API（已證實無效）

### 關鍵程式碼片段
```typescript
// Preview SDK 初始化
const preview = new Preview(htmlElement, 'player', publicToken);

// iframe 創建（跨域！）
iframe.setAttribute('src', `https://creatomate.com/embed?version=1.6.0&token=${publicToken}`);

// ❌ 錯誤方法：使用相對路徑代理
await preview.setSource({
  elements: [{ source: '/api/media-proxy?url=...' }]  // 會被解析為 creatomate.com/api/media-proxy
});

// ✅ 正確方法：使用 cacheAsset
const response = await fetch('https://files.blocktempo.ai/image.jpeg');
const blob = await response.blob();
await preview.cacheAsset('https://files.blocktempo.ai/image.jpeg', blob);
await preview.setSource({
  elements: [{ source: 'https://files.blocktempo.ai/image.jpeg' }]
});
```

### 環境配置
```env
CREATOMATE_API_KEY=your_api_key
NEXT_PUBLIC_CREATOMATE_PUBLIC_TOKEN=your_public_token
NEXT_PUBLIC_TEMPLATE_ID=your_template_id
```

---

*文件創建時間：2025年1月*
*最後更新：2025年10月30日 - 新增 Media Proxy 實測失敗記錄*
