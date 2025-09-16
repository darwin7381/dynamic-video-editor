#!/usr/bin/env python3
"""
最終確定性測試 - 找到真正比 Whisper-1 更好的方案
實際查看內容，不用數值評分
"""

import os
from dotenv import load_dotenv
import time
from openai import OpenAI

# 載入環境變數
load_dotenv()

def format_srt_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def create_srt_from_segments(segments):
    """從段落資訊創建 SRT"""
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

def create_custom_srt_from_words(words, max_chars=20, max_duration=2.5):
    """使用詞彙級時間戳記創建短段落 SRT"""
    if not words:
        return "無詞彙資訊"
    
    subtitles = []
    current_subtitle = {
        'start': None,
        'end': None,
        'text': ''
    }
    
    for word_obj in words:
        word = word_obj.word if hasattr(word_obj, 'word') else str(word_obj)
        start_time = word_obj.start if hasattr(word_obj, 'start') else 0
        end_time = word_obj.end if hasattr(word_obj, 'end') else 0
        
        word = word.strip()
        if not word:
            continue
            
        # 檢查是否需要開始新段落
        if (current_subtitle['start'] is None or 
            len(current_subtitle['text'] + word) > max_chars or
            (end_time - current_subtitle['start']) > max_duration):
            
            # 保存當前段落
            if current_subtitle['text']:
                subtitles.append(current_subtitle.copy())
            
            # 開始新段落
            current_subtitle = {
                'start': start_time,
                'end': end_time,
                'text': word
            }
        else:
            # 添加到當前段落
            current_subtitle['text'] += word
            current_subtitle['end'] = end_time
    
    # 添加最後一個段落
    if current_subtitle['text']:
        subtitles.append(current_subtitle)
    
    # 生成 SRT
    srt_content = []
    for i, subtitle in enumerate(subtitles, 1):
        start_time = format_srt_time(subtitle['start'])
        end_time = format_srt_time(subtitle['end'])
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(subtitle['text'])
        srt_content.append("")
    
    return "\n".join(srt_content)

def analyze_srt_manually(srt_content, test_name):
    """手動分析 SRT - 實際查看內容"""
    print(f"\n📺 {test_name} - 實際內容檢查")
    print("=" * 60)
    
    # 解析 SRT
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
    
    print(f"📊 總段落數: {len(segments)}")
    print(f"📏 段落長度範圍: {min(seg['length'] for seg in segments)} - {max(seg['length'] for seg in segments)} 字符")
    
    # 實際顯示所有段落內容
    print(f"\n📋 所有段落內容:")
    
    problem_count = 0
    very_long_count = 0
    
    for seg in segments:
        # 根據用戶的問題：段落過長是問題
        status = ""
        if seg['length'] > 40:
            status = "🚨 嚴重過長 (用戶的主要問題!)"
            very_long_count += 1
            problem_count += 1
        elif seg['length'] > 30:
            status = "⚠️ 過長 (可能有問題)"
            problem_count += 1
        elif seg['length'] >= 15:
            status = "✅ 合理長度"
        else:
            status = "🔸 較短 (不是問題)"
        
        print(f"  {seg['id']:2d}. ({seg['length']:2d}字符) {status}")
        print(f"      {seg['text']}")
        print()
    
    # 實際評估
    print(f"🎯 解決用戶問題的實際效果:")
    print(f"  🚨 嚴重過長段落 (>40字符): {very_long_count} 個")
    print(f"  ⚠️ 總問題段落 (>30字符): {problem_count} 個")
    
    if very_long_count == 0 and problem_count <= 2:
        actual_rating = "🏆 優秀 - 解決了用戶的段落過長問題"
        score = 90
    elif very_long_count == 0 and problem_count <= 5:
        actual_rating = "✅ 良好 - 大幅改善段落過長問題"
        score = 70
    elif very_long_count <= 1:
        actual_rating = "⚠️ 一般 - 部分改善問題"
        score = 50
    else:
        actual_rating = "❌ 不佳 - 未解決問題"
        score = 30
    
    print(f"\n📈 實際解決效果: {actual_rating}")
    
    return {
        'segments': segments,
        'total_segments': len(segments),
        'very_long_count': very_long_count,
        'problem_count': problem_count,
        'actual_rating': actual_rating,
        'score': score,
        'avg_length': sum(seg['length'] for seg in segments) / len(segments),
        'max_length': max(seg['length'] for seg in segments)
    }

def main():
    """最終確定性測試 - 找到真正比 Whisper-1 更好的方案"""
    print("🎯 最終確定性測試 - 找到比 Whisper-1 更好的解決方案")
    print("=" * 80)
    print("用戶問題：Whisper-1 有段落過長問題，需要找到更好的替代方案")
    print("=" * 80)
    
    # API 設定
    openai_api_key = os.getenv("OPENAI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    openai_client = OpenAI(api_key=openai_api_key)
    groq_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    
    results = []
    
    # 最佳 Prompt (基於之前的迭代結果)
    best_prompt = """轉錄財經新聞。字幕要求：
- 每段最多 20 字符
- 不要把多個句子合併在一段
- 在逗號、句號處自然分段
- 保持語義完整但優先控制長度"""
    
    # 1. Whisper-1 基準 (用戶現在使用的)
    print(f"\n📊 測試 1: Whisper-1 基準 (用戶目前的方案)")
    try:
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="srt",
                language="zh"
            )
        
        with open("final_whisper1_baseline.srt", "w", encoding="utf-8") as f:
            f.write(transcription)
        
        analysis = analyze_srt_manually(transcription, "Whisper-1 基準")
        results.append(('Whisper-1 基準', analysis))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 2. Whisper-1 + 最佳 Prompt
    print(f"\n📊 測試 2: Whisper-1 + 最佳 Prompt")
    try:
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="srt",
                prompt=best_prompt,
                language="zh"
            )
        
        with open("final_whisper1_best_prompt.srt", "w", encoding="utf-8") as f:
            f.write(transcription)
        
        analysis = analyze_srt_manually(transcription, "Whisper-1 + 最佳Prompt")
        results.append(('Whisper-1 + 最佳Prompt', analysis))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 3. Whisper-1 詞彙級自定義 (最精確控制)
    print(f"\n📊 測試 3: Whisper-1 詞彙級自定義控制")
    try:
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"],
                language="zh"
            )
        
        print(f"📝 獲得 {len(transcription.words)} 個詞彙的時間戳記")
        
        # 創建短段落 SRT
        custom_srt = create_custom_srt_from_words(transcription.words, max_chars=20, max_duration=2.5)
        
        with open("final_whisper1_word_level.srt", "w", encoding="utf-8") as f:
            f.write(custom_srt)
        
        analysis = analyze_srt_manually(custom_srt, "Whisper-1 詞彙級自定義")
        results.append(('Whisper-1 詞彙級自定義', analysis))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 4. Groq Whisper Large v3 基準
    print(f"\n📊 測試 4: Groq Whisper Large v3 基準")
    try:
        with open(audio_file, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                response_format="verbose_json",
                language="zh"
            )
        
        srt_content = create_srt_from_segments(transcription.segments)
        
        with open("final_groq_baseline.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        analysis = analyze_srt_manually(srt_content, "Groq Large v3 基準")
        results.append(('Groq Large v3 基準', analysis))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 5. Groq Whisper Large v3 + 最佳 Prompt
    print(f"\n📊 測試 5: Groq Whisper Large v3 + 最佳 Prompt")
    try:
        with open(audio_file, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                response_format="verbose_json",
                prompt=best_prompt,
                language="zh"
            )
        
        srt_content = create_srt_from_segments(transcription.segments)
        
        with open("final_groq_best_prompt.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        analysis = analyze_srt_manually(srt_content, "Groq Large v3 + 最佳Prompt")
        results.append(('Groq Large v3 + 最佳Prompt', analysis))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 最終比較 - 實際效果
    print(f"\n" + "=" * 80)
    print(f"🏆 最終結果：哪個方案真正比 Whisper-1 更好？")
    print("=" * 80)
    
    if results:
        # 找到 Whisper-1 基準
        whisper1_baseline = None
        for name, analysis in results:
            if name == 'Whisper-1 基準':
                whisper1_baseline = analysis
                break
        
        if whisper1_baseline:
            print(f"📊 Whisper-1 基準表現:")
            print(f"  嚴重過長段落: {whisper1_baseline['very_long_count']} 個")
            print(f"  問題段落總數: {whisper1_baseline['problem_count']} 個")
            print(f"  最長段落: {whisper1_baseline['max_length']} 字符")
            print(f"  實際評級: {whisper1_baseline['actual_rating']}")
            
            print(f"\n🚀 其他方案 vs Whisper-1 比較:")
            
            better_solutions = []
            
            for name, analysis in results:
                if name != 'Whisper-1 基準':
                    print(f"\n  {name}:")
                    print(f"    嚴重過長段落: {analysis['very_long_count']} vs {whisper1_baseline['very_long_count']} (基準)")
                    print(f"    問題段落總數: {analysis['problem_count']} vs {whisper1_baseline['problem_count']} (基準)")
                    print(f"    最長段落: {analysis['max_length']} vs {whisper1_baseline['max_length']} (基準)")
                    print(f"    實際評級: {analysis['actual_rating']}")
                    
                    # 判斷是否真的更好
                    is_better = False
                    improvement_reasons = []
                    
                    if analysis['very_long_count'] < whisper1_baseline['very_long_count']:
                        is_better = True
                        improvement_reasons.append("減少嚴重過長段落")
                    
                    if analysis['problem_count'] < whisper1_baseline['problem_count']:
                        is_better = True
                        improvement_reasons.append("減少問題段落")
                    
                    if analysis['max_length'] < whisper1_baseline['max_length']:
                        is_better = True
                        improvement_reasons.append("控制最長段落")
                    
                    if is_better:
                        print(f"    🎉 比 Whisper-1 更好！原因: {', '.join(improvement_reasons)}")
                        better_solutions.append((name, analysis, improvement_reasons))
                    else:
                        print(f"    ❌ 不如 Whisper-1")
            
            # 總結真正更好的方案
            if better_solutions:
                print(f"\n🏅 找到 {len(better_solutions)} 個比 Whisper-1 更好的方案:")
                
                # 按實際效果排序
                better_solutions.sort(key=lambda x: (x[1]['very_long_count'], x[1]['problem_count']))
                
                for i, (name, analysis, reasons) in enumerate(better_solutions, 1):
                    print(f"\n  {i}. {name}")
                    print(f"     改善原因: {', '.join(reasons)}")
                    print(f"     嚴重過長段落: {analysis['very_long_count']} 個")
                    print(f"     問題段落總數: {analysis['problem_count']} 個")
                    print(f"     {analysis['actual_rating']}")
                
                # 最佳推薦
                best_solution = better_solutions[0]
                print(f"\n🏆 最佳解決方案: {best_solution[0]}")
                print(f"   {best_solution[1]['actual_rating']}")
                print(f"   改善效果: {', '.join(best_solution[2])}")
                
            else:
                print(f"\n😞 沒有找到比 Whisper-1 基準更好的方案")
                print(f"   所有測試方案的表現都不如 Whisper-1 基準")
                print(f"   建議繼續使用 Whisper-1 基準版本")
    
    print(f"\n🎉 最終確定性測試完成！")
    return results

if __name__ == "__main__":
    main()
