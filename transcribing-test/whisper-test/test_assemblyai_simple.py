#!/usr/bin/env python3
"""
簡化的 AssemblyAI 測試 - 去除不支援的中文功能
"""

import os
from dotenv import load_dotenv
import assemblyai as aai

# 載入環境變數
load_dotenv()

def format_srt_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def create_srt_from_words(words, max_chars=20):
    """從詞彙級時間戳記創建 SRT"""
    if not words:
        return "無詞彙資訊"
    
    segments = []
    current_segment = {
        'start': None,
        'end': None,
        'text': ''
    }
    
    for word in words:
        word_text = word.text.strip()
        if not word_text:
            continue
            
        if current_segment['start'] is None:
            current_segment['start'] = word.start / 1000
            current_segment['end'] = word.end / 1000
            current_segment['text'] = word_text
        elif len(current_segment['text'] + ' ' + word_text) > max_chars:
            # 完成當前段落
            segments.append(current_segment.copy())
            # 開始新段落
            current_segment = {
                'start': word.start / 1000,
                'end': word.end / 1000,
                'text': word_text
            }
        else:
            # 添加到當前段落
            current_segment['text'] += ' ' + word_text
            current_segment['end'] = word.end / 1000
    
    # 添加最後一個段落
    if current_segment['text']:
        segments.append(current_segment)
    
    # 生成 SRT
    srt_content = []
    for i, segment in enumerate(segments, 1):
        start_time = format_srt_time(segment['start'])
        end_time = format_srt_time(segment['end'])
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(segment['text'])
        srt_content.append("")
    
    return "\n".join(srt_content)

def display_srt_content(srt_content, service_name):
    """顯示 SRT 實際內容"""
    print(f"\n📺 {service_name} SRT 實際內容")
    print("=" * 60)
    
    lines = srt_content.strip().split('\n')
    segments = []
    
    i = 0
    while i < len(lines):
        if lines[i].strip().isdigit():
            if i + 2 < len(lines):
                segment_id = int(lines[i])
                time_line = lines[i + 1]
                text_lines = []
                i += 2
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i])
                    i += 1
                
                if text_lines:
                    text = ' '.join(text_lines).strip()
                    segments.append({
                        'id': segment_id,
                        'time': time_line,
                        'text': text,
                        'length': len(text)
                    })
        i += 1
    
    if not segments:
        print("❌ 無法解析 SRT")
        return None
    
    lengths = [seg['length'] for seg in segments]
    problem_segments = [seg for seg in segments if seg['length'] > 30]
    
    print(f"📊 段落統計:")
    print(f"  總段落數: {len(segments)}")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  平均長度: {sum(lengths)/len(lengths):.1f} 字符")
    print(f"  問題段落 (>30字符): {len(problem_segments)} 個")
    
    print(f"\n📋 前10個段落實際內容:")
    for seg in segments[:10]:
        status = "🚨" if seg['length'] > 40 else "⚠️" if seg['length'] > 30 else "✅" if 15 <= seg['length'] <= 25 else "🔸"
        print(f"  {seg['id']:2d}. ({seg['length']:2d}字符) {status} {seg['text']}")
    
    # 與最佳方案比較
    print(f"\n🏆 與 Groq 最佳方案比較:")
    print(f"  {service_name} 最長段落: {max(lengths)} vs Groq 18 字符")
    print(f"  {service_name} 問題段落: {len(problem_segments)} vs Groq 0 個")
    
    if max(lengths) <= 18 and len(problem_segments) == 0:
        print(f"  🎉 {service_name} 段落控制與 Groq 最佳方案相當或更好！")
        return True
    elif max(lengths) <= 25 and len(problem_segments) <= 2:
        print(f"  ✅ {service_name} 段落控制良好")
        return False
    else:
        print(f"  ❌ {service_name} 段落控制不如 Groq 最佳方案")
        return False

def main():
    """簡化的 AssemblyAI 測試"""
    print("🚀 AssemblyAI Universal-1 簡化測試")
    print("=" * 80)
    
    # 設定 API Key
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    try:
        print("🔄 開始 AssemblyAI 轉錄 (基本設定)...")
        
        # 基本設定 (避免中文不支援的功能)
        config = aai.TranscriptionConfig(
            language_code="zh",     # 中文
            speaker_labels=True,    # 說話者識別
            punctuate=True,        # 標點符號
            format_text=True       # 格式化文字
        )
        
        transcriber = aai.Transcriber(config=config)
        
        # 執行轉錄
        transcript = transcriber.transcribe(audio_file)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"❌ 轉錄失敗: {transcript.error}")
            return
        
        print(f"✅ AssemblyAI 轉錄成功")
        
        # 分析結果
        print(f"\n🎯 AssemblyAI Universal-1 - 詳細分析")
        print("=" * 60)
        
        # 基本資訊
        print(f"📊 基本資訊:")
        print(f"  轉錄狀態: {transcript.status}")
        print(f"  文字長度: {len(transcript.text)} 字符")
        
        # 檢查功能支援
        print(f"\n🔍 功能支援檢查:")
        
        if hasattr(transcript, 'words') and transcript.words:
            print(f"  ✅ 詞彙級時間戳記: {len(transcript.words)} 個詞彙")
        else:
            print(f"  ❌ 無詞彙級時間戳記")
        
        if hasattr(transcript, 'segments') and transcript.segments:
            print(f"  ✅ 段落級時間戳記: {len(transcript.segments)} 個段落")
        else:
            print(f"  ❌ 無段落級時間戳記")
        
        # 轉錄品質檢查
        print(f"\n📝 轉錄品質:")
        text = transcript.text
        
        # 檢查語言
        has_traditional = any(char in text for char in ['台積電', '聯電', '連準會', '納斯達克'])
        print(f"  語言: {'繁體中文 ✅' if has_traditional else '簡體中文 ❌'}")
        
        # 檢查標點符號
        punctuation_count = text.count('，') + text.count('。') + text.count('！') + text.count('？')
        print(f"  標點符號: {punctuation_count} 個")
        
        # 檢查專業術語
        terms_found = 0
        if '台積電' in text:
            terms_found += 1
            print(f"  ✅ 台積電 識別正確")
        if 'NVIDIA' in text or '輝達' in text:
            terms_found += 1
            print(f"  ✅ NVIDIA/輝達 識別正確")
        if '納斯達克' in text:
            terms_found += 1
            print(f"  ✅ 納斯達克 識別正確")
        if '比特幣' in text:
            terms_found += 1
            print(f"  ✅ 比特幣 識別正確")
        
        print(f"  專業術語識別: {terms_found}/4 個")
        
        # 顯示轉錄內容
        print(f"\n📋 轉錄內容:")
        print(f"  {text}")
        
        # 計算品質評分
        quality_score = 0
        if has_traditional:
            quality_score += 20
        quality_score += min(punctuation_count * 2, 15)
        quality_score += terms_found * 3.75
        
        print(f"\n🏆 與 Groq 最佳方案比較 (95.2分):")
        print(f"  AssemblyAI 轉錄品質: {quality_score:.1f}/50")
        print(f"  Groq 最佳轉錄品質: 45.2/50")
        
        quality_better = quality_score > 45
        
        # 如果有詞彙級時間戳記，測試段落控制
        if hasattr(transcript, 'words') and transcript.words:
            print(f"\n🎯 測試 AssemblyAI 段落控制能力...")
            
            # 測試不同的段落長度設定
            for max_chars in [18, 20, 25]:
                print(f"\n📊 測試目標長度: {max_chars} 字符")
                
                custom_srt = create_srt_from_words(transcript.words, max_chars)
                
                filename = f"assemblyai_custom_{max_chars}chars.srt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(custom_srt)
                print(f"💾 已保存: {filename}")
                
                # 分析這個版本的段落品質
                segment_better = display_srt_content(custom_srt, f"AssemblyAI ({max_chars}字符)")
                
                if segment_better:
                    print(f"  🎉 AssemblyAI {max_chars}字符版本段落控制優秀！")
                    break
        
        # 最終評估
        print(f"\n🏆 AssemblyAI 最終評估:")
        if quality_better:
            print(f"  轉錄品質: 🎉 優於 Groq 最佳方案")
        else:
            print(f"  轉錄品質: ✅ 良好但不如 Groq 最佳方案")
        
        print(f"  多人辨識: ✅ 支援")
        print(f"  詞彙級時間戳記: {'✅ 支援' if hasattr(transcript, 'words') and transcript.words else '❌ 不支援'}")
        
        return transcript
        
    except Exception as e:
        print(f"❌ AssemblyAI 測試失敗: {str(e)}")
        return None

if __name__ == "__main__":
    main()
