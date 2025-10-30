# 🎯 n8n 實現 ElevenLabs 詞彙級 SRT 完整指南

## 📋 流程概述

```
Download Audio → ElevenLabs 轉錄 → 處理詞彙級數據 → 生成自定義 SRT
```

---

## 🔧 n8n Workflow 配置

### 節點 1: Download Audio（已有）
- 下載音檔到 n8n
- 輸出：音檔的 binary data

---

### 節點 2: ElevenLabs Speech-to-Text（HTTP Request）

**節點類型**: `HTTP Request`

**配置**:
```
Method: POST
URL: https://api.elevenlabs.io/v1/speech-to-text

Authentication: Generic Credential Type
  → Header Auth
  → Name: xi-api-key
  → Value: {{$credentials.elevenLabsApi.apiKey}}

Body Content Type: Multipart-Form
```

**Parameters (Form Data)**:
```
file: {{$binary.data}}
model_id: scribe_v1
```

**Options**:
- Response Format: JSON
- Timeout: 120000 (120秒)

**預期輸出**:
```json
{
  "language_code": "zho",
  "language_probability": 0.999,
  "text": "完整的轉錄文字...",
  "words": [
    {
      "text": "美",
      "start": 0.5,
      "end": 0.659,
      "type": "word",
      "logprob": 0.0
    },
    ...
  ]
}
```

---

### 節點 3: Code (Function) - 生成自定義 SRT

**節點類型**: `Code`

**配置**:
```javascript
// 從 ElevenLabs 結果中提取 words
const elevenLabsResult = $input.item.json;
const words = elevenLabsResult.words || [];

// 設定參數
const MAX_CHARS = 18;  // 每段最多字符數（可調整）
const MAX_DURATION = 5.0;  // 每段最長時間（秒）

// 生成 SRT 的函數
function generateSRT(words, maxChars, maxDuration) {
  let srtContent = "";
  let segmentIndex = 1;
  let currentSegment = [];
  let currentText = "";
  let segmentStart = null;
  
  for (const word of words) {
    // 只處理 word 類型，跳過 spacing 和 audio_event
    if (word.type !== 'word') {
      continue;
    }
    
    const wordText = word.text;
    const wordStart = word.start;
    const wordEnd = word.end;
    
    if (segmentStart === null) {
      segmentStart = wordStart;
    }
    
    // 檢查是否需要開始新段落
    const potentialText = currentText + wordText;
    const currentDuration = currentSegment.length > 0 
      ? wordEnd - segmentStart 
      : 0;
    
    const shouldBreak = (
      potentialText.length > maxChars && currentSegment.length > 0
    ) || (
      currentDuration > maxDuration && currentSegment.length > 0
    );
    
    if (shouldBreak) {
      // 生成當前段落
      const segmentEnd = currentSegment[currentSegment.length - 1].end;
      srtContent += formatSRTSegment(segmentIndex, segmentStart, segmentEnd, currentText);
      
      // 開始新段落
      segmentIndex++;
      currentSegment = [word];
      currentText = wordText;
      segmentStart = wordStart;
    } else {
      currentSegment.push(word);
      currentText = potentialText;
    }
  }
  
  // 處理最後一個段落
  if (currentSegment.length > 0) {
    const segmentEnd = currentSegment[currentSegment.length - 1].end;
    srtContent += formatSRTSegment(segmentIndex, segmentStart, segmentEnd, currentText);
  }
  
  return srtContent;
}

// 格式化 SRT 時間
function formatSRTTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const milliseconds = Math.floor((seconds % 1) * 1000);
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')},${milliseconds.toString().padStart(3, '0')}`;
}

// 格式化單個 SRT 段落
function formatSRTSegment(index, startSec, endSec, text) {
  const startTime = formatSRTTime(startSec);
  const endTime = formatSRTTime(endSec);
  
  return `${index}\n${startTime} --> ${endTime}\n${text}\n\n`;
}

// 生成 SRT
const srtContent = generateSRT(words, MAX_CHARS, MAX_DURATION);

// 輸出結果
return {
  json: {
    srt: srtContent,
    transcription: elevenLabsResult.text,
    language: elevenLabsResult.language_code,
    word_count: words.filter(w => w.type === 'word').length,
    total_words: words.length
  }
};
```

---

### 節點 4: 保存或使用 SRT

**選項 A: 保存為檔案**
- 節點類型: `Write Binary File`
- File Name: `{{ $json.filename }}.srt`
- Data: `{{ $json.srt }}`

**選項 B: 傳送到下一個節點**
- 直接使用 `{{ $json.srt }}` 變數

---

## 🎨 完整的 n8n Workflow JSON

### 可直接導入的 Workflow

```json
{
  "name": "ElevenLabs 詞彙級 SRT 生成",
  "nodes": [
    {
      "parameters": {
        "url": "https://api.elevenlabs.io/v1/speech-to-text",
        "authentication": "headerAuth",
        "sendBody": true,
        "contentType": "multipart-form-data",
        "bodyParameters": {
          "parameters": [
            {
              "name": "model_id",
              "value": "scribe_v1"
            }
          ]
        },
        "options": {
          "timeout": 120000
        }
      },
      "name": "ElevenLabs Transcribe",
      "type": "n8n-nodes-base.httpRequest",
      "position": [500, 300],
      "credentials": {
        "headerAuth": {
          "id": "1",
          "name": "ElevenLabs API"
        }
      }
    },
    {
      "parameters": {
        "jsCode": "// 完整的 JavaScript 代碼（見上方）"
      },
      "name": "Generate SRT",
      "type": "n8n-nodes-base.code",
      "position": [700, 300]
    }
  ],
  "connections": {
    "ElevenLabs Transcribe": {
      "main": [
        [
          {
            "node": "Generate SRT",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## 🔑 設定 ElevenLabs API Credentials

在 n8n 中設定認證：

1. **前往**: Credentials → Add Credential
2. **選擇**: Header Auth
3. **設定**:
   ```
   Name: ElevenLabs API
   Header Name: xi-api-key
   Header Value: sk_c10b61842ead12201698676af90f1421d5f6e3cd555317ec
   ```

---

## 📝 可調整參數

在 Code 節點中，您可以調整：

```javascript
const MAX_CHARS = 18;      // 每段最多字符數
const MAX_DURATION = 5.0;  // 每段最長時間（秒）
```

**建議值**：
- 短影片字幕: `MAX_CHARS = 15-20`
- 長影片字幕: `MAX_CHARS = 30-40`
- YouTube 字幕: `MAX_CHARS = 32`（YouTube 建議）

---

## 🧪 測試步驟

### 步驟 1: 設定 Credentials
```
n8n → Credentials → Add → Header Auth
Name: xi-api-key
Value: [您的 ElevenLabs API Key]
```

### 步驟 2: 創建 HTTP Request 節點
```
Method: POST
URL: https://api.elevenlabs.io/v1/speech-to-text
Authentication: Header Auth (ElevenLabs API)
Body: Multipart-Form
  - file: {{$binary.data}}
  - model_id: scribe_v1
```

### 步驟 3: 添加 Code 節點
- 貼上上方的 JavaScript 代碼
- 調整 `MAX_CHARS` 參數

### 步驟 4: 測試執行
- 上傳測試音檔
- 檢查輸出的 SRT 格式
- 驗證段落長度

---

## ✅ 預期輸出範例

### JSON 輸出：
```json
{
  "srt": "1\n00:00:00,500 --> 00:00:03,299\n美国白宫直接把进口中国商品的关税从百\n\n2\n00:00:03,299 --> 00:00:06,500\n分之一百四十五爽拉到百分之两百四十五\n\n...",
  "transcription": "完整的轉錄文字...",
  "language": "zho",
  "word_count": 223,
  "total_words": 325
}
```

### SRT 內容：
```srt
1
00:00:00,500 --> 00:00:03,299
美国白宫直接把进口中国商品的关税从百

2
00:00:03,299 --> 00:00:06,500
分之一百四十五爽拉到百分之两百四十五

3
00:00:06,500 --> 00:00:09,420
，中美贸易战火直接加大马力。连准会主
```

---

## 🚀 進階功能

### 功能 1: 添加說話者標識（如果 ElevenLabs 返回 speaker_id）

在 Code 節點中添加：

```javascript
// 檢查是否有說話者資訊
function generateSRTWithSpeakers(words, maxChars) {
  let srtContent = "";
  let segmentIndex = 1;
  let currentSpeaker = null;
  let currentSegment = [];
  let currentText = "";
  let segmentStart = null;
  
  for (const word of words) {
    if (word.type !== 'word') continue;
    
    const speaker = word.speaker_id || null;
    const wordText = word.text;
    
    // 如果說話者改變，開始新段落
    if (currentSpeaker && speaker !== currentSpeaker) {
      const segmentEnd = currentSegment[currentSegment.length - 1].end;
      const textWithSpeaker = `[${currentSpeaker}] ${currentText}`;
      srtContent += formatSRTSegment(segmentIndex, segmentStart, segmentEnd, textWithSpeaker);
      
      segmentIndex++;
      currentSegment = [word];
      currentText = wordText;
      segmentStart = word.start;
      currentSpeaker = speaker;
    } else {
      if (!currentSpeaker) currentSpeaker = speaker;
      if (!segmentStart) segmentStart = word.start;
      currentSegment.push(word);
      currentText += wordText;
    }
  }
  
  // 處理最後段落
  if (currentSegment.length > 0) {
    const segmentEnd = currentSegment[currentSegment.length - 1].end;
    const textWithSpeaker = currentSpeaker ? `[${currentSpeaker}] ${currentText}` : currentText;
    srtContent += formatSRTSegment(segmentIndex, segmentStart, segmentEnd, textWithSpeaker);
  }
  
  return srtContent;
}

// 檢查第一個 word 是否有 speaker_id
const hasSpeakers = words.some(w => w.speaker_id);

const srtContent = hasSpeakers 
  ? generateSRTWithSpeakers(words, MAX_CHARS)
  : generateSRT(words, MAX_CHARS, MAX_DURATION);
```

---

### 功能 2: 處理音頻事件（laughter, applause）

```javascript
// 在生成 SRT 時包含音頻事件
function generateSRTWithEvents(words, maxChars) {
  // ... 原有邏輯 ...
  
  for (const word of words) {
    if (word.type === 'audio_event') {
      // 添加音頻事件標記
      currentText += `[${word.text}]`;
      continue;
    }
    
    if (word.type === 'word') {
      // 處理正常詞彙
      currentText += word.text;
    }
  }
  
  // ... 其餘邏輯 ...
}
```

---

## 📊 完整的 Code 節點代碼（可直接使用）

```javascript
// ========================================
// ElevenLabs 詞彙級 SRT 生成器
// 作者: AI Team
// 日期: 2025-10-19
// ========================================

// 從 ElevenLabs 結果中提取 words
const elevenLabsResult = $input.item.json;
const words = elevenLabsResult.words || [];

// ========================================
// 可調整參數
// ========================================
const MAX_CHARS = 18;      // 每段最多字符數
const MAX_DURATION = 5.0;  // 每段最長時間（秒）
const INCLUDE_SPEAKERS = true;  // 是否包含說話者標識

// ========================================
// 核心函數
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
    // 只處理 word 類型
    if (word.type !== 'word') {
      continue;
    }
    
    const wordText = word.text;
    const wordStart = word.start;
    const wordEnd = word.end;
    const speaker = word.speaker_id || null;
    
    if (segmentStart === null) {
      segmentStart = wordStart;
    }
    
    if (currentSpeaker === null) {
      currentSpeaker = speaker;
    }
    
    // 檢查是否需要開始新段落
    const potentialText = currentText + wordText;
    const currentDuration = currentSegment.length > 0 ? wordEnd - segmentStart : 0;
    
    // 說話者改變或超過字數/時間限制
    const shouldBreak = (
      (INCLUDE_SPEAKERS && speaker && speaker !== currentSpeaker) ||
      (potentialText.length > maxChars && currentSegment.length > 0) ||
      (currentDuration > maxDuration && currentSegment.length > 0)
    );
    
    if (shouldBreak) {
      // 生成當前段落
      const segmentEnd = currentSegment[currentSegment.length - 1].end;
      let finalText = currentText;
      
      // 添加說話者標識
      if (INCLUDE_SPEAKERS && currentSpeaker) {
        finalText = `[${currentSpeaker}] ${currentText}`;
      }
      
      srtContent += formatSRTSegment(segmentIndex, segmentStart, segmentEnd, finalText);
      
      // 開始新段落
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
  
  // 處理最後一個段落
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
// 主要執行
// ========================================

const srtContent = generateSRT(words, MAX_CHARS, MAX_DURATION);

// 統計資訊
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
    max_chars_setting: MAX_CHARS,
    max_duration_setting: MAX_DURATION
  }
};
```

---

## 🎯 使用方式

### 在 n8n 中的操作步驟：

1. **在 Download Audio 後添加 HTTP Request 節點**
   - 配置為 ElevenLabs API 調用
   - 將音檔傳送到 ElevenLabs

2. **添加 Code 節點**
   - 貼上上方的完整代碼
   - 調整 `MAX_CHARS` 參數（建議 18）

3. **添加後續節點處理 SRT**
   - 可以保存為檔案
   - 可以傳送到其他服務
   - 可以顯示或下載

---

## 📊 輸出數據結構

Code 節點會輸出：

```json
{
  "srt": "完整的 SRT 內容...",
  "transcription": "完整的轉錄文字",
  "language": "zho",
  "language_probability": 0.999,
  "word_count": 223,
  "total_words": 325,
  "segment_count": 18,
  "speakers_detected": 0,
  "speakers": [],
  "max_chars_setting": 18,
  "max_duration_setting": 5
}
```

**可用變數**：
- `{{ $json.srt }}` - SRT 字幕內容
- `{{ $json.transcription }}` - 完整文字
- `{{ $json.segment_count }}` - 段落數量
- `{{ $json.speakers }}` - 檢測到的說話者

---

## ⚙️ 進階配置

### 配置 1: 不同字數的段落

```javascript
const MAX_CHARS = 15;  // YouTube 短片
const MAX_CHARS = 32;  // YouTube 標準
const MAX_CHARS = 42;  // 長影片
```

### 配置 2: 關閉說話者標識

```javascript
const INCLUDE_SPEAKERS = false;
```

### 配置 3: 只在說話者改變時換行

```javascript
// 修改 shouldBreak 條件
const shouldBreak = (
  (speaker && speaker !== currentSpeaker)  // 只在說話者改變時換行
);
```

---

## 🎉 完成！

現在您的 n8n workflow 可以：
1. ✅ 接收音檔（Download Audio）
2. ✅ 發送到 ElevenLabs Scribe V1 轉錄
3. ✅ 獲得 325 個詞彙的精確時間戳記
4. ✅ 自動重組為 18 字符段落的 SRT
5. ✅ 如果有多人，自動添加說話者標識
6. ✅ 輸出完整的 SRT 字幕檔

**下一步**: 在 n8n 中實際創建這些節點並測試！


