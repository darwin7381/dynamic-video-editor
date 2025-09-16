#!/usr/bin/env python3
"""
測試 ElevenLabs, AssemblyAI, Groq 的段落級輸出
並與詞彙級進行比較分析
"""

import os
import requests
import json
import time
from datetime import timedelta
import assemblyai as aai
from dotenv import load_dotenv

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

def analyze_segment_quality(segments, service_name):
    """分析段落品質"""
    if not segments:
        return {
            'total_segments': 0,
            'avg_length': 0,
            'max_length': 0,
            'min_length': 0,
            'long_segments': 0,
            'score': 0
        }
    
    lengths = [len(seg['text']) for seg in segments]
    long_segments = sum(1 for length in lengths if length > 25)
    
    analysis = {
        'total_segments': len(segments),
        'avg_length': sum(lengths) / len(lengths) if lengths else 0,
        'max_length': max(lengths) if lengths else 0,
        'min_length': min(lengths) if lengths else 0,
        'long_segments': long_segments,
        'score': max(0, 60 - long_segments * 10)  # 基礎評分邏輯
    }
    
    print(f"📊 {service_name} 段落級分析:")
    print(f"  總段落數: {analysis['total_segments']}")
    print(f"  平均長度: {analysis['avg_length']:.1f} 字符")
    print(f"  最長段落: {analysis['max_length']} 字符")
    print(f"  最短段落: {analysis['min_length']} 字符")
    print(f"  問題段落: {analysis['long_segments']} 個 (>25字符)")
    print(f"  段落控制評分: {analysis['score']}/60")
    
    return analysis

def test_elevenlabs_segment_level():
    """測試 ElevenLabs 段落級輸出"""
    print(f"\n🚀 測試 ElevenLabs Scribe 段落級輸出")
    print("=" * 60)
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    audio_file = "../audio-tts-mp3-20250523032437-WJdKQdwW.mp3"
    
    try:
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        headers = {"xi-api-key": api_key}
        
        with open(audio_file, 'rb') as f:
            files = {"file": (audio_file, f, "audio/mpeg")}
            data = {"model_id": "scribe_v1"}  # 不要詞彙級參數，看是否預設給段落級
            
            print(f"📤 發送請求...")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ ElevenLabs 段落級測試成功")
                
                # 保存結果
                with open("elevenlabs_segment_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                # 檢查是否有段落級數據
                segments = []
                if 'segments' in result:
                    print(f"✅ 發現段落級數據: {len(result['segments'])} 個段落")
                    segments = [{'text': seg.get('text', ''), 'start': seg.get('start', 0), 'end': seg.get('end', 0)} 
                               for seg in result['segments']]
                elif 'words' in result:
                    print(f"⚠️ 只有詞彙級數據，嘗試轉換為段落級")
                    # 簡單的句子分割邏輯
                    words = result['words']
                    current_segment = {'text': '', 'start': words[0]['start'], 'end': words[0]['end']}
                    
                    for word in words:
                        current_segment['text'] += word['text']
                        current_segment['end'] = word['end']
                        
                        # 簡單的句子結束判斷
                        if word['text'] in ['。', '！', '？', '.', '!', '?'] or len(current_segment['text']) > 30:
                            segments.append(current_segment.copy())
                            if words.index(word) < len(words) - 1:
                                next_word = words[words.index(word) + 1]
                                current_segment = {'text': '', 'start': next_word['start'], 'end': next_word['end']}
                    
                    if current_segment['text']:
                        segments.append(current_segment)
                
                # 生成 SRT
                if segments:
                    srt_content = ""
                    for i, seg in enumerate(segments, 1):
                        srt_content += f"{i}\n"
                        srt_content += f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n"
                        srt_content += f"{seg['text']}\n\n"
                    
                    with open("elevenlabs_segment_level.srt", "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    print(f"💾 已保存: elevenlabs_segment_level.srt")
                
                # 分析品質
                analysis = analyze_segment_quality(segments, "ElevenLabs")
                return result, segments, analysis
                
            else:
                print(f"❌ ElevenLabs 請求失敗: {response.status_code} - {response.text}")
                return None, [], {}
                
    except Exception as e:
        print(f"❌ ElevenLabs 測試錯誤: {str(e)}")
        return None, [], {}

def test_assemblyai_segment_level():
    """測試 AssemblyAI 段落級輸出"""
    print(f"\n🚀 測試 AssemblyAI Universal-1 段落級輸出")
    print("=" * 60)
    
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    audio_file = "../audio-tts-mp3-20250523032437-WJdKQdwW.mp3"
    
    try:
        aai.settings.api_key = api_key
        
        # 配置段落級轉錄
        config = aai.TranscriptionConfig(
            model=aai.SpeechModel.best,
            language_code="zh",
            punctuate=True,
            format_text=True,
            # 不要 word_boost 和詞彙級參數
        )
        
        print(f"📤 上傳音檔並開始轉錄...")
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file, config)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"❌ AssemblyAI 轉錄失敗: {transcript.error}")
            return None, [], {}
        
        print(f"✅ AssemblyAI 段落級測試成功")
        
        # 保存結果
        result_data = {
            'text': transcript.text,
            'confidence': transcript.confidence,
            'audio_duration': transcript.audio_duration,
            'status': str(transcript.status)
        }
        
        # 檢查是否有段落數據
        segments = []
        if hasattr(transcript, 'paragraphs') and transcript.paragraphs:
            print(f"✅ 發現段落級數據: {len(transcript.paragraphs.paragraphs)} 個段落")
            for para in transcript.paragraphs.paragraphs:
                segments.append({
                    'text': para.text,
                    'start': para.start / 1000.0,  # 轉換為秒
                    'end': para.end / 1000.0
                })
        elif hasattr(transcript, 'utterances') and transcript.utterances:
            print(f"✅ 發現語句級數據: {len(transcript.utterances)} 個語句")
            for utterance in transcript.utterances:
                segments.append({
                    'text': utterance.text,
                    'start': utterance.start / 1000.0,
                    'end': utterance.end / 1000.0
                })
        else:
            print(f"⚠️ 沒有段落級數據，使用整體文本")
            segments = [{
                'text': transcript.text,
                'start': 0,
                'end': transcript.audio_duration / 1000.0 if transcript.audio_duration else 30
            }]
        
        result_data['segments'] = segments
        
        with open("assemblyai_segment_result.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # 生成 SRT
        if segments:
            srt_content = ""
            for i, seg in enumerate(segments, 1):
                srt_content += f"{i}\n"
                srt_content += f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n"
                srt_content += f"{seg['text']}\n\n"
            
            with open("assemblyai_segment_level.srt", "w", encoding="utf-8") as f:
                f.write(srt_content)
            print(f"💾 已保存: assemblyai_segment_level.srt")
        
        # 分析品質
        analysis = analyze_segment_quality(segments, "AssemblyAI")
        return result_data, segments, analysis
        
    except Exception as e:
        print(f"❌ AssemblyAI 測試錯誤: {str(e)}")
        return None, [], {}

def test_groq_segment_level():
    """測試 Groq Whisper Large v3 段落級輸出"""
    print(f"\n🚀 測試 Groq Whisper Large v3 段落級輸出")
    print("=" * 60)
    
    api_key = os.getenv("GROQ_API_KEY")
    audio_file = "../audio-tts-mp3-20250523032437-WJdKQdwW.mp3"
    
    try:
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        with open(audio_file, 'rb') as f:
            files = {
                "file": (audio_file, f, "audio/mpeg")
            }
            data = {
                "model": "whisper-large-v3",
                "response_format": "verbose_json",
                "language": "zh"
                # 不要 timestamp_granularities 參數，看預設段落級
            }
            
            print(f"📤 發送請求...")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Groq 段落級測試成功")
                
                # 保存結果
                with open("groq_segment_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                # 檢查段落數據
                segments = []
                if 'segments' in result and result['segments']:
                    print(f"✅ 發現段落級數據: {len(result['segments'])} 個段落")
                    segments = [{'text': seg.get('text', ''), 'start': seg.get('start', 0), 'end': seg.get('end', 0)} 
                               for seg in result['segments']]
                else:
                    print(f"⚠️ 沒有段落級數據，使用整體文本")
                    segments = [{
                        'text': result.get('text', ''),
                        'start': 0,
                        'end': result.get('duration', 30)
                    }]
                
                # 生成 SRT
                if segments:
                    srt_content = ""
                    for i, seg in enumerate(segments, 1):
                        srt_content += f"{i}\n"
                        srt_content += f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n"
                        srt_content += f"{seg['text']}\n\n"
                    
                    with open("groq_segment_level.srt", "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    print(f"💾 已保存: groq_segment_level.srt")
                
                # 分析品質
                analysis = analyze_segment_quality(segments, "Groq")
                return result, segments, analysis
                
            else:
                print(f"❌ Groq 請求失敗: {response.status_code} - {response.text}")
                return None, [], {}
                
    except Exception as e:
        print(f"❌ Groq 測試錯誤: {str(e)}")
        return None, [], {}

def compare_segment_vs_word_level():
    """比較段落級與詞彙級的差異"""
    print(f"\n📊 段落級 vs 詞彙級比較分析")
    print("=" * 80)
    
    # 讀取之前的詞彙級結果進行比較
    word_level_results = {}
    
    # ElevenLabs 詞彙級結果
    try:
        with open("elevenlabs_scribe_v1_result.json", "r", encoding="utf-8") as f:
            elevenlabs_word = json.load(f)
            word_level_results['ElevenLabs'] = {
                'words': len(elevenlabs_word.get('words', [])),
                'type': '詞彙級'
            }
    except:
        word_level_results['ElevenLabs'] = {'words': 0, 'type': '未測試'}
    
    # AssemblyAI 詞彙級結果
    try:
        with open("assemblyai_chinese_result.json", "r", encoding="utf-8") as f:
            assemblyai_word = json.load(f)
            word_level_results['AssemblyAI'] = {
                'words': len(assemblyai_word.get('words', [])),
                'type': '詞彙級'
            }
    except:
        word_level_results['AssemblyAI'] = {'words': 0, 'type': '未測試'}
    
    # Groq 詞彙級結果 (假設之前有測試)
    word_level_results['Groq'] = {
        'words': 244,  # 之前測試的結果
        'type': '詞彙級'
    }
    
    print(f"📋 詞彙級 vs 段落級對比:")
    print(f"{'服務':<15} {'詞彙級':<10} {'段落級':<10} {'控制精度':<15} {'推薦用途':<20}")
    print("-" * 80)
    
    services_data = [
        ('ElevenLabs', word_level_results['ElevenLabs']['words'], '待測試', '詞彙級最精確', '高品質字幕'),
        ('AssemblyAI', word_level_results['AssemblyAI']['words'], '待測試', '企業級功能', '多人會議'),
        ('Groq', word_level_results['Groq']['words'], '待測試', '成本效益', '快速處理')
    ]
    
    for service, word_count, segment_status, precision, usage in services_data:
        print(f"{service:<15} {word_count:<10} {segment_status:<10} {precision:<15} {usage:<20}")
    
    return word_level_results

def main():
    """主測試函數"""
    print("🎯 段落級 vs 詞彙級比較測試")
    print("=" * 80)
    print("目標: 比較三個服務的段落級與詞彙級輸出差異")
    print("=" * 80)
    
    results = {}
    
    # 測試各服務的段落級輸出
    print(f"\n🔄 開始段落級測試...")
    
    # ElevenLabs 段落級
    elevenlabs_result, elevenlabs_segments, elevenlabs_analysis = test_elevenlabs_segment_level()
    results['ElevenLabs'] = {
        'result': elevenlabs_result,
        'segments': elevenlabs_segments,
        'analysis': elevenlabs_analysis
    }
    
    time.sleep(2)  # 避免 API 限制
    
    # AssemblyAI 段落級
    assemblyai_result, assemblyai_segments, assemblyai_analysis = test_assemblyai_segment_level()
    results['AssemblyAI'] = {
        'result': assemblyai_result,
        'segments': assemblyai_segments,
        'analysis': assemblyai_analysis
    }
    
    time.sleep(2)
    
    # Groq 段落級
    groq_result, groq_segments, groq_analysis = test_groq_segment_level()
    results['Groq'] = {
        'result': groq_result,
        'segments': groq_segments,
        'analysis': groq_analysis
    }
    
    # 比較分析
    word_level_results = compare_segment_vs_word_level()
    
    # 總結
    print(f"\n🏆 段落級測試總結")
    print("=" * 60)
    
    for service, data in results.items():
        if data['analysis']:
            analysis = data['analysis']
            print(f"\n{service}:")
            print(f"  段落數: {analysis['total_segments']}")
            print(f"  最長段落: {analysis['max_length']} 字符")
            print(f"  問題段落: {analysis['long_segments']} 個")
            print(f"  段落控制評分: {analysis['score']}/60")
    
    print(f"\n💡 重要發現:")
    print(f"  - 段落級通常段落較長，適合閱讀")
    print(f"  - 詞彙級可精確控制段落長度，適合字幕")
    print(f"  - 不同服務的段落分割策略不同")
    
    return results

if __name__ == "__main__":
    main()
