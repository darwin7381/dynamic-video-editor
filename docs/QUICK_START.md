# 🚀 快速開始指南

**最後更新**：2025年11月2日  
**預計時間**：5-10 分鐘

---

## ✅ 當前功能狀態

| 功能 | 狀態 | 需要設定 |
|------|------|---------|
| 圖片（任何來源） | ✅ 完全支援 | 無 |
| 影片（有 CORS） | ✅ 完全支援 | Cloudflare R2 CORS |
| 影片（無 CORS） | ✅ 完全支援 | 無 |
| GIF 定格顯示 | ✅ 完全支援 | 無 |
| GIF 動畫播放 | ⚠️ 需設定 | CloudConvert API Key |

---

## 📋 必要設定（5 分鐘）

### 步驟 1：設定 Creatomate Tokens

已在 `.env.local` 中：
```env
CREATOMATE_API_KEY=...
NEXT_PUBLIC_CREATOMATE_PUBLIC_TOKEN=...
```
✅ 已完成

---

## ⚙️ 選擇性設定

### GIF 動畫支援（如需要）

**如果你需要 GIF 作為 video 類型播放動畫**：

1. 註冊 CloudConvert：https://cloudconvert.com/register
2. 取得 API Key：https://cloudconvert.com/dashboard/api/v2/keys
3. 加到 `.env.local`：
   ```env
   CLOUDCONVERT_API_KEY=你的API密鑰
   ```
4. 重啟伺服器

**免費額度**：25 次/天

**詳細說明**：參考 `convertapi-setup.md`

---

## 🧪 測試案例

### 測試 1：圖片（必定成功）

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

預期：✅ 立即顯示

### 測試 2：影片（你的 R2）

```json
{
  "type": "video",
  "source": "https://files.blocktempo.ai/Video-Placeholder.mp4",
  "duration": "5 s"
}
```

預期：✅ 正常播放

### 測試 3：GIF 定格

```json
{
  "type": "image",
  "source": "https://media.tenor.com/EOhh4Dv9AdUAAAAM/point-at-you-point.gif",
  "fit": "cover",
  "duration": "4 s"
}
```

預期：✅ 顯示第一幀（定格）

### 測試 4：GIF 動畫（需 CloudConvert）

```json
{
  "type": "video",
  "source": "https://media.tenor.com/EOhh4Dv9AdUAAAAM/point-at-you-point.gif",
  "fit": "cover",
  "duration": "4 s"
}
```

預期：
- ⏳ 等待 3-5 秒（轉換中）
- ✅ GIF 動畫播放

---

## 🎯 使用技巧

### 1. JSON 編輯器即時預覽

- 修改 JSON 後等待 0.8 秒
- 自動更新預覽
- 無需按任何按鈕

### 2. GIF 的兩種用法

**靜態預覽**（免費，即時）：
```json
{ "type": "image", "source": "xxx.gif" }
```

**動畫預覽**（需 API，3-5秒）：
```json
{ "type": "video", "source": "xxx.gif" }
```

### 3. 外部素材

**有 CORS 的來源**：
- 直接使用，自動處理

**無 CORS 的來源**：
- 已知網域（如 2050today.org）：自動使用代理
- 未知網域：可能需要加到代理邏輯中

---

## 🐛 常見問題

### Q1：圖片顯示黑畫面？

**檢查**：
1. 查看 Console 日誌
2. 確認 URL 可訪問
3. 等待 1-2 秒（下載時間）

**通常是**：網路問題或 URL 無效

### Q2：GIF 不會動？

**檢查**：
1. element type 是 "video" 還是 "image"？
2. 是否設定了 CloudConvert API Key？
3. 查看 Console 是否有轉換日誌

**解決**：
- type="image" → 只會顯示定格（正常）
- type="video" → 需要 CloudConvert API Key

### Q3：影片無法播放？

**檢查**：
1. 影片來源是否有 CORS？
2. 查看 Console 錯誤訊息
3. 檢查影片格式（需為 MP4）

**解決**：
- 設定 R2 CORS
- 或等待自動使用代理

---

## 📚 進階閱讀

- **完整技術細節**：`COMPLETE_SOLUTION_SUMMARY.md`
- **架構深度分析**：`creatomate-preview-sdk-deep-dive.md`
- **問題排查**：`cacheasset-investigation.md`

---

**開始使用！有問題請查閱相關文檔。** 🎉

