# 🎯 n8n 設定 ElevenLabs SRT 生成 - 逐步指南

## 📍 您的當前位置

```
[Download Audio] → [data] → [您要添加的新節點]
```

---

## 🔧 詳細操作步驟

### 步驟 1: 添加 HTTP Request 節點

#### 1.1 添加節點
- 點擊 `data` 節點後面的 **+** 號
- 搜尋 **HTTP Request**
- 點擊添加

#### 1.2 基本設定
```
Method: POST
URL: https://api.elevenlabs.io/v1/speech-to-text
```

#### 1.3 設定認證
1. 點擊 **Authentication** 下拉選單
2. 選擇 **Generic Credential Type**
3. **Generic Auth Type** 選擇 **Header Auth**
4. 點擊 **Credential for Header Auth** 旁的下拉選單

#### 1.4 創建新的 Credential（如果還沒有）
1. 點擊 **Create New Credential**
2. 設定：
   ```
   Name: xi-api-key
   Value: sk_c10b61842ead12201698676af90f1421d5f6e3cd555317ec
   ```
3. 點擊 **Save**

#### 1.5 設定請求 Body
1. 切換到 **Body** 標籤
2. 設定：
   ```
   Send Body: ✅ 打勾
   Body Content Type: Multipart-Form Data
   ```

3. 在 **Body Parameters** 點擊 **Add Parameter**
   ```
   Name: model_id
   Value: scribe_v1
   ```

#### 1.6 設定 Binary Data
1. 切換到 **Options** 標籤
2. 點擊 **Add Option** → 選擇 **Timeout**
   ```
   Timeout: 120000
   ```
3. 找到 **Send Binary Data** 選項並打勾
4. 設定：
   ```
   Binary Property: data
   ```

#### 1.7 測試節點
- 點擊 **Execute Node** 測試
- 應該會看到返回的 JSON 包含 `words` 陣列

---

### 步驟 2: 添加 Code 節點

#### 2.1 添加節點
- 點擊 HTTP Request 節點後的 **+** 號
- 搜尋 **Code**
- 點擊添加

#### 2.2 貼上代碼
1. 在 **JavaScript** 代碼區域
2. **刪除所有預設代碼**
3. 貼上以下完整代碼：

```javascript
// ========================================
// ElevenLabs 詞彙級 SRT 生成器
// ========================================

const elevenLabsResult = $input.item.json;
const words = elevenLabsResult.words || [];

// ========================================
// 🎯 在這裡調整參數
// ========================================
const MAX_CHARS = 18;      // 每段最多字符數（推薦 15-40）
const MAX_DURATION = 5.0;  // 每段最長時間（秒，推薦 3-7）
const INCLUDE_SPEAKERS = true;  // 是否包含說話者標識

// ========================================
// 核心函數（不需要修改）
// ========================================

function formatSRTTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const milliseconds = Math.floor((seconds % 1) * 1000);
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')},${milliseconds.toString().padStart(3, '0')}`;
}

function formatSRTSegment(index, startSec, endSec, text) {
  const startTime = formatSRTTime(startSec);
  const endTime = formatSRTTime(endSec);
  return `${index}\n${startTime} --> ${endTime}\n${text}\n\n`;
}

function generateSRT(words, maxChars, maxDuration) {
  let srtContent = "";
  let segmentIndex = 1;
  let currentSegment = [];
  let currentText = "";
  let segmentStart = null;
  let currentSpeaker = null;
  
  for (const word of words) {
    if (word.type !== 'word') continue;
    
    const wordText = word.text;
    const wordStart = word.start;
    const wordEnd = word.end;
    const speaker = word.speaker_id || null;
    
    if (segmentStart === null) segmentStart = wordStart;
    if (currentSpeaker === null) currentSpeaker = speaker;
    
    const potentialText = currentText + wordText;
    const currentDuration = currentSegment.length > 0 ? wordEnd - segmentStart : 0;
    
    const shouldBreak = (
      (INCLUDE_SPEAKERS && speaker && speaker !== currentSpeaker) ||
      (potentialText.length > maxChars && currentSegment.length > 0) ||
      (currentDuration > maxDuration && currentSegment.length > 0)
    );
    
    if (shouldBreak) {
      const segmentEnd = currentSegment[currentSegment.length - 1].end;
      let finalText = currentText;
      
      if (INCLUDE_SPEAKERS && currentSpeaker) {
        finalText = `[${currentSpeaker}] ${currentText}`;
      }
      
      srtContent += formatSRTSegment(segmentIndex, segmentStart, segmentEnd, finalText);
      
      segmentIndex++;
      currentSegment = [word];
      currentText = wordText;
      segmentStart = wordStart;
      currentSpeaker = speaker;
    } else {
      currentSegment.push(word);
      currentText = potentialText;
    }
  }
  
  if (currentSegment.length > 0) {
    const segmentEnd = currentSegment[currentSegment.length - 1].end;
    let finalText = currentText;
    
    if (INCLUDE_SPEAKERS && currentSpeaker) {
      finalText = `[${currentSpeaker}] ${currentText}`;
    }
    
    srtContent += formatSRTSegment(segmentIndex, segmentStart, segmentEnd, finalText);
  }
  
  return srtContent;
}

// ========================================
// 執行生成
// ========================================

const srtContent = generateSRT(words, MAX_CHARS, MAX_DURATION);

const wordCount = words.filter(w => w.type === 'word').length;
const speakers = [...new Set(words.filter(w => w.speaker_id).map(w => w.speaker_id))];
const segments = srtContent.split('\n\n').filter(s => s.trim()).length;

// ========================================
// 輸出結果
// ========================================

return {
  json: {
    srt: srtContent,
    transcription: elevenLabsResult.text,
    language: elevenLabsResult.language_code,
    language_probability: elevenLabsResult.language_probability,
    word_count: wordCount,
    total_words: words.length,
    segment_count: segments,
    speakers_detected: speakers.length,
    speakers: speakers,
    settings: {
      max_chars: MAX_CHARS,
      max_duration: MAX_DURATION,
      include_speakers: INCLUDE_SPEAKERS
    }
  }
};
```

4. 點擊 **Execute Node** 測試

---

## 📊 輸出數據說明

Code 節點執行後會輸出：

```json
{
  "srt": "完整的 SRT 字幕內容...",
  "transcription": "完整的轉錄文字",
  "language": "zho",
  "language_probability": 0.999,
  "word_count": 223,
  "segment_count": 18,
  "speakers_detected": 2,
  "speakers": ["speaker_0", "speaker_1"]
}
```

---

## 🎯 如何使用輸出

### 方法 1: 保存為 SRT 檔案

添加 **Write Binary File** 節點：
```
File Path: /tmp/{{ $json.filename }}.srt
Data: {{ $json.srt }}
```

### 方法 2: 顯示在畫面上

添加 **Set** 節點：
```
Value: {{ $json.srt }}
```

### 方法 3: 傳送到其他服務

直接使用變數：
```
{{ $json.srt }}
```

---

## ⚙️ 參數調整指南

### MAX_CHARS（每段最多字符數）

```javascript
const MAX_CHARS = 15;  // 適合短影片、手機觀看
const MAX_CHARS = 18;  // 推薦值（測試最佳）
const MAX_CHARS = 32;  // YouTube 標準
const MAX_CHARS = 40;  // 長影片、桌面觀看
```

### MAX_DURATION（每段最長時間）

```javascript
const MAX_DURATION = 3.0;  // 快節奏影片
const MAX_DURATION = 5.0;  // 推薦值
const MAX_DURATION = 7.0;  // 慢節奏影片
```

### INCLUDE_SPEAKERS（說話者標識）

```javascript
const INCLUDE_SPEAKERS = true;   // 顯示 [speaker_0] 文字...
const INCLUDE_SPEAKERS = false;  // 只顯示 文字...
```

---

## 🔍 故障排除

### 問題 1: HTTP Request 失敗（401 Unauthorized）

**解決方案**:
- 檢查 API Key 是否正確
- 確認 Header Name 是 `xi-api-key`（不是 `Authorization`）

### 問題 2: 沒有返回 words 陣列

**解決方案**:
- 確認 `model_id` 設定為 `scribe_v1`
- 檢查音檔格式是否支援

### 問題 3: Code 節點報錯

**解決方案**:
- 確認前一個節點有成功返回 JSON
- 檢查 `$input.item.json.words` 是否存在

### 問題 4: SRT 格式不正確

**解決方案**:
- 檢查 `formatSRTTime` 函數的輸出
- 確認時間格式為 `HH:MM:SS,mmm`

---

## ✅ 完整的 Workflow 流程

```
┌─────────────────┐
│  Download Audio │
│  (已有節點)      │
└────────┬────────┘
         │ binary data
         ↓
┌─────────────────────────┐
│  HTTP Request           │
│  (ElevenLabs Transcribe)│
│  - Method: POST         │
│  - URL: /speech-to-text │
│  - Body: file + model_id│
└────────┬────────────────┘
         │ JSON (含 words 陣列)
         ↓
┌─────────────────────────┐
│  Code                   │
│  (Generate Custom SRT)  │
│  - 讀取 words           │
│  - 按 18 字符重組       │
│  - 生成 SRT 格式        │
└────────┬────────────────┘
         │ JSON (含 srt 欄位)
         ↓
┌─────────────────────────┐
│  後續處理               │
│  - 保存檔案             │
│  - 或傳送到其他服務     │
└─────────────────────────┘
```

---

## 🎨 進階技巧

### 技巧 1: 動態調整字符數

```javascript
// 根據語言調整字符數
const MAX_CHARS = elevenLabsResult.language_code === 'zho' ? 18 : 32;
```

### 技巧 2: 根據影片長度調整

```javascript
// 根據音檔長度調整段落時間
const audioDuration = words[words.length - 1].end;
const MAX_DURATION = audioDuration > 600 ? 7.0 : 5.0;  // 10分鐘以上用7秒
```

### 技巧 3: 添加字幕樣式

```javascript
// 在 SRT 中添加 ASS 樣式標記
let finalText = currentText;
if (currentSpeaker === 'speaker_0') {
  finalText = `{\\c&H00FF00&}${currentText}`;  // 綠色
} else if (currentSpeaker === 'speaker_1') {
  finalText = `{\\c&H0000FF&}${currentText}`;  // 紅色
}
```

---

## 📝 快速複製區域

### HTTP Request 節點設定（快速複製）

```
URL: https://api.elevenlabs.io/v1/speech-to-text
Method: POST
Authentication: Header Auth
  Header Name: xi-api-key
  Header Value: [您的API Key]
Body Content Type: Multipart-Form Data
Body Parameters:
  - model_id: scribe_v1
Send Binary Data: ✅
Binary Property: data
Timeout: 120000
```

### Code 節點設定（完整代碼在上方）

**只需要調整這三個參數**：
```javascript
const MAX_CHARS = 18;      // 字符數
const MAX_DURATION = 5.0;  // 時間限制
const INCLUDE_SPEAKERS = true;  // 說話者標識
```

---

## 🎉 完成後的效果

### 輸入（Download Audio）:
```
音檔: test_audio.mp3
時長: 69 秒
```

### 輸出（Code 節點）:
```json
{
  "srt": "1\n00:00:00,500 --> 00:00:03,299\n美国白宫直接把进口中国商品的关税从百\n\n2\n00:00:03,299 --> 00:00:06,500\n分之一百四十五爽拉到百分之两百四十五\n\n...",
  "segment_count": 18,
  "word_count": 223,
  "speakers_detected": 0
}
```

### 使用 SRT:
```
{{ $json.srt }}  ← 直接在後續節點中使用
```

---

## 💡 常見應用場景

### 場景 1: 自動生成影片字幕
```
Download Audio → ElevenLabs → Generate SRT → Upload to Video Platform
```

### 場景 2: 批量處理音檔
```
Read Files from Folder → Loop → Download Audio → ElevenLabs → Generate SRT → Save
```

### 場景 3: 多語言字幕生成
```
Download Audio → ElevenLabs → Check Language → Generate SRT (調整參數) → Save
```

---

## 📞 需要幫助？

如果遇到問題，檢查：
1. ✅ API Key 是否正確設定
2. ✅ HTTP Request 是否成功返回（有 words 陣列）
3. ✅ Code 節點是否能讀取到 `$input.item.json.words`
4. ✅ 生成的 SRT 格式是否正確

---

**設定完成後，您的 workflow 就能自動將音檔轉換為精確的 18 字符 SRT 字幕了！** 🎊




