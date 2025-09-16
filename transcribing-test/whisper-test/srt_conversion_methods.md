# 非直接 SRT 輸出模型的字幕轉換方法詳解

## 概述

大多數語音轉文字 API 服務（如 Google Cloud Speech-to-Text、Azure Speech、AWS Transcribe）並不直接提供 SRT 格式輸出，而是提供包含時間戳記的 JSON 或其他結構化數據。本文檔詳細說明如何將這些數據轉換為標準 SRT 格式。

## 1. 常見的非直接 SRT 模型輸出格式

### Google Cloud Speech-to-Text
```json
{
  "results": [
    {
      "alternatives": [
        {
          "transcript": "你好世界",
          "confidence": 0.95,
          "words": [
            {
              "word": "你好",
              "startTime": "0.100s",
              "endTime": "0.800s"
            },
            {
              "word": "世界",
              "startTime": "0.800s", 
              "endTime": "1.300s"
            }
          ]
        }
      ]
    }
  ]
}
```

### Azure Speech Services
```json
{
  "DisplayText": "你好世界",
  "Duration": 13000000,
  "Offset": 1000000,
  "NBest": [
    {
      "Confidence": 0.95,
      "Display": "你好世界",
      "Words": [
        {
          "Word": "你好",
          "Offset": 1000000,
          "Duration": 7000000
        },
        {
          "Word": "世界", 
          "Offset": 8000000,
          "Duration": 5000000
        }
      ]
    }
  ]
}
```

### AWS Transcribe
```json
{
  "results": {
    "transcripts": [
      {
        "transcript": "你好世界"
      }
    ],
    "items": [
      {
        "start_time": "0.10",
        "end_time": "0.80", 
        "alternatives": [
          {
            "confidence": "0.95",
            "content": "你好"
          }
        ],
        "type": "pronunciation"
      },
      {
        "start_time": "0.80",
        "end_time": "1.30",
        "alternatives": [
          {
            "confidence": "0.95", 
            "content": "世界"
          }
        ],
        "type": "pronunciation"
      }
    ]
  }
}
```

## 2. SRT 轉換方法

### 方法 1: 基於詞彙級時間戳記的轉換（最精確）

這是目前最精確的方法，利用每個詞彙的開始和結束時間來創建合理的字幕段落。

```python
def convert_to_srt_word_level(transcription_data, max_chars_per_subtitle=50, max_duration=5.0):
    """
    基於詞彙級時間戳記轉換為 SRT
    
    Args:
        transcription_data: 包含詞彙級時間戳記的轉錄數據
        max_chars_per_subtitle: 每個字幕段落的最大字符數
        max_duration: 每個字幕段落的最大持續時間（秒）
    """
    subtitles = []
    current_subtitle = {
        'start_time': None,
        'end_time': None,
        'text': ''
    }
    
    for word_data in transcription_data['words']:
        word = word_data['word']
        start_time = float(word_data['start_time'])
        end_time = float(word_data['end_time'])
        
        # 如果是第一個詞或需要開始新段落
        if (current_subtitle['start_time'] is None or 
            len(current_subtitle['text'] + word) > max_chars_per_subtitle or
            (end_time - current_subtitle['start_time']) > max_duration):
            
            # 保存當前字幕段落
            if current_subtitle['text']:
                subtitles.append(current_subtitle.copy())
            
            # 開始新段落
            current_subtitle = {
                'start_time': start_time,
                'end_time': end_time,
                'text': word
            }
        else:
            # 添加到當前段落
            current_subtitle['text'] += ' ' + word
            current_subtitle['end_time'] = end_time
    
    # 添加最後一個段落
    if current_subtitle['text']:
        subtitles.append(current_subtitle)
    
    return generate_srt_content(subtitles)

def generate_srt_content(subtitles):
    """生成標準 SRT 格式內容"""
    srt_content = []
    
    for i, subtitle in enumerate(subtitles, 1):
        start_time = format_time(subtitle['start_time'])
        end_time = format_time(subtitle['end_time'])
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(subtitle['text'])
        srt_content.append("")  # 空行
    
    return "\n".join(srt_content)

def format_time(seconds):
    """將秒數轉換為 SRT 時間格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
```

### 方法 2: 基於句子分割的轉換

```python
def convert_to_srt_sentence_level(transcription_data, max_chars_per_subtitle=80):
    """
    基於句子分割轉換為 SRT
    適用於沒有詞彙級時間戳記的情況
    """
    import re
    
    full_text = transcription_data['transcript']
    start_time = transcription_data['start_time']
    end_time = transcription_data['end_time']
    total_duration = end_time - start_time
    
    # 使用正則表達式分割句子
    sentences = re.split(r'[。！？.!?]', full_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    subtitles = []
    total_chars = sum(len(s) for s in sentences)
    current_time = start_time
    
    for sentence in sentences:
        # 基於字符數比例估算時間
        sentence_duration = (len(sentence) / total_chars) * total_duration
        
        # 確保最小持續時間
        sentence_duration = max(sentence_duration, 1.0)
        
        # 分割過長的句子
        if len(sentence) > max_chars_per_subtitle:
            parts = split_long_sentence(sentence, max_chars_per_subtitle)
            part_duration = sentence_duration / len(parts)
            
            for part in parts:
                subtitles.append({
                    'start_time': current_time,
                    'end_time': current_time + part_duration,
                    'text': part
                })
                current_time += part_duration
        else:
            subtitles.append({
                'start_time': current_time,
                'end_time': current_time + sentence_duration,
                'text': sentence
            })
            current_time += sentence_duration
    
    return generate_srt_content(subtitles)

def split_long_sentence(sentence, max_chars):
    """分割過長的句子"""
    parts = []
    words = sentence.split()
    current_part = ""
    
    for word in words:
        if len(current_part + word) <= max_chars:
            current_part += word + " "
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = word + " "
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts
```

### 方法 3: 智能分段算法（推薦）

```python
def intelligent_srt_conversion(transcription_data, 
                             max_chars_per_subtitle=60,
                             max_duration=4.0,
                             min_duration=1.0):
    """
    智能 SRT 轉換算法
    結合語義分析、時間控制和字符限制
    """
    import nltk
    from nltk.tokenize import sent_tokenize
    
    # 如果有詞彙級時間戳記，使用方法1
    if 'words' in transcription_data:
        return convert_with_word_timing(transcription_data, max_chars_per_subtitle, max_duration)
    
    # 否則使用智能分段
    text = transcription_data['transcript']
    start_time = transcription_data['start_time']
    end_time = transcription_data['end_time']
    
    # 使用 NLTK 進行更準確的句子分割
    sentences = sent_tokenize(text)
    
    subtitles = []
    current_subtitle = {
        'start_time': start_time,
        'text': '',
        'sentences': []
    }
    
    total_chars = len(text)
    processed_chars = 0
    
    for sentence in sentences:
        # 計算當前處理進度對應的時間點
        sentence_progress = processed_chars / total_chars
        sentence_start = start_time + (end_time - start_time) * sentence_progress
        
        processed_chars += len(sentence)
        next_progress = processed_chars / total_chars
        sentence_end = start_time + (end_time - start_time) * next_progress
        
        # 檢查是否需要開始新的字幕段落
        potential_text = current_subtitle['text'] + ' ' + sentence if current_subtitle['text'] else sentence
        potential_duration = sentence_end - current_subtitle['start_time']
        
        if (len(potential_text) > max_chars_per_subtitle or 
            potential_duration > max_duration or
            is_natural_break(sentence)):
            
            # 完成當前字幕段落
            if current_subtitle['text']:
                current_subtitle['end_time'] = sentence_start
                # 確保最小持續時間
                if current_subtitle['end_time'] - current_subtitle['start_time'] < min_duration:
                    current_subtitle['end_time'] = current_subtitle['start_time'] + min_duration
                
                subtitles.append(current_subtitle.copy())
            
            # 開始新的字幕段落
            current_subtitle = {
                'start_time': sentence_start,
                'text': sentence,
                'sentences': [sentence]
            }
        else:
            # 添加到當前段落
            current_subtitle['text'] = potential_text
            current_subtitle['sentences'].append(sentence)
    
    # 處理最後一個段落
    if current_subtitle['text']:
        current_subtitle['end_time'] = end_time
        subtitles.append(current_subtitle)
    
    return generate_srt_content(subtitles)

def is_natural_break(sentence):
    """判斷是否為自然的分段點"""
    # 檢查句子是否以強烈的結束標點符號結尾
    strong_endings = ['。', '！', '？', '.', '!', '?']
    return any(sentence.strip().endswith(ending) for ending in strong_endings)
```

## 3. 不同方法的優缺點比較

### 詞彙級時間戳記方法
**優點:**
- 時間精確度最高
- 可以精確控制每個詞的時間
- 適合製作高質量字幕

**缺點:**
- 需要支援詞彙級時間戳記的 API
- 計算複雜度較高
- 成本通常較高

### 句子分割方法  
**優點:**
- 實現簡單
- 適用於大多數 API
- 成本較低

**缺點:**
- 時間精確度較低
- 依賴文本分析質量
- 可能出現時間不同步

### 智能分段方法
**優點:**
- 平衡精確度和實用性
- 考慮語義完整性
- 可調節參數多

**缺點:**
- 實現複雜度中等
- 需要額外的 NLP 工具
- 調優需要經驗

## 4. 推薦的最佳實踐

1. **優先使用詞彙級時間戳記**：如果 API 支援，這是最精確的方法
2. **智能參數設置**：
   - 最大字符數：50-80 字符（中文）
   - 最大持續時間：3-5 秒
   - 最小持續時間：1-2 秒
3. **後處理優化**：
   - 檢查時間重疊
   - 調整過短或過長的段落
   - 優化分段點
4. **質量檢查**：
   - 驗證 SRT 格式正確性
   - 檢查時間連續性
   - 測試播放效果

## 5. 解決您提到的問題

針對您遇到的「whisper-1 SRT 段落過長」問題，可以使用以下策略：

```python
def fix_long_srt_segments(srt_content, max_chars=50, max_duration=4.0):
    """
    修復過長的 SRT 段落
    """
    segments = parse_srt(srt_content)
    fixed_segments = []
    
    for segment in segments:
        duration = segment['end_time'] - segment['start_time']
        text_length = len(segment['text'])
        
        # 如果段落過長，需要分割
        if text_length > max_chars or duration > max_duration:
            sub_segments = split_segment_intelligently(segment, max_chars, max_duration)
            fixed_segments.extend(sub_segments)
        else:
            fixed_segments.append(segment)
    
    return generate_srt_content(fixed_segments)
```

這種方法可以後處理 whisper-1 的輸出，解決段落過長的問題，同時保持時間準確性。
