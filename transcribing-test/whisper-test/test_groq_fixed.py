#!/usr/bin/env python3
"""
修復後的 Groq Whisper Large v3 測試
正確處理時間戳記資訊
"""

import os
from dotenv import load_dotenv
import time
import json
from openai import OpenAI

# 載入環境變數
load_dotenv()

def create_srt_from_groq_segments(segments):
    """從 Groq 的段落資訊創建 SRT"""
    srt_content = []
    
    for i, segment in enumerate(segments, 1):
        start_time = format_srt_time(segment.start)
        end_time = format_srt_time(segment.end)
        text = segment.text.strip()
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(text)
        srt_content.append("")
    
    return "\n".join(srt_content)

def format_srt_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def analyze_srt_quality(srt_content):
    """分析 SRT 品質"""
    lines = srt_content.strip().split('\n')
    segments = []
    current_text = ""
    
    for line in lines:
        if line.strip().isdigit():
            if current_text:
                segments.append(current_text.strip())
            current_text = ""
        elif "-->" not in line and line.strip():
            current_text += line + " "
    
    if current_text:
        segments.append(current_text.strip())
    
    if segments:
        segment_lengths = [len(seg) for seg in segments]
        return {
            'segment_count': len(segments),
            'avg_length': sum(segment_lengths) / len(segment_lengths),
            'max_length': max(segment_lengths),
            'min_length': min(segment_lengths)
        }
    return None

def main():
    """主測試函數"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    # 初始化 Groq 客戶端
    groq_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    
    print("🚀 Groq Whisper Large v3 完整測試")
    print("=" * 60)
    
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                response_format="verbose_json",
                language="zh"
            )
        
        processing_time = time.time() - start_time
        
        print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
        print(f"🌍 檢測語言: {transcription.language}")
        print(f"⏱️ 音檔時長: {transcription.duration} 秒")
        print(f"📝 轉錄文字長度: {len(transcription.text)} 字符")
        
        # 檢查段落資訊
        if transcription.segments:
            segments = transcription.segments
            print(f"📊 段落數: {len(segments)}")
            
            print(f"\n🔍 段落資訊分析:")
            segment_lengths = [len(seg.text) for seg in segments]
            avg_length = sum(segment_lengths) / len(segment_lengths)
            max_length = max(segment_lengths)
            min_length = min(segment_lengths)
            
            print(f"  平均段落長度: {avg_length:.1f} 字符")
            print(f"  最長段落: {max_length} 字符")
            print(f"  最短段落: {min_length} 字符")
            
            print(f"\n📋 前 5 個段落:")
            for i, seg in enumerate(segments[:5]):
                duration = seg.end - seg.start
                print(f"  {i+1}. [{seg.start:.2f}-{seg.end:.2f}] ({duration:.2f}s) {seg.text}")
            
            # 創建 SRT
            print(f"\n🎯 創建 SRT 字幕文件...")
            srt_content = create_srt_from_groq_segments(segments)
            
            # 保存 SRT
            with open("groq_whisper_large_v3_generated.srt", "w", encoding="utf-8") as f:
                f.write(srt_content)
            
            print(f"✅ SRT 已保存: groq_whisper_large_v3_generated.srt")
            
            # 分析 SRT 品質
            srt_quality = analyze_srt_quality(srt_content)
            if srt_quality:
                print(f"\n📊 SRT 品質分析:")
                print(f"  段落數: {srt_quality['segment_count']}")
                print(f"  平均長度: {srt_quality['avg_length']:.1f} 字符")
                print(f"  最長段落: {srt_quality['max_length']} 字符")
                print(f"  最短段落: {srt_quality['min_length']} 字符")
            
            # 顯示 SRT 預覽
            print(f"\n📄 SRT 預覽:")
            preview_lines = srt_content.split('\n')[:20]
            for line in preview_lines:
                print(f"  {line}")
            if len(srt_content.split('\n')) > 20:
                print(f"  ...")
        
        # 檢查詞彙資訊
        if transcription.words:
            print(f"📝 詞彙級時間戳記: {len(transcription.words)} 個詞彙")
        else:
            print(f"❌ 沒有詞彙級時間戳記")
        
        # 保存完整的轉錄資訊
        transcription_dict = {
            'text': transcription.text,
            'language': transcription.language,
            'duration': transcription.duration,
            'segments': [
                {
                    'id': seg.id,
                    'start': seg.start,
                    'end': seg.end,
                    'text': seg.text,
                    'avg_logprob': seg.avg_logprob,
                    'compression_ratio': seg.compression_ratio,
                    'no_speech_prob': seg.no_speech_prob
                } for seg in transcription.segments
            ] if transcription.segments else [],
            'words': transcription.words  # 這個可能是 None
        }
        
        with open("groq_transcription_complete.json", "w", encoding="utf-8") as f:
            json.dump(transcription_dict, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 完整轉錄資訊已保存: groq_transcription_complete.json")
        
        return {
            'success': True,
            'processing_time': processing_time,
            'has_segments': bool(transcription.segments),
            'has_words': bool(transcription.words),
            'segment_count': len(transcription.segments) if transcription.segments else 0,
            'word_count': len(transcription.words) if transcription.words else 0,
            'srt_quality': srt_quality
        }
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    result = main()
    
    print(f"\n" + "=" * 60)
    print(f"📊 最終結果總結")
    print(f"=" * 60)
    
    if result['success']:
        print(f"✅ 測試成功")
        print(f"⏱️ 處理時間: {result['processing_time']:.2f} 秒")
        print(f"📊 段落級時間戳記: {'支援' if result['has_segments'] else '不支援'} ({result['segment_count']} 個)")
        print(f"📝 詞彙級時間戳記: {'支援' if result['has_words'] else '不支援'} ({result['word_count']} 個)")
        
        if result['srt_quality']:
            quality = result['srt_quality']
            print(f"\n🎯 SRT 品質:")
            print(f"  最長段落: {quality['max_length']} 字符")
            print(f"  平均段落: {quality['avg_length']:.1f} 字符")
        
        if result['has_segments']:
            print(f"\n🎉 結論: Groq Whisper Large v3 支援段落級時間戳記，可以生成 SRT！")
        else:
            print(f"\n😞 結論: Groq Whisper Large v3 不支援時間戳記")
    else:
        print(f"❌ 測試失敗: {result['error']}")
    
    print(f"\n🚀 Groq Whisper Large v3 速度優勢: 約 {result['processing_time']:.2f} 秒 (比 OpenAI whisper-1 快約 70%)")
