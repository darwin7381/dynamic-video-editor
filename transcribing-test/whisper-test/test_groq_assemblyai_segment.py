#!/usr/bin/env python3
"""
使用有效 API 測試 Groq 和 AssemblyAI 的段落級輸出
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

def test_groq_with_valid_key():
    """使用有效的 API Key 測試 Groq"""
    print(f"\n🚀 Groq Whisper Large v3 段落級測試 (有效 API)")
    print("=" * 60)
    
    # 嘗試不同的 Groq API Key
    api_keys = [
        os.getenv("GROQ_API_KEY"),
        os.getenv("GROQ_API_KEY_2"),  # 備用
    ]
    
    audio_file = "../audio-tts-mp3-20250523032437-WJdKQdwW.mp3"
    
    for i, api_key in enumerate(api_keys, 1):
        print(f"\n嘗試 API Key {i}...")
        
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
                }
                
                print(f"📤 發送 Groq 請求...")
                response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Groq API Key {i} 成功！")
                    
                    # 保存結果
                    with open("groq_segment_real_result.json", "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    # 檢查段落數據
                    if 'segments' in result and result['segments']:
                        segments = result['segments']
                        print(f"✅ 發現 {len(segments)} 個段落")
                        
                        # 生成 SRT
                        srt_content = ""
                        for idx, seg in enumerate(segments, 1):
                            text = seg.get('text', '').strip()
                            start = seg.get('start', 0)
                            end = seg.get('end', 0)
                            
                            srt_content += f"{idx}\n"
                            srt_content += f"{format_time(start)} --> {format_time(end)}\n"
                            srt_content += f"{text}\n\n"
                        
                        with open("groq_segment_real.srt", "w", encoding="utf-8") as f:
                            f.write(srt_content)
                        print(f"💾 Groq 段落級 SRT 已保存: groq_segment_real.srt")
                        
                        # 分析
                        lengths = [len(seg.get('text', '').strip()) for seg in segments]
                        print(f"📊 Groq 段落分析:")
                        print(f"  總段落數: {len(segments)}")
                        print(f"  平均長度: {sum(lengths) / len(lengths):.1f} 字符")
                        print(f"  最長段落: {max(lengths)} 字符")
                        print(f"  長段落數: {sum(1 for l in lengths if l > 25)} 個")
                        
                        return result
                    else:
                        print(f"❌ 沒有段落數據")
                        return None
                        
                else:
                    print(f"❌ API Key {i} 失敗: {response.status_code}")
                    if i < len(api_keys):
                        continue
                    else:
                        print(f"所有 Groq API Key 都失敗")
                        return None
                        
        except Exception as e:
            print(f"❌ API Key {i} 錯誤: {str(e)}")
            if i < len(api_keys):
                continue
    
    return None

def test_assemblyai_with_valid_key():
    """使用有效的 API Key 測試 AssemblyAI"""
    print(f"\n🚀 AssemblyAI Universal-1 段落級測試 (有效 API)")
    print("=" * 60)
    
    # 嘗試不同的 AssemblyAI API Key
    api_keys = [
        os.getenv("ASSEMBLYAI_API_KEY"),
        "1234567890abcdef1234567890abcdef",  # 備用
    ]
    
    audio_file = "../audio-tts-mp3-20250523032437-WJdKQdwW.mp3"
    
    for i, api_key in enumerate(api_keys, 1):
        print(f"\n嘗試 API Key {i}...")
        
        try:
            aai.settings.api_key = api_key
            
            config = aai.TranscriptionConfig(
                language_code="zh",
                punctuate=True,
                format_text=True
            )
            
            print(f"📤 上傳音檔並開始轉錄...")
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_file, config)
            
            if transcript.status == aai.TranscriptStatus.error:
                print(f"❌ API Key {i} 轉錄失敗: {transcript.error}")
                if i < len(api_keys):
                    continue
                else:
                    return None
            
            print(f"✅ AssemblyAI API Key {i} 成功！")
            
            # 嘗試獲取段落級數據
            segments = []
            segment_type = "unknown"
            
            # 檢查不同類型的段落數據
            if hasattr(transcript, 'sentences') and transcript.sentences:
                print(f"✅ 發現句子級數據: {len(transcript.sentences)} 個")
                for sentence in transcript.sentences:
                    segments.append({
                        'text': sentence.text,
                        'start': sentence.start / 1000.0,
                        'end': sentence.end / 1000.0
                    })
                segment_type = "sentences"
                
            elif hasattr(transcript, 'paragraphs') and transcript.paragraphs:
                print(f"✅ 發現段落級數據: {len(transcript.paragraphs.paragraphs)} 個")
                for para in transcript.paragraphs.paragraphs:
                    segments.append({
                        'text': para.text,
                        'start': para.start / 1000.0,
                        'end': para.end / 1000.0
                    })
                segment_type = "paragraphs"
                
            else:
                # 手動分割文本為段落
                print(f"⚠️ 沒有自動段落，手動分割文本")
                text = transcript.text
                duration = transcript.audio_duration / 1000.0 if transcript.audio_duration else 30
                
                # 簡單按句號分割
                sentences = text.split('。')
                segment_duration = duration / len(sentences) if sentences else duration
                
                for idx, sentence in enumerate(sentences):
                    if sentence.strip():
                        segments.append({
                            'text': sentence.strip() + ('。' if idx < len(sentences) - 1 else ''),
                            'start': idx * segment_duration,
                            'end': (idx + 1) * segment_duration
                        })
                segment_type = "manual_split"
            
            # 保存結果
            result_data = {
                'text': transcript.text,
                'confidence': transcript.confidence,
                'segments': segments,
                'segment_type': segment_type
            }
            
            with open("assemblyai_segment_real_result.json", "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            # 生成 SRT
            if segments:
                srt_content = ""
                for idx, seg in enumerate(segments, 1):
                    text = seg['text'].strip()
                    start = seg['start']
                    end = seg['end']
                    
                    srt_content += f"{idx}\n"
                    srt_content += f"{format_time(start)} --> {format_time(end)}\n"
                    srt_content += f"{text}\n\n"
                
                with open("assemblyai_segment_real.srt", "w", encoding="utf-8") as f:
                    f.write(srt_content)
                print(f"💾 AssemblyAI 段落級 SRT 已保存: assemblyai_segment_real.srt")
                
                # 分析
                lengths = [len(seg['text'].strip()) for seg in segments]
                print(f"📊 AssemblyAI 段落分析:")
                print(f"  段落類型: {segment_type}")
                print(f"  總段落數: {len(segments)}")
                print(f"  平均長度: {sum(lengths) / len(lengths):.1f} 字符")
                print(f"  最長段落: {max(lengths)} 字符")
                print(f"  長段落數: {sum(1 for l in lengths if l > 25)} 個")
                
                return result_data
            else:
                print(f"❌ 沒有有效段落數據")
                return None
                
        except Exception as e:
            print(f"❌ API Key {i} 錯誤: {str(e)}")
            if i < len(api_keys):
                continue
    
    return None

def create_final_comparison():
    """創建最終的段落級 vs 詞彙級比較"""
    print(f"\n📊 最終段落級 vs 詞彙級比較")
    print("=" * 80)
    
    # 檢查所有生成的文件
    segment_files = [
        ("elevenlabs_segment_real.srt", "ElevenLabs 段落級"),
        ("assemblyai_segment_real.srt", "AssemblyAI 段落級"),
        ("groq_segment_real.srt", "Groq 段落級")
    ]
    
    word_files = [
        ("elevenlabs_precise_18chars.srt", "ElevenLabs 詞彙級"),
        ("assemblyai_precise_18chars.srt", "AssemblyAI 詞彙級"),
        ("final_groq_word_level.srt", "Groq 詞彙級")
    ]
    
    print(f"📋 段落級測試結果:")
    segment_success = 0
    for filepath, name in segment_files:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✅ {name}: {filepath} ({file_size} bytes)")
            segment_success += 1
        else:
            print(f"  ❌ {name}: 測試失敗")
    
    print(f"\n📋 詞彙級對照 (之前成功的):")
    word_success = 0
    for filepath, name in word_files:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✅ {name}: {filepath} ({file_size} bytes)")
            word_success += 1
        else:
            print(f"  ❌ {name}: 不存在")
    
    print(f"\n🏆 測試成功率:")
    print(f"  段落級: {segment_success}/3 ({segment_success/3*100:.1f}%)")
    print(f"  詞彙級: {word_success}/3 ({word_success/3*100:.1f}%)")
    
    if segment_success > 0:
        print(f"\n✅ 段落級測試部分成功！")
        print(f"📁 檢查這些文件來查看段落級結果:")
        for filepath, name in segment_files:
            if os.path.exists(filepath):
                print(f"  - {filepath}")
        
        print(f"\n📁 對應的詞彙級文件:")
        for filepath, name in word_files:
            if os.path.exists(filepath):
                print(f"  - {filepath}")
    
    return segment_success, word_success

def main():
    """主測試函數"""
    print("🎯 使用有效 API 進行段落級測試")
    print("=" * 80)
    
    results = {}
    
    # 測試 Groq
    groq_result = test_groq_with_valid_key()
    results['Groq'] = groq_result
    
    time.sleep(2)
    
    # 測試 AssemblyAI
    assemblyai_result = test_assemblyai_with_valid_key()
    results['AssemblyAI'] = assemblyai_result
    
    # 創建最終比較
    segment_success, word_success = create_final_comparison()
    
    print(f"\n🎉 最終結論:")
    if segment_success >= 2:
        print(f"✅ 段落級測試大部分成功！可以進行有效比較")
    elif segment_success >= 1:
        print(f"⚠️ 段落級測試部分成功，可以進行有限比較")
    else:
        print(f"❌ 段落級測試失敗，無法進行比較")
    
    print(f"\n📁 請檢查生成的文件來查看段落級與詞彙級的差異")
    
    return results

if __name__ == "__main__":
    main()
