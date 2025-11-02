# CloudConvert 設定指南

## 📋 什麼是 CloudConvert？

**CloudConvert** = 雲端檔案轉換服務
- 支援 200+ 種格式轉換
- **GIF → MP4 轉換：支援 ✅**
- **速度：2-5 秒** ⭐
- 免費額度：25 次/天
- 付費方案：每月訂閱制

官網：https://cloudconvert.com/

---

## 🚀 設定步驟

### 1. 註冊帳號

1. 訪問：https://cloudconvert.com/register
2. 填寫 Email 和密碼
3. 驗證 Email

### 2. 取得 API Key

1. 登入後，前往：https://cloudconvert.com/dashboard/api/v2/keys
2. 點擊「Create API Key」
3. 複製你的 API Key（類似：`eyJ0eXAiOiJKV1QiLCJhbGc...`）

### 3. 設定環境變數

在 `.env.local` 檔案中加入：

```env
CLOUDCONVERT_API_KEY=你的_API_Key
```

例如：
```env
CLOUDCONVERT_API_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
```

### 4. 重啟開發伺服器

```bash
# 停止當前伺服器（Ctrl+C）
npm run dev
```

---

## 🧪 測試

### 測試 API

```bash
curl -X POST http://localhost:3000/api/convert-gif \
  -H "Content-Type: application/json" \
  -d '{"gifUrl":"https://media.tenor.com/EOhh4Dv9AdUAAAAM/point-at-you-point.gif"}' \
  > test-output.mp4
```

應該產生一個可播放的 MP4 檔案。

### 測試 JSON 編輯器

```json
{
  "output_format": "mp4",
  "width": 1920,
  "height": 1080,
  "elements": [
    {
      "type": "video",
      "source": "https://media.tenor.com/EOhh4Dv9AdUAAAAM/point-at-you-point.gif",
      "fit": "cover",
      "duration": "4 s"
    }
  ]
}
```

**預期結果**：
- ⏳ 轉換 2-3 秒
- ✅ GIF 動畫正常播放

---

## 📊 使用配額

### 免費額度

- **250 次/月**
- 每個 GIF 轉換 = 1 次
- 適合開發和小規模使用

### 配額用完後

**方案 1**：付費升級
- $9/月 = 1500 次
- $29/月 = 6000 次

**方案 2**：替代方案
- 接受 GIF 靜態預覽
- 或實作 FFmpeg.wasm（本地轉換，無配額限制）

---

## ⚡ 效能優勢

### ConvertAPI vs FFmpeg.wasm

| 項目 | ConvertAPI | FFmpeg.wasm |
|------|-----------|-------------|
| **首次使用** | 2-3 秒 ⭐⭐⭐⭐⭐ | 30秒+ (下載wasm) ⭐ |
| **後續使用** | 2-3 秒 ⭐⭐⭐⭐⭐ | 3-5 秒 ⭐⭐⭐⭐ |
| **伺服器負載** | 無 ⭐⭐⭐⭐⭐ | 無 ⭐⭐⭐⭐⭐ |
| **使用者 CPU** | 無 ⭐⭐⭐⭐⭐ | 高 ⭐⭐ |
| **成本** | 付費 ⭐⭐⭐ | 免費 ⭐⭐⭐⭐⭐ |

### 轉換速度測試

- 500KB GIF: ~1.5 秒
- 1MB GIF: ~2 秒
- 2MB GIF: ~3 秒

---

## 🎯 完整流程

```
使用者輸入 GIF URL
  ↓
偵測到 .gif
  ↓
調用 /api/convert-gif
  ↓
ConvertAPI 雲端轉換（2-3秒）
  ↓
下載轉換後的 MP4
  ↓
快取在記憶體
  ↓
創建快取 URL: /api/convert-gif-cached?url=...
  ↓
cacheAsset(快取URL, MP4 Blob)
  ↓
中間層替換 JSON
  ↓
Preview SDK 載入
  ↓
iframe 驗證 URL: GET /api/convert-gif-cached?url=...
  ↓
✅ 200 OK，返回 MP4
  ↓
✅ GIF 動畫播放成功！
```

---

## 🔒 安全注意事項

### API Secret 保護

- ✅ 使用環境變數（不要寫死在程式碼）
- ✅ 不要提交到 Git
- ✅ `.env.local` 已在 `.gitignore` 中

### 防濫用

建議加入：
- Rate limiting（限制每分鐘轉換次數）
- IP 白名單
- 監控使用量

---

**設定完成後即可測試！**

