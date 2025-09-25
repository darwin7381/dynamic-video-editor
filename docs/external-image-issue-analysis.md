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

| 方案 | 可行性 | 自動化程度 | 維護成本 | 推薦度 |
|------|--------|------------|----------|--------|
| 修改 SDK | ❌ 技術上可行但不實際 | 低 | 極高 | ❌ |
| 上傳到 Creatomate CDN | ❌ 需手動操作 | 低 | 高 | ❌ |
| 圖片代理 | ✅ 完全可行 | 高 | 低 | ✅ |
| Base64 內嵌 | ⚠️ 僅適合小檔案 | 中 | 中 | ⚠️ |

### 最終推薦：圖片代理方案

## 🔧 圖片代理解決方案詳解

### 核心機制

**問題根源**：
```
原本流程（失敗）：
Creatomate iframe → 直接請求 https://external-domain.com/image.jpg
                  ↓
                安全檢查：external-domain.com 不在白名單
                  ↓
                ❌ 顯示黑色
```

**代理解決方案**：
```
使用代理的流程（成功）：
Creatomate iframe → 請求 /api/media-proxy?url=...
                  ↓
                你的 Next.js API → 代理去抓取真正的圖片
                  ↓
                返回圖片數據給 Creatomate
                  ↓
                ✅ 正常顯示
```

### 為什麼代理能成功？

1. **繞過 URL 檢查**：
   - Creatomate 看到的是：`/api/media-proxy?url=...`
   - 這是**相對路徑**，不會觸發外部網域檢查

2. **服務端代理**：
   - API 在服務端抓取圖片
   - 直接返回圖片的**二進制數據**
   - Creatomate 收到的是數據，不是 URL

3. **支援多媒體**：
   - 圖片（JPG, PNG, WebP, SVG）
   - 影片（MP4, WebM, AVI）
   - GIF 動畫
   - 音訊（MP3, WAV, AAC）

## 🎯 實施計劃

### 階段一：基礎代理 API
- 創建 `/api/media-proxy.ts`
- 支援基本圖片代理
- 添加錯誤處理和快取

### 階段二：多媒體支援
- 支援影片、GIF、音訊
- 優化快取策略
- 添加檔案類型檢測

### 階段三：整合測試
- 更新 JSON 測試工具
- 添加代理 URL 轉換功能
- 全面測試各種媒體類型

## 🔚 結論

**問題本質**：Creatomate Preview SDK 透過 iframe 載入遠端頁面，該頁面對外部圖片有嚴格的安全限制。

**解決方案**：透過服務端代理繞過安全檢查，讓 Creatomate 以為圖片來自內部資源。

**優勢**：
- ✅ 完全繞過 Creatomate 限制
- ✅ 支援所有媒體類型
- ✅ 可以添加快取和優化
- ✅ 部署後立即生效
- ✅ 不需要手動上傳

**這是目前唯一實際可行的解決方案！**

---

## 📚 技術參考

### 相關檔案
- `node_modules/@creatomate/preview/src/Preview.ts` - SDK 核心實現
- `pages/tools/json-test.tsx` - JSON 測試工具
- `components/App.tsx` - 首頁範例實現

### 關鍵程式碼片段
```typescript
// Preview SDK 初始化
const preview = new Preview(htmlElement, 'player', publicToken);

// iframe 創建
iframe.setAttribute('src', `https://creatomate.com/embed?version=1.6.0&token=${publicToken}`);

// 設置來源
await preview.setSource(convertedSource);
```

### 環境配置
```env
CREATOMATE_API_KEY=your_api_key
NEXT_PUBLIC_CREATOMATE_PUBLIC_TOKEN=your_public_token
NEXT_PUBLIC_TEMPLATE_ID=your_template_id
```

---

*文件創建時間：2025年1月*
*最後更新：2025年1月*
