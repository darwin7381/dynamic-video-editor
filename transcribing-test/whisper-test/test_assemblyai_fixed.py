#!/usr/bin/env python3
"""
修復後的 AssemblyAI 測試 - 使用正確的 SDK
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

def create_srt_from_words(words):
    """從詞彙級時間戳記創建 SRT"""
    if not words:
        return "無詞彙資訊"
    
    # 按時間分組詞彙為合理的段落
    segments = []
    current_segment = {
        'start': None,
        'end': None,
        'text': ''
    }
    
    for word in words:
        if current_segment['start'] is None:
            current_segment['start'] = word.start / 1000  # 轉換為秒
            current_segment['end'] = word.end / 1000
            current_segment['text'] = word.text
        elif len(current_segment['text'] + ' ' + word.text) > 25:  # 控制段落長度
            # 完成當前段落
            segments.append(current_segment.copy())
            # 開始新段落
            current_segment = {
                'start': word.start / 1000,
                'end': word.end / 1000,
                'text': word.text
            }
        else:
            # 添加到當前段落
            current_segment['text'] += ' ' + word.text
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

def analyze_assemblyai_result(transcript, method_name):
    """分析 AssemblyAI 結果"""
    print(f"\n🎯 {method_name} - 詳細分析")
    print("=" * 60)
    
    # 基本資訊
    print(f"📊 基本資訊:")
    print(f"  轉錄狀態: {transcript.status}")
    print(f"  文字長度: {len(transcript.text)} 字符")
    print(f"  音檔時長: {transcript.audio_duration / 1000:.1f} 秒")
    
    # 檢查功能支援
    print(f"\n🔍 功能支援檢查:")
    
    if hasattr(transcript, 'words') and transcript.words:
        print(f"  ✅ 詞彙級時間戳記: {len(transcript.words)} 個詞彙")
        
        # 創建自定義 SRT
        custom_srt = create_srt_from_words(transcript.words)
        
        with open("assemblyai_word_level.srt", "w", encoding="utf-8") as f:
            f.write(custom_srt)
        print(f"  💾 詞彙級 SRT 已保存: assemblyai_word_level.srt")
        
        # 分析段落品質
        lines = custom_srt.strip().split('\n')
        segments = []
        
        i = 0
        while i < len(lines):
            if lines[i].strip().isdigit():
                if i + 2 < len(lines):
                    text_lines = []
                    i += 2
                    while i < len(lines) and lines[i].strip():
                        text_lines.append(lines[i])
                        i += 1
                    
                    if text_lines:
                        text = ' '.join(text_lines).strip()
                        segments.append(len(text))
            i += 1
        
        if segments:
            print(f"  📊 段落統計: {len(segments)} 個段落")
            print(f"  📏 最長段落: {max(segments)} 字符")
            print(f"  📏 平均長度: {sum(segments)/len(segments):.1f} 字符")
            
            problem_count = sum(1 for length in segments if length > 30)
            print(f"  🚨 問題段落 (>30字符): {problem_count} 個")
    else:
        print(f"  ❌ 無詞彙級時間戳記")
    
    if hasattr(transcript, 'segments') and transcript.segments:
        print(f"  ✅ 段落級時間戳記: {len(transcript.segments)} 個段落")
    else:
        print(f"  ❌ 無段落級時間戳記")
    
    if hasattr(transcript, 'speaker_labels') and transcript.speaker_labels:
        speakers = set(label.speaker for label in transcript.speaker_labels)
        print(f"  ✅ 說話者識別: {len(speakers)} 個說話者")
    else:
        print(f"  ❌ 無說話者識別")
    
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
    
    # 與最佳方案比較
    print(f"\n🏆 與 Groq 最佳方案比較 (95.2分):")
    
    quality_score = 0
    if has_traditional:
        quality_score += 20
    quality_score += min(punctuation_count * 2, 15)
    quality_score += terms_found * 3.75
    
    print(f"  AssemblyAI 轉錄品質: {quality_score:.1f}/50")
    print(f"  Groq 最佳轉錄品質: 45.2/50")
    
    if quality_score > 45:
        print(f"  🎉 AssemblyAI 轉錄品質更好！")
        return True
    elif quality_score > 35:
        print(f"  ✅ AssemblyAI 轉錄品質良好")
        return False
    else:
        print(f"  ⚠️ AssemblyAI 轉錄品質一般")
        return False

def main():
    """使用正確的 AssemblyAI SDK 測試"""
    print("🚀 AssemblyAI Universal-1 正確測試 (使用官方 SDK)")
    print("=" * 80)
    
    # 設定 API Key
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    try:
        print("🔄 開始 AssemblyAI 轉錄...")
        
        # 設定轉錄選項
        config = aai.TranscriptionConfig(
            language_code="zh",           # 中文
            speaker_labels=True,          # 說話者識別
            punctuate=True,              # 標點符號
            format_text=True,            # 格式化文字
            word_boost=["台積電", "聯電", "日月光", "NVIDIA", "ADR", "納斯達克", "費半", "比特幣", "聯準會"],  # 詞彙增強
            boost_param="high"           # 高增強
        )
        
        transcriber = aai.Transcriber(config=config)
        
        # 執行轉錄
        transcript = transcriber.transcribe(audio_file)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"❌ 轉錄失敗: {transcript.error}")
            return
        
        print(f"✅ AssemblyAI 轉錄成功")
        
        # 分析結果
        is_better = analyze_assemblyai_result(transcript, "AssemblyAI Universal-1")
        
        # 保存轉錄結果
        with open("assemblyai_transcript_text.txt", "w", encoding="utf-8") as f:
            f.write(transcript.text)
        print(f"💾 轉錄文字已保存: assemblyai_transcript_text.txt")
        
        # 如果有詞彙級時間戳記，創建自定義 SRT
        if hasattr(transcript, 'words') and transcript.words:
            print(f"\n🎯 創建 AssemblyAI 自定義 SRT...")
            custom_srt = create_srt_from_words(transcript.words)
            
            with open("assemblyai_custom.srt", "w", encoding="utf-8") as f:
                f.write(custom_srt)
            print(f"💾 自定義 SRT 已保存: assemblyai_custom.srt")
            
            # 分析 SRT 段落品質
            lines = custom_srt.strip().split('\n')
            segment_lengths = []
            
            i = 0
            while i < len(lines):
                if lines[i].strip().isdigit():
                    if i + 2 < len(lines):
                        text_lines = []
                        i += 2
                        while i < len(lines) and lines[i].strip():
                            text_lines.append(lines[i])
                            i += 1
                        
                        if text_lines:
                            text = ' '.join(text_lines).strip()
                            segment_lengths.append(len(text))
                i += 1
            
            if segment_lengths:
                print(f"\n📊 AssemblyAI SRT 段落分析:")
                print(f"  總段落數: {len(segment_lengths)}")
                print(f"  最長段落: {max(segment_lengths)} 字符")
                print(f"  平均長度: {sum(segment_lengths)/len(segment_lengths):.1f} 字符")
                
                problem_count = sum(1 for length in segment_lengths if length > 30)
                print(f"  問題段落 (>30字符): {problem_count} 個")
                
                print(f"\n🏆 與 Groq 最佳方案段落控制比較:")
                print(f"  AssemblyAI 最長: {max(segment_lengths)} vs Groq 18 字符")
                print(f"  AssemblyAI 問題段落: {problem_count} vs Groq 0 個")
                
                if max(segment_lengths) <= 18 and problem_count == 0:
                    print(f"  🎉 AssemblyAI 段落控制與 Groq 最佳方案相當或更好！")
                elif max(segment_lengths) <= 25 and problem_count <= 2:
                    print(f"  ✅ AssemblyAI 段落控制良好")
                else:
                    print(f"  ⚠️ AssemblyAI 段落控制不如 Groq 最佳方案")
        
        return {
            'success': True,
            'transcript': transcript,
            'is_better_quality': is_better,
            'max_segment_length': max(segment_lengths) if 'segment_lengths' in locals() and segment_lengths else None
        }
        
    except Exception as e:
        print(f"❌ AssemblyAI 測試失敗: {str(e)}")
        return None

if __name__ == "__main__":
    main()
