# GIF → MP4 轉換方案

## 📋 問題描述

**問題**：Creatomate Preview SDK 不支援 GIF 作為 `type="video"` 在即時預覽中播放

**影響**：
- ❌ GIF 在預覽中顯示黑畫面或定格
- ✅ 最終渲染時正常播放

**用戶需求**：即時預覽時也要看到 GIF 動畫效果

---

## 💡 解決方案：FFmpeg.wasm

### 什麼是 FFmpeg.wasm？

**FFmpeg**：
- 業界標準的開源影音處理工具
- 可以轉換幾乎所有影音格式
- 專業軟體（Premiere、Final Cut）底層都用它

**WebAssembly (Wasm)**：
- 可以在瀏覽器執行的高效能程式碼
- 由 C/C++ 編譯而成
- 接近原生執行速度

**FFmpeg.wasm = FFmpeg + WebAssembly**：
- ✅ 完全在瀏覽器執行
- ✅ 不需要上傳檔案到伺服器
- ✅ 隱私安全
- ✅ 免費

---

## 🔧 實作方式

### 1. 安裝套件

```bash
npm install @ffmpeg/ffmpeg @ffmpeg/util
```

### 2. 核心轉換函數

```typescript
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile, toBlobURL } from '@ffmpeg/util';

async function convertGifToMp4(gifBlob: Blob): Promise<Blob> {
  // 初始化 FFmpeg
  const ffmpeg = new FFmpeg();
  await ffmpeg.load();
  
  // 寫入 GIF
  await ffmpeg.writeFile('input.gif', await fetchFile(gifBlob));
  
  // 執行轉換
  await ffmpeg.exec([
    '-i', 'input.gif',
    '-movflags', 'faststart',
    '-pix_fmt', 'yuv420p',
    'output.mp4'
  ]);
  
  // 讀取結果
  const data = await ffmpeg.readFile('output.mp4');
  return new Blob([data], { type: 'video/mp4' });
}
```

### 3. 自動處理流程

```
JSON 編輯器輸入：
{
  "type": "video",
  "source": "https://example.com/animation.gif"
}

↓ 自動觸發

1. 偵測 GIF
2. 下載 GIF (773KB)
3. 轉換為 MP4 (2-5 秒)
4. 創建假 URL: "...animation.mp4?converted=123"
5. cacheAsset(假URL, MP4 Blob)
6. 替換 JSON 中的 source
7. setSource({ source: "...animation.mp4?converted=123" })

↓

✅ 預覽正常播放 GIF 動畫！
```

---

## ⏱️ 效能分析

### 首次使用

```
1. 下載 FFmpeg.wasm core (~30MB)  ← 只需一次
2. 初始化                        ← 1-2 秒
3. 轉換 GIF → MP4               ← 2-5 秒
────────────────────────────────
總時間：約 3-8 秒（首次）
```

### 後續使用

```
1. FFmpeg 已載入（跳過）
2. 轉換 GIF → MP4               ← 2-5 秒
────────────────────────────────
總時間：約 2-5 秒
```

### 轉換速度影響因素

| 因素 | 影響 |
|------|------|
| GIF 檔案大小 | 500KB: ~2秒, 2MB: ~5秒 |
| GIF 解析度 | 1080p: ~4秒, 720p: ~3秒 |
| GIF 幀數 | 30幀: ~2秒, 100幀: ~5秒 |
| 使用者電腦效能 | CPU 越快越好 |

---

## 🎯 使用體驗

### 使用者看到的流程

```
1. 輸入包含 GIF 的 JSON
   ↓
2. 等待 0.8 秒（防抖）
   ↓
3. 彈出進度視窗：
   ┌────────────────────────┐
   │  🎬 GIF 轉檔中...       │
   │  轉換 GIF → MP4 (1/3)  │
   │  ████████░░░░ 65%      │
   │  首次使用需要載入       │
   │  FFmpeg.wasm (~30MB)   │
   └────────────────────────┘
   ↓
4. 3-5 秒後自動關閉
   ↓
5. ✅ 預覽顯示 GIF 動畫
```

---

## ✅ 優點

1. **完全自動化**
   - 使用者無需手動操作
   - 偵測到 GIF 自動轉換

2. **隱私安全**
   - 不上傳到伺服器
   - 完全在瀏覽器處理

3. **免費**
   - 無 API 費用
   - 無伺服器成本

4. **真正的 MP4**
   - 不是偽裝，是真實轉換
   - 相容性完美

---

## ⚠️ 注意事項

### 1. 首次載入

首次使用需要下載 ~30MB 的 FFmpeg.wasm：
- 會有幾秒的等待時間
- 只需下載一次（有快取）

### 2. 轉換時間

GIF 轉 MP4 需要 2-5 秒：
- 影響即時預覽體驗
- 但只在包含 GIF 時才需要

### 3. 瀏覽器相容性

需要支援 WebAssembly 的瀏覽器：
- ✅ Chrome 57+
- ✅ Firefox 52+
- ✅ Safari 11+
- ✅ Edge 16+

---

## 📊 測試案例

### 測試 1：小型 GIF（推薦）

```json
{
  "type": "video",
  "source": "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif",
  "duration": "3 s"
}
```

預期：~2 秒轉換完成

### 測試 2：中型 GIF

```json
{
  "type": "video",
  "source": "https://media.tenor.com/EOhh4Dv9AdUAAAAM/point-at-you-point.gif",
  "duration": "4 s"
}
```

預期：~3-4 秒轉換完成

---

## 🚀 下一步

**現在可以測試了！**

1. 重啟開發伺服器（讓 next.config.js 生效）
2. 刷新頁面
3. 輸入包含 GIF 的 JSON
4. 觀察轉檔進度
5. 查看預覽是否播放

**預期結果**：
- ✅ 顯示轉檔進度視窗
- ✅ GIF 轉換為真正的 MP4
- ✅ 預覽能播放 GIF 動畫

---

**文件創建時間**：2025年10月30日  
**解決方案**：FFmpeg.wasm 瀏覽器端轉檔

