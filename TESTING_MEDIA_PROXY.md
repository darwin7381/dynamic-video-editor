# 🧪 Media Proxy 測試指南

## 修復內容總結

### ✅ 已修復的問題

**問題**：JSON 編輯器的即時預覽功能沒有使用 media-proxy，導致外部素材（包括 Cloudflare R2）無法載入。

**修復**：在 `pages/tools/json-test.tsx` 的 `useEffect` 即時更新函數中加入 `processMediaUrlsInJson()` 調用。

### 📝 修改的檔案

1. **`pages/tools/json-test.tsx`** (第 688-738 行)
   - 在即時預覽的 `useEffect` 中加入外部媒體 URL 處理
   - 確保所有外部 URL 都會自動轉換為代理 URL

### 🔧 工作原理

```
原始 JSON（你輸入的）
  ↓
processMediaUrlsInJson()  ← 新增的處理步驟
  ↓
轉換 URL：
  https://files.blocktempo.ai/xxx.jpg
  →
  /api/media-proxy?url=https%3A%2F%2Ffiles.blocktempo.ai%2Fxxx.jpg
  ↓
convertToSnakeCase()
  ↓
preview.setSource()
  ↓
✅ Creatomate Preview SDK 看到的是相對路徑
✅ 代理 API 去抓取真正的圖片
✅ 即時預覽成功顯示！
```

---

## 🚀 測試步驟

### 測試 1：使用測試按鈕（最快）

1. 啟動開發伺服器：
   ```bash
   npm run dev
   ```

2. 開啟瀏覽器訪問：
   ```
   http://localhost:3000/tools/json-test
   ```

3. 點擊 **「🧪 測試外部圖片」** 按鈕

4. **預期結果**：
   - ✅ 看到 Cloudflare R2 的圖片（`files.blocktempo.ai`）
   - ✅ 圖片正常顯示，不是黑色
   - ✅ Console 顯示：
     ```
     🔧 即時預覽：開始處理外部媒體 URL...
     ✅ 即時預覽：媒體 URL 處理完成
     🧪 測試代理 URL: /api/media-proxy?url=https%3A%2F%2Ffiles.blocktempo.ai%2F...
     🧪 代理 URL 測試結果: 200 OK
     🎉 測試圖片載入成功！
     ```

---

### 測試 2：手動輸入 JSON（測試即時預覽）

1. 在左側 JSON 編輯器中貼上以下內容：

```json
{
  "output_format": "mp4",
  "width": 1920,
  "height": 1080,
  "fill_color": "#000000",
  "elements": [
    {
      "type": "image",
      "source": "https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg",
      "fit": "cover",
      "time": "0 s",
      "duration": "5 s"
    },
    {
      "type": "text",
      "text": "Cloudflare R2 即時預覽測試",
      "font_family": "Noto Sans TC",
      "font_size": "6 vh",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "50%",
      "time": "1 s",
      "duration": "3 s"
    }
  ]
}
```

2. **等待 0.8 秒**（防抖延遲）

3. **預期結果**：
   - ✅ 右側預覽自動更新
   - ✅ 顯示 Cloudflare R2 的圖片
   - ✅ Console 顯示：
     ```
     🔧 即時預覽：開始處理外部媒體 URL...
     ✅ 即時預覽：媒體 URL 處理完成
     ✅ JSON更新成功，時間軸元素: 2
     ```

---

### 測試 3：測試任意外部網域

使用提供的測試檔案 `test-external-media.json`：

1. 複製 `test-external-media.json` 的內容

2. 貼到 JSON 編輯器中

3. **預期結果**：
   - ✅ 第一段：顯示 Cloudflare R2 圖片
   - ✅ 第二段：顯示 Picsum 隨機圖片
   - ✅ 兩張圖片都正常載入

---

### 測試 4：即時編輯測試

1. 在 JSON 編輯器中修改 `source` URL：
   ```json
   "source": "https://picsum.photos/800/600"
   ```

2. 等待 0.8 秒

3. **預期結果**：
   - ✅ 預覽立即更新為新圖片
   - ✅ 無需按任何按鈕
   - ✅ Console 顯示處理日誌

---

## 🔍 除錯檢查清單

### 如果圖片顯示為黑色

1. **檢查 Console 日誌**：
   ```javascript
   // 應該看到：
   🔧 即時預覽：開始處理外部媒體 URL...
   ✅ 即時預覽：媒體 URL 處理完成
   
   // 不應該看到：
   ❌ JSON更新失敗
   ```

2. **檢查 Network Tab**：
   - 打開 DevTools → Network
   - 篩選：`media-proxy`
   - 應該看到：`/api/media-proxy?url=...` 請求
   - 狀態碼應該是：`200 OK`

3. **檢查代理 URL**：
   ```javascript
   // 在 Console 輸入：
   const url = "https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg";
   const proxyUrl = `/api/media-proxy?url=${encodeURIComponent(url)}`;
   fetch(proxyUrl).then(r => console.log('代理狀態:', r.status));
   
   // 應該顯示：代理狀態: 200
   ```

### 如果代理 API 失敗

1. **檢查 API 是否運行**：
   ```bash
   # 在瀏覽器訪問：
   http://localhost:3000/api/media-proxy?url=https://picsum.photos/200/200
   
   # 應該直接顯示圖片
   ```

2. **檢查 CORS 錯誤**：
   - 代理 API 已設定 `Access-Control-Allow-Origin: *`
   - 不應該有 CORS 問題

3. **檢查 URL 編碼**：
   ```javascript
   // 確認 URL 正確編碼
   console.log(encodeURIComponent('https://files.blocktempo.ai/test.jpg'));
   // 應該輸出：https%3A%2F%2Ffiles.blocktempo.ai%2Ftest.jpg
   ```

---

## 📊 支援的素材來源

### ✅ 完全支援（會自動代理）

- **Cloudflare R2**：`https://files.blocktempo.ai/*`
- **任意 HTTPS 網域**：`https://example.com/*`
- **圖片服務**：Picsum, Unsplash, etc.
- **你自己的 CDN**：任何 HTTPS URL

### ✅ 不需要代理（直接支援）

- **Creatomate 官方素材**：
  - `https://creatomate-static.s3.amazonaws.com/*`
  - `https://creatomate.com/*`
  - `https://static.creatomate.com/*`

### ❌ 不支援

- HTTP URL（只支援 HTTPS，安全考量）
- 檔案大小 > 50MB（代理 API 限制）

---

## 🎯 效能考量

### 快取機制

代理 API 已設定適當的快取標頭：

```javascript
// 圖片：快取 24 小時
Cache-Control: public, max-age=86400

// 音訊：快取 2 小時
Cache-Control: public, max-age=7200

// 影片：快取 1 小時
Cache-Control: public, max-age=3600
```

### 防抖延遲

即時預覽使用 800ms 防抖，避免過於頻繁的更新：

```javascript
setTimeout(async () => {
  // 處理 JSON 更新
}, 800);
```

---

## 💡 進階測試

### 測試混合素材

```json
{
  "output_format": "mp4",
  "width": 1920,
  "height": 1080,
  "elements": [
    {
      "type": "video",
      "source": "https://files.blocktempo.ai/video.mp4",
      "time": "0 s",
      "duration": "5 s"
    },
    {
      "type": "image",
      "source": "https://creatomate-static.s3.amazonaws.com/demo/image1.jpg",
      "time": "5 s",
      "duration": "3 s"
    },
    {
      "type": "image",
      "source": "https://picsum.photos/1920/1080",
      "time": "8 s",
      "duration": "3 s"
    }
  ]
}
```

**預期行為**：
- Cloudflare R2 影片 → 使用代理
- Creatomate 官方圖片 → 不使用代理（直接載入）
- Picsum 圖片 → 使用代理

---

## 🐛 已知問題與解決方案

### 問題 1：首次載入可能較慢

**原因**：代理需要從外部下載素材

**解決**：
- 快取機制會加速後續載入
- 考慮預熱常用素材

### 問題 2：大型影片可能超時

**原因**：代理 API 有 30 秒超時限制

**解決**：
- 使用較小的影片檔案
- 或考慮直接上傳到 Creatomate CDN

---

## 📈 成功指標

測試成功的標準：

- ✅ Cloudflare R2 素材能即時預覽
- ✅ 任意外部網域素材能即時預覽
- ✅ 修改 JSON 後自動更新（0.8秒內）
- ✅ Console 無錯誤訊息
- ✅ Network 請求狀態碼 200
- ✅ 預覽畫面正常顯示，無黑色區域

---

## 🎉 下一步

如果測試成功：

1. ✅ 可以開始使用任意外部素材
2. ✅ 不需要手動上傳到 Creatomate
3. ✅ 即時預覽完全可用
4. ✅ 支援 Cloudflare R2 和所有外部來源

如果測試失敗：

1. 檢查上述除錯清單
2. 查看 Console 和 Network 詳細日誌
3. 回報具體錯誤訊息

---

**測試時間**：2025年10月30日  
**修復版本**：Media Proxy v1.0  
**狀態**：✅ 準備測試

