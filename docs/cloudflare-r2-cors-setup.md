# Cloudflare R2 CORS 設定完整指南

## 問題分析

**現象**：圖片 URL `https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg` 在 Creatomate Preview SDK 中無法載入。

**錯誤**：
```
Access to fetch at 'https://files.blocktempo.ai/...' from origin 'https://creatomate.com' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

**診斷結果**：
```bash
curl -I https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg
# 結果：沒有任何 Access-Control-* 標頭
```

**結論**：R2 的 CORS 設定沒有生效或未正確設定。

---

## ✅ 正確的 CORS 設定

### 方法 1：在 Cloudflare Dashboard 設定

1. **登入 Cloudflare Dashboard**
   - https://dash.cloudflare.com

2. **進入 R2**
   - 左側選單 → R2 Object Storage
   - 找到並點擊你的 bucket

3. **進入 Settings**
   - 點擊上方的 "Settings" 標籤

4. **設定 CORS Policy**
   - 找到 "CORS Policy" 區塊
   - 點擊 "Edit" 或直接編輯 JSON

5. **貼入以下設定**：

```json
[
  {
    "AllowedOrigins": [
      "https://creatomate.com",
      "http://localhost:3000",
      "https://localhost:3000",
      "*"
    ],
    "AllowedMethods": [
      "GET",
      "HEAD"
    ],
    "AllowedHeaders": [
      "*"
    ],
    "ExposeHeaders": [
      "Content-Length",
      "Content-Type",
      "ETag"
    ],
    "MaxAgeSeconds": 3600
  }
]
```

6. **儲存設定**

7. **等待 2-5 分鐘**（讓設定生效）

8. **驗證設定**：
```bash
curl -I "https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg"
# 應該看到：
# Access-Control-Allow-Origin: *
# 或
# Access-Control-Allow-Origin: https://creatomate.com
```

---

### 方法 2：使用 Cloudflare Workers（如果 Dashboard 設定無效）

如果 R2 的 CORS 設定無法生效，可以使用 Worker 添加 CORS 標頭：

```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // 從 R2 獲取檔案
    const object = await env.MY_BUCKET.get(url.pathname);
    
    if (!object) {
      return new Response('Not Found', { status: 404 });
    }
    
    // 返回檔案並添加 CORS 標頭
    return new Response(object.body, {
      headers: {
        'Content-Type': object.httpMetadata.contentType || 'application/octet-stream',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Max-Age': '3600',
        'Cache-Control': 'public, max-age=31536000',
      }
    });
  }
};
```

---

## 🧪 測試 CORS 設定

### 測試 1：使用 curl

```bash
curl -I "https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg"
```

**應該看到**：
```
HTTP/2 200
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, HEAD
```

### 測試 2：使用瀏覽器 Console

```javascript
fetch('https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg', {
  mode: 'cors'
})
.then(r => console.log('✅ CORS OK:', r.status))
.catch(e => console.error('❌ CORS 失敗:', e));
```

### 測試 3：在 Creatomate Preview 中測試

設定完成後，在 JSON 編輯器貼入：
```json
{
  "output_format": "mp4",
  "width": 1920,
  "height": 1080,
  "elements": [
    {
      "type": "image",
      "source": "https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg",
      "fit": "cover",
      "duration": "4 s"
    }
  ]
}
```

**預期結果**：
- ✅ 圖片正常顯示
- ✅ 沒有 CORS 錯誤

---

## ⚠️ 常見問題

### Q1：設定後仍然有 CORS 錯誤

**可能原因**：
1. 設定尚未生效（等待 5-10 分鐘）
2. CDN 快取（清除瀏覽器快取）
3. CORS 規則格式錯誤

**解決方法**：
- 清除瀏覽器快取
- 使用無痕模式測試
- 檢查 CORS JSON 格式是否正確

### Q2：`AllowedOrigins: ["*"]` 為什麼不直接用這個？

**可以！** 但要注意：
- 允許所有來源存取
- 對公開資源沒問題
- 對私密資源需謹慎

### Q3：R2 CORS 設定在哪裡？

**正確位置**：
```
Cloudflare Dashboard
  → R2 Object Storage
  → 點擊你的 bucket
  → Settings 標籤
  → CORS Policy 區塊
```

**不是在**：
- ❌ Workers & Pages 設定
- ❌ Domain 設定
- ❌ 網站設定

---

## 🎯 終極解決方案

如果 CORS 設定確實無法生效或你需要支援任意外部網域：

### 使用 cacheAsset() API

**前提**：你的網域需要能夠下載素材（你的 R2 需要允許 localhost:3000）

```typescript
// 在 setSource 之前
const response = await fetch(url);  // 你的頁面下載
const blob = await response.blob();
await preview.cacheAsset(url, blob);  // 傳給 iframe
await preview.setSource(...);  // 使用原始 URL
```

**CORS 需求**：
- ✅ R2 允許 `localhost:3000`（你的頁面）
- ❌ R2 **不需要**允許 `creatomate.com`（因為 iframe 不會請求）

---

**下一步**：請確認 CORS 標頭是否已經出現在 HTTP 回應中！

