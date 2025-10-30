# GIF 預覽解決方案 - 最終分析

## 🔍 問題根源（已確認）

### 實驗證據

**測試結果**：
```
GIF 轉 MP4 完成
  ↓
URL 替換：https://files.blocktempo.ai/giphy-3.gif
       → https://files.blocktempo.ai/giphy-3.mp4?converted=123
  ↓  
cacheAsset(假URL, 真MP4 Blob) ✅ 成功
  ↓
setSource({ source: 假URL })
  ↓
iframe 嘗試載入
  ↓
❌ GET https://files.blocktempo.ai/giphy-3.mp4?converted=123
   → 404 Not Found
  ↓
❌ 播放失敗
```

### 根本原因

**Creatomate Preview SDK 的 cacheAsset 註解第 472-473 行的「This URL won't be requested」是錯誤的或有條件的！**

實際行為：
1. ✅ 對圖片：URL 確實不會被請求（只用快取）
2. ❌ **對影片：iframe 仍會驗證 URL 是否可訪問**
3. ❌ 如果 URL 返回 404 → 拒絕播放（即使有快取）

這解釋了所有現象：
- ✅ Google 影片（有 CORS，URL 存在）→ 成功
- ❌ 2050today 影片（無 CORS，URL 存在但無法訪問）→ 失敗  
- ❌ 假的 MP4 URL（不存在）→ 404 → 失敗

---

## 💡 可行的解決方案

### 方案 A：轉換後上傳到 R2（推薦）

```
1. 偵測 GIF
2. FFmpeg.wasm 轉換為 MP4
3. 上傳到 Cloudflare R2
4. 取得真實可訪問的 URL
5. 替換 JSON 中的 source
6. ✅ Preview 可以直接載入（有 CORS，URL 存在）
```

**優點**：
- ✅ URL 真實存在
- ✅ 有 CORS
- ✅ 永久儲存（下次不用再轉）
- ✅ 完全可行

**缺點**：
- ⚠️ 需要 R2 API 權限
- ⚠️ 上傳需要時間（~1-2秒）

---

### 方案 B：接受 Preview 限制（最實際）

**實作方式**：

1. **視覺提示系統**（你的建議）
   ```
   JSON 編輯器中：
   
   "source": "https://example.com/animation.gif"  ← 黃色背景（GIF 偵測）
   
   或
   
   "source": "https://example.com/animation.gif"  ← 灰色 + 提示圖標
            ⚠️ GIF 預覽為靜態，最終影片會動畫播放
   ```

2. **自動降級**
   ```typescript
   if (偵測到 GIF 且 type="video") {
     // 預覽時：改為 type="image"（至少能看到）
     // 最終渲染：保持 type="video"（正常播放）
   }
   ```

3. **提供「預覽模式」切換**
   ```
   [預覽模式] [渲染模式]
   
   預覽模式：GIF 顯示靜態（快）
   渲染模式：GIF 正常（需要實際渲染，慢）
   ```

---

## 🎯 我的建議

**立即採用方案 B**（視覺提示 + 自動降級）

原因：
1. ✅ 實作簡單（今天就能完成）
2. ✅ 不影響即時預覽速度
3. ✅ 使用者體驗清晰
4. ✅ 最終渲染完全正常

**長期考慮方案 A**（上傳 R2）

當你需要：
- 完美的預覽體驗
- 願意等待上傳時間
- 有 R2 儲存空間

---

**要我實作方案 B 的視覺提示系統嗎？這是當前最實際的解決方案。**
