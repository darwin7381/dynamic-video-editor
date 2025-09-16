# API Keys 設定說明

## 📋 概要

所有的 API keys 已從腳本中移除並移到環境變數中，以提高安全性。

## 🔧 設定步驟

### 1. 複製環境變數範本
```bash
cp .env.example .env
```

### 2. 編輯 .env 檔案
在 `.env` 檔案中填入您的實際 API keys：

```bash
# ElevenLabs API Key
ELEVENLABS_API_KEY=your_actual_elevenlabs_key_here

# AssemblyAI API Keys
ASSEMBLYAI_API_KEY=your_actual_assemblyai_key_here
ASSEMBLYAI_API_KEY_2=your_backup_assemblyai_key_here

# Groq API Keys
GROQ_API_KEY=your_actual_groq_key_here
GROQ_API_KEY_2=your_backup_groq_key_here

# OpenAI API Key (optional)
OPENAI_API_KEY=your_actual_openai_key_here
```

### 3. 確保依賴已安裝
```bash
uv add python-dotenv
```

## 🔐 API Keys 獲取方式

### ElevenLabs
- 訪問: https://elevenlabs.io/app/speech-synthesis
- 登入後在 Profile > API Keys 頁面獲取

### AssemblyAI
- 訪問: https://www.assemblyai.com/app/account
- 登入後在 Account 頁面找到 API Key

### Groq
- 訪問: https://console.groq.com/keys
- 登入後創建新的 API Key

### OpenAI (可選)
- 訪問: https://platform.openai.com/api-keys
- 登入後創建新的 API Key

## ⚠️ 重要注意事項

1. **不要提交 .env 檔案**
   - `.env` 檔案已被加入 `.gitignore`
   - 只提交 `.env.example` 範本檔案

2. **API Key 格式**
   - ElevenLabs: `sk_` 開頭，48 字符
   - AssemblyAI: `f` 開頭，32 字符
   - Groq: `gsk_` 開頭，52 字符
   - OpenAI: `sk-proj-` 開頭，約 100+ 字符

3. **備用 Keys**
   - 某些腳本使用備用 API keys (如 `GROQ_API_KEY_2`)
   - 建議設定備用 keys 以避免 API 限制

## 🧪 測試設定

運行任何測試腳本前，確保：
```bash
# 檢查環境變數是否載入
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('ElevenLabs Key:', 'OK' if os.getenv('ELEVENLABS_API_KEY') else 'Missing')
print('AssemblyAI Key:', 'OK' if os.getenv('ASSEMBLYAI_API_KEY') else 'Missing')
print('Groq Key:', 'OK' if os.getenv('GROQ_API_KEY') else 'Missing')
"
```

## 🎉 已修復的檔案

總共修復了 29 個 Python 檔案，包括：
- `test_segment_level_comparison.py`
- `final_elevenlabs_assemblyai_test.py`
- `test_groq_assemblyai_segment.py`
- 以及其他 26 個測試腳本

所有腳本現在都會自動從 `.env` 檔案載入 API keys。
