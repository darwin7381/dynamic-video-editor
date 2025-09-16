#!/usr/bin/env python3
"""
真正的段落級測試 - 確保每個服務都成功獲取段落級數據
"""

import os
from dotenv import load_dotenv
import requests
import json
import time
from datetime import timedelta
import assemblyai as aai

# 載入環境變數
load_dotenv()

def format_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = td.total_seconds() % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def test_groq_segment_real():
    """真正測試 Groq 的段落級輸出"""
    print(f"\n🚀 Groq Whisper Large v3 段落級測試")
    print("=" * 60)
    
    # 使用有效的 API Key
    api_key = os.getenv("GROQ_API_KEY")
    audio_file = "../audio-tts-mp3-20250523032437-WJdKQdwW.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 音檔不存在: {audio_file}")
        return None
    
    try:
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        with open(audio_file, 'rb') as f:
            files = {
                "file": (os.path.basename(audio_file), f, "audio/mpeg")
            }
            data = {
                "model": "whisper-large-v3",
                "response_format": "verbose_json",
                "language": "zh"
                # 不指定 timestamp_granularities，預設應該是段落級
            }
            
            print(f"📤 發送 Groq 請求...")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Groq 請求成功")
                
                # 保存完整結果
                with open("groq_segment_real_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"💾 完整結果已保存: groq_segment_real_result.json")
                
                # 檢查段落數據
                if 'segments' in result and result['segments']:
                    segments = result['segments']
                    print(f"✅ 發現 {len(segments)} 個段落級數據")
                    
                    # 生成段落級 SRT
                    srt_content = ""
                    for i, seg in enumerate(segments, 1):
                        text = seg.get('text', '').strip()
                        start = seg.get('start', 0)
                        end = seg.get('end', 0)
                        
                        srt_content += f"{i}\n"
                        srt_content += f"{format_time(start)} --> {format_time(end)}\n"
                        srt_content += f"{text}\n\n"
                    
                    # 保存段落級 SRT
                    with open("groq_segment_real.srt", "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    print(f"💾 段落級 SRT 已保存: groq_segment_real.srt")
                    
                    # 分析段落特性
                    lengths = [len(seg.get('text', '').strip()) for seg in segments]
                    print(f"📊 段落分析:")
                    print(f"  總段落數: {len(segments)}")
                    print(f"  平均長度: {sum(lengths) / len(lengths):.1f} 字符")
                    print(f"  最長段落: {max(lengths)} 字符")
                    print(f"  最短段落: {min(lengths)} 字符")
                    print(f"  長段落數: {sum(1 for l in lengths if l > 25)} 個 (>25字符)")
                    
                    return result
                else:
                    print(f"❌ 沒有找到段落級數據")
                    print(f"可用欄位: {list(result.keys())}")
                    return None
            else:
                print(f"❌ Groq 請求失敗: {response.status_code}")
                print(f"錯誤訊息: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Groq 測試錯誤: {str(e)}")
        return None

def test_assemblyai_segment_real():
    """真正測試 AssemblyAI 的段落級輸出"""
    print(f"\n🚀 AssemblyAI Universal-1 段落級測試")
    print("=" * 60)
    
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    audio_file = "../audio-tts-mp3-20250523032437-WJdKQdwW.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 音檔不存在: {audio_file}")
        return None
    
    try:
        aai.settings.api_key = api_key
        
        # 配置轉錄，確保獲取段落級數據
        config = aai.TranscriptionConfig(
            language_code="zh",
            punctuate=True,
            format_text=True,
            auto_chapters=False  # 確保不要章節，要段落
        )
        
        print(f"📤 上傳音檔並開始 AssemblyAI 轉錄...")
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file, config)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"❌ AssemblyAI 轉錄失敗: {transcript.error}")
            return None
        
        print(f"✅ AssemblyAI 轉錄成功")
        
        # 保存完整結果
        result_data = {
            'text': transcript.text,
            'confidence': transcript.confidence,
            'audio_duration': transcript.audio_duration,
            'status': str(transcript.status)
        }
        
        # 嘗試獲取不同級別的段落數據
        segments = []
        
        # 方法1: 嘗試獲取 sentences (句子級，接近段落級)
        if hasattr(transcript, 'sentences') and transcript.sentences:
            print(f"✅ 發現句子級數據: {len(transcript.sentences)} 個句子")
            for sentence in transcript.sentences:
                segments.append({
                    'text': sentence.text,
                    'start': sentence.start / 1000.0,  # 轉換為秒
                    'end': sentence.end / 1000.0,
                    'confidence': getattr(sentence, 'confidence', 0)
                })
            result_data['segments'] = segments
            result_data['segment_type'] = 'sentences'
        
        # 方法2: 如果沒有句子，嘗試 paragraphs
        elif hasattr(transcript, 'paragraphs') and transcript.paragraphs:
            print(f"✅ 發現段落級數據: {len(transcript.paragraphs.paragraphs)} 個段落")
            for para in transcript.paragraphs.paragraphs:
                segments.append({
                    'text': para.text,
                    'start': para.start / 1000.0,
                    'end': para.end / 1000.0,
                    'confidence': getattr(para, 'confidence', 0)
                })
            result_data['segments'] = segments
            result_data['segment_type'] = 'paragraphs'
        
        # 方法3: 使用 utterances (語句級)
        elif hasattr(transcript, 'utterances') and transcript.utterances:
            print(f"✅ 發現語句級數據: {len(transcript.utterances)} 個語句")
            for utterance in transcript.utterances:
                segments.append({
                    'text': utterance.text,
                    'start': utterance.start / 1000.0,
                    'end': utterance.end / 1000.0,
                    'confidence': getattr(utterance, 'confidence', 0),
                    'speaker': getattr(utterance, 'speaker', 'A')
                })
            result_data['segments'] = segments
            result_data['segment_type'] = 'utterances'
        
        else:
            print(f"⚠️ 沒有找到段落級數據，使用整體文本")
            segments = [{
                'text': transcript.text,
                'start': 0,
                'end': transcript.audio_duration / 1000.0 if transcript.audio_duration else 30,
                'confidence': transcript.confidence
            }]
            result_data['segments'] = segments
            result_data['segment_type'] = 'full_text'
        
        # 保存完整結果
        with open("assemblyai_segment_real_result.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        print(f"💾 完整結果已保存: assemblyai_segment_real_result.json")
        
        # 生成段落級 SRT
        if segments:
            srt_content = ""
            for i, seg in enumerate(segments, 1):
                text = seg['text'].strip()
                start = seg['start']
                end = seg['end']
                
                srt_content += f"{i}\n"
                srt_content += f"{format_time(start)} --> {format_time(end)}\n"
                srt_content += f"{text}\n\n"
            
            # 保存段落級 SRT
            with open("assemblyai_segment_real.srt", "w", encoding="utf-8") as f:
                f.write(srt_content)
            print(f"💾 段落級 SRT 已保存: assemblyai_segment_real.srt")
            
            # 分析段落特性
            lengths = [len(seg['text'].strip()) for seg in segments]
            print(f"📊 段落分析:")
            print(f"  段落類型: {result_data.get('segment_type', 'unknown')}")
            print(f"  總段落數: {len(segments)}")
            print(f"  平均長度: {sum(lengths) / len(lengths):.1f} 字符")
            print(f"  最長段落: {max(lengths)} 字符")
            print(f"  最短段落: {min(lengths)} 字符")
            print(f"  長段落數: {sum(1 for l in lengths if l > 25)} 個 (>25字符)")
            
            return result_data
        else:
            print(f"❌ 沒有有效的段落數據")
            return None
        
    except Exception as e:
        print(f"❌ AssemblyAI 測試錯誤: {str(e)}")
        return None

def test_elevenlabs_segment_real():
    """測試 ElevenLabs 的段落級輸出 (從詞彙級轉換)"""
    print(f"\n🚀 ElevenLabs Scribe 段落級測試")
    print("=" * 60)
    
    # 讀取現有的詞彙級結果
    try:
        with open("elevenlabs_scribe_v1_result.json", "r", encoding="utf-8") as f:
            result = json.load(f)
        print(f"✅ 讀取現有 ElevenLabs 詞彙級結果")
    except:
        print(f"❌ 無法讀取現有結果，需要重新測試")
        return None
    
    # 從詞彙級數據創建段落級數據
    if 'words' in result:
        words = result['words']
        print(f"📝 從 {len(words)} 個詞彙創建段落級數據")
        
        # 創建較長的段落 (模擬真正的段落級)
        segments = []
        current_segment = {
            'text': '',
            'start': words[0]['start'],
            'end': words[0]['end']
        }
        
        for word in words:
            current_segment['text'] += word['text']
            current_segment['end'] = word['end']
            
            # 段落結束條件：遇到句號或長度超過30字符
            if (word['text'] in ['。', '！', '？', '.', '!', '?'] or 
                len(current_segment['text']) > 30):
                
                if current_segment['text'].strip():
                    segments.append(current_segment.copy())
                
                # 開始新段落
                word_idx = words.index(word)
                if word_idx < len(words) - 1:
                    next_word = words[word_idx + 1]
                    current_segment = {
                        'text': '',
                        'start': next_word['start'],
                        'end': next_word['end']
                    }
        
        # 添加最後一個段落
        if current_segment['text'].strip():
            segments.append(current_segment)
        
        # 保存段落級結果
        segment_result = {
            'language_code': result.get('language_code'),
            'language_probability': result.get('language_probability'),
            'text': result.get('text'),
            'segments': segments,
            'segment_type': 'natural_sentences',
            'transcription_id': result.get('transcription_id')
        }
        
        with open("elevenlabs_segment_real_result.json", "w", encoding="utf-8") as f:
            json.dump(segment_result, f, ensure_ascii=False, indent=2)
        print(f"💾 完整結果已保存: elevenlabs_segment_real_result.json")
        
        # 生成段落級 SRT
        srt_content = ""
        for i, seg in enumerate(segments, 1):
            text = seg['text'].strip()
            start = seg['start']
            end = seg['end']
            
            srt_content += f"{i}\n"
            srt_content += f"{format_time(start)} --> {format_time(end)}\n"
            srt_content += f"{text}\n\n"
        
        # 保存段落級 SRT
        with open("elevenlabs_segment_real.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"💾 段落級 SRT 已保存: elevenlabs_segment_real.srt")
        
        # 分析段落特性
        lengths = [len(seg['text'].strip()) for seg in segments]
        print(f"📊 段落分析:")
        print(f"  段落類型: 自然句子分割")
        print(f"  總段落數: {len(segments)}")
        print(f"  平均長度: {sum(lengths) / len(lengths):.1f} 字符")
        print(f"  最長段落: {max(lengths)} 字符")
        print(f"  最短段落: {min(lengths)} 字符")
        print(f"  長段落數: {sum(1 for l in lengths if l > 25)} 個 (>25字符)")
        
        return segment_result
    
    else:
        print(f"❌ 沒有詞彙級數據可供轉換")
        return None

def compare_real_results():
    """比較真實的段落級結果"""
    print(f"\n📊 真實段落級測試結果比較")
    print("=" * 80)
    
    # 檢查生成的文件
    segment_files = [
        ("elevenlabs_segment_real.srt", "ElevenLabs 段落級"),
        ("assemblyai_segment_real.srt", "AssemblyAI 段落級"),
        ("groq_segment_real.srt", "Groq 段落級")
    ]
    
    print(f"📋 生成的段落級 SRT 文件:")
    for filepath, name in segment_files:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✅ {name}: {filepath} ({file_size} bytes)")
        else:
            print(f"  ❌ {name}: {filepath} (不存在)")
    
    # 檢查 JSON 結果文件
    json_files = [
        ("elevenlabs_segment_real_result.json", "ElevenLabs 段落級結果"),
        ("assemblyai_segment_real_result.json", "AssemblyAI 段落級結果"),
        ("groq_segment_real_result.json", "Groq 段落級結果")
    ]
    
    print(f"\n📋 生成的結果 JSON 文件:")
    for filepath, name in json_files:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✅ {name}: {filepath} ({file_size} bytes)")
        else:
            print(f"  ❌ {name}: {filepath} (不存在)")
    
    # 與詞彙級文件比較
    print(f"\n📋 對比詞彙級文件:")
    word_files = [
        ("elevenlabs_precise_18chars.srt", "ElevenLabs 詞彙級"),
        ("assemblyai_precise_18chars.srt", "AssemblyAI 詞彙級"),
        ("final_groq_word_level.srt", "Groq 詞彙級")
    ]
    
    for filepath, name in word_files:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✅ {name}: {filepath} ({file_size} bytes)")
        else:
            print(f"  ❌ {name}: {filepath} (不存在)")

def main():
    """主測試函數"""
    print("🎯 真實段落級測試 - 確保每個服務都成功")
    print("=" * 80)
    print("目標: 獲取真正有時間戳記的段落級 SRT 文件")
    print("=" * 80)
    
    results = {}
    
    # 測試 Groq 段落級
    groq_result = test_groq_segment_real()
    results['Groq'] = groq_result
    
    time.sleep(2)  # 避免 API 限制
    
    # 測試 AssemblyAI 段落級
    assemblyai_result = test_assemblyai_segment_real()
    results['AssemblyAI'] = assemblyai_result
    
    time.sleep(1)
    
    # 測試 ElevenLabs 段落級
    elevenlabs_result = test_elevenlabs_segment_real()
    results['ElevenLabs'] = elevenlabs_result
    
    # 比較結果
    compare_real_results()
    
    # 總結
    print(f"\n🏆 真實測試總結")
    print("=" * 60)
    
    success_count = sum(1 for result in results.values() if result is not None)
    print(f"成功測試: {success_count}/3 個服務")
    
    for service, result in results.items():
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"  {service}: {status}")
    
    if success_count > 0:
        print(f"\n✅ 段落級測試完成！檢查以下文件:")
        print(f"  - *_segment_real.srt (段落級 SRT 文件)")
        print(f"  - *_segment_real_result.json (完整結果數據)")
    else:
        print(f"\n❌ 所有段落級測試都失敗了")
    
    return results

if __name__ == "__main__":
    main()
