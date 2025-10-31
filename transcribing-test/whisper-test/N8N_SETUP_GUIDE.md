# 🚀 n8n ElevenLabs 詞彙級 SRT 設定指南

## 📋 快速開始（3 步驟）

### 步驟 1: 設定 ElevenLabs API Credential

1. 在 n8n 中點擊右上角的 **Credentials**
2. 點擊 **Add Credential**
3. 搜尋並選擇 **Header Auth**
4. 設定如下：
   ```
   Credential Name: ElevenLabs API Key
   Name: xi-api-key
   Value: sk_c10b61842ead12201698676af90f1421d5f6e3cd555317ec
   ```
5. 點擊 **Save**

---

### 步驟 2: 在 Download Audio 後添加 HTTP Request 節點

1. 點擊 Download Audio 節點後的 **+** 號
2. 搜尋並添加 **HTTP Request** 節點
3. 配置如下：

   **Basic Settings**:
   ```
   Method: POST
   URL: https://api.elevenlabs.io/v1/speech-to-text
   ```

   **Authentication**:
   ```
   Authentication: Generic Credential Type
   Generic Auth Type: Header Auth
   Credential: ElevenLabs API Key (剛剛創建的)
   ```

   **Body**:
   ```
   Send Body: ✅ (打勾)
   Body Content Type: Multipart-Form Data
   
   Body Parameters:
   - Name: model_id
     Value: scribe_v1
   ```

   **Binary Data**:
   ```
   Send Binary Data: ✅ (打勾)
   Input Data Field Name: data
   ```

   **Options**:
   ```
   Timeout: 120000
   ```

4. 點擊 **Execute Node** 測試（確保有音檔輸入）

---

### 步驟 3: 添加 Code 節點生成 SRT

1. 點擊 HTTP Request 節點後的 **+** 號
2. 搜尋並添加 **Code** 節點
3. 將以下代碼貼入：

```javascript
// 從 ElevenLabs 結果中提取 words
const elevenLabsResult = $input.item.json;
const words = elevenLabsResult.words || [];

// 可調整參數
const MAX_CHARS = 18;      // 每段最多字符數（建議 15-40）
const MAX_DURATION = 5.0;  // 每段最長時間（秒）
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
"
      },
      "name": "Generate Custom SRT",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [
        900,
        300
      ]
    }
  ],
  "connections": {
    "ElevenLabs Transcribe": {
      "main": [
        [
          {
            "node": "Generate Custom SRT",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [],
  "triggerCount": 0,
  "updatedAt": "2025-10-19T00:00:00.000Z",
  "versionId": "1"
}




