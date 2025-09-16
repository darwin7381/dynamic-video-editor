#!/usr/bin/env python3
"""
修正版段落級測試 - 使用正確的 API 參數
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

def test_assemblyai_segment_fixed():
    """修正版 AssemblyAI 段落級測試"""
    print(f"\n🚀 測試 AssemblyAI Universal-1 段落級輸出 (修正版)")
    print("=" * 60)
    
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    audio_file = "../audio-tts-mp3-20250523032437-WJdKQdwW.mp3"
    
    try:
        aai.settings.api_key = api_key
        
        # 使用基本配置，不指定特定模型
        config = aai.TranscriptionConfig(
            language_code="zh",
            punctuate=True,
            format_text=True
        )
        
        print(f"📤 上傳音檔並開始轉錄...")
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file, config)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"❌ AssemblyAI 轉錄失敗: {transcript.error}")
            return None, [], {}
        
        print(f"✅ AssemblyAI 段落級測試成功")
        
        # 使用 sentences 作為段落級數據
        segments = []
        if hasattr(transcript, 'sentences') and transcript.sentences:
            print(f"✅ 發現句子級數據: {len(transcript.sentences)} 個句子")
            for sentence in transcript.sentences:
                segments.append({
                    'text': sentence.text,
                    'start': sentence.start / 1000.0,  # 轉換為秒
                    'end': sentence.end / 1000.0
                })
        else:
            print(f"⚠️ 沒有句子級數據，使用整體文本")
            segments = [{
                'text': transcript.text,
                'start': 0,
                'end': transcript.audio_duration / 1000.0 if transcript.audio_duration else 30
            }]
        
        # 保存結果
        result_data = {
            'text': transcript.text,
            'confidence': transcript.confidence,
            'audio_duration': transcript.audio_duration,
            'segments': segments,
            'status': str(transcript.status)
        }
        
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

def test_groq_segment_fixed():
    """修正版 Groq 段落級測試"""
    print(f"\n🚀 測試 Groq Whisper Large v3 段落級輸出 (修正版)")
    print("=" * 60)
    
    # 使用正確的 Groq API Key
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
                # 預設應該給段落級的 segments
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
                # 嘗試使用之前的結果文件
                try:
                    with open("groq_whisper_large_v3_result.json", "r", encoding="utf-8") as f:
                        result = json.load(f)
                        print(f"🔄 使用之前的 Groq 結果進行段落分析")
                        
                        segments = []
                        if 'segments' in result:
                            segments = [{'text': seg.get('text', ''), 'start': seg.get('start', 0), 'end': seg.get('end', 0)} 
                                       for seg in result['segments']]
                        
                        analysis = analyze_segment_quality(segments, "Groq (快取)")
                        return result, segments, analysis
                except:
                    return None, [], {}
                
    except Exception as e:
        print(f"❌ Groq 測試錯誤: {str(e)}")
        return None, [], {}

def compare_detailed_results():
    """詳細比較段落級與詞彙級結果"""
    print(f"\n📊 詳細比較分析")
    print("=" * 80)
    
    # 讀取 ElevenLabs 段落級結果
    try:
        with open("elevenlabs_segment_level.srt", "r", encoding="utf-8") as f:
            elevenlabs_segment_content = f.read()
        print(f"✅ ElevenLabs 段落級 SRT 已讀取")
    except:
        elevenlabs_segment_content = ""
    
    # 讀取 ElevenLabs 詞彙級結果 (之前的最佳版本)
    try:
        with open("elevenlabs_precise_18chars.srt", "r", encoding="utf-8") as f:
            elevenlabs_word_content = f.read()
        print(f"✅ ElevenLabs 詞彙級 SRT 已讀取")
    except:
        elevenlabs_word_content = ""
    
    print(f"\n📋 ElevenLabs 對比:")
    segment_count = elevenlabs_segment_content.count('\n\n') if elevenlabs_segment_content else 0
    word_count = elevenlabs_word_content.count('\n\n') if elevenlabs_word_content else 0
    print(f"  段落級段落數: {segment_count}")
    print(f"  詞彙級段落數: {word_count}")
    
    # 顯示前3個段落的對比
    if elevenlabs_segment_content and elevenlabs_word_content:
        print(f"\n📝 前3個段落對比:")
        
        segment_blocks = elevenlabs_segment_content.split('\n\n')[:3]
        word_blocks = elevenlabs_word_content.split('\n\n')[:3]
        
        for i, (seg_block, word_block) in enumerate(zip(segment_blocks, word_blocks), 1):
            if len(seg_block.split('\n')) >= 3 and len(word_block.split('\n')) >= 3:
                seg_text = seg_block.split('\n')[2]
                word_text = word_block.split('\n')[2]
                
                print(f"\n  段落 {i}:")
                print(f"    段落級: {seg_text} ({len(seg_text)} 字符)")
                print(f"    詞彙級: {word_text} ({len(word_text)} 字符)")

def main():
    """主測試函數"""
    print("🎯 段落級測試 (修正版)")
    print("=" * 80)
    
    results = {}
    
    # 測試 AssemblyAI 段落級
    assemblyai_result, assemblyai_segments, assemblyai_analysis = test_assemblyai_segment_fixed()
    results['AssemblyAI'] = {
        'result': assemblyai_result,
        'segments': assemblyai_segments,
        'analysis': assemblyai_analysis
    }
    
    time.sleep(2)
    
    # 測試 Groq 段落級
    groq_result, groq_segments, groq_analysis = test_groq_segment_fixed()
    results['Groq'] = {
        'result': groq_result,
        'segments': groq_segments,
        'analysis': groq_analysis
    }
    
    # 詳細比較
    compare_detailed_results()
    
    # 總結比較
    print(f"\n🏆 段落級 vs 詞彙級總結")
    print("=" * 60)
    
    comparison_table = [
        ["服務", "段落級評分", "詞彙級評分", "推薦使用"],
        ["ElevenLabs", "0/60 (長段落)", "100/100 (完美)", "詞彙級"],
        ["AssemblyAI", f"{assemblyai_analysis.get('score', 0)}/60", "82/100", "看需求"],
        ["Groq", f"{groq_analysis.get('score', 0)}/60", "95/100", "詞彙級"]
    ]
    
    for row in comparison_table:
        print(f"{row[0]:<12} {row[1]:<15} {row[2]:<15} {row[3]:<10}")
    
    print(f"\n💡 重要結論:")
    print(f"  ✅ 詞彙級控制明顯優於段落級")
    print(f"  ✅ ElevenLabs 詞彙級仍是最佳選擇")
    print(f"  ✅ 段落級適合閱讀，詞彙級適合字幕")
    
    return results

if __name__ == "__main__":
    main()
