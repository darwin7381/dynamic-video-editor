#!/usr/bin/env python3
"""
正確的全面測試 - 解決用戶的 SRT 段落過長問題
重新測試所有方案，包含詞彙級時間戳記
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

def create_custom_srt_from_words(words, max_chars=25, max_duration=3.0):
    """使用詞彙級時間戳記創建自定義 SRT - 解決段落過長問題"""
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

def analyze_srt_for_long_segments(srt_content, model_name):
    """分析 SRT 的段落過長問題 - 根據用戶的實際需求"""
    print(f"\n📺 {model_name} - 段落過長問題分析")
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
    
    if not segments:
        print("❌ 無法解析 SRT")
        return None
    
    lengths = [seg['length'] for seg in segments]
    
    print(f"📊 段落統計:")
    print(f"  總段落數: {len(segments)}")
    print(f"  平均長度: {sum(lengths)/len(lengths):.1f} 字符")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  最短段落: {min(lengths)} 字符")
    
    # 根據用戶的問題：段落過長是問題！
    very_long = [l for l in lengths if l > 40]  # 嚴重過長 - 主要問題
    long = [l for l in lengths if l > 30]  # 過長 - 次要問題  
    good = [l for l in lengths if 15 <= l <= 30]  # 理想長度
    short = [l for l in lengths if l < 15]  # 過短但不是主要問題
    
    print(f"\n🎯 段落過長問題評估:")
    print(f"  🚨 嚴重過長 (>40字符): {len(very_long)} 個 ({len(very_long)/len(segments)*100:.1f}%)")
    print(f"  ⚠️ 過長 (>30字符): {len(long)} 個 ({len(long)/len(segments)*100:.1f}%)")
    print(f"  ✅ 理想長度 (15-30字符): {len(good)} 個 ({len(good)/len(segments)*100:.1f}%)")
    print(f"  🔸 過短 (<15字符): {len(short)} 個 ({len(short)/len(segments)*100:.1f}%)")
    
    # 顯示問題段落
    problem_segments = [seg for seg in segments if seg['length'] > 30]
    if problem_segments:
        print(f"\n🚨 發現的過長段落 (您的主要問題):")
        for seg in problem_segments[:5]:  # 只顯示前5個
            print(f"  段落 {seg['id']}: {seg['length']} 字符")
            print(f"    時間: {seg['time']}")
            print(f"    內容: {seg['text']}")
            print()
        if len(problem_segments) > 5:
            print(f"  ... 還有 {len(problem_segments) - 5} 個過長段落")
    else:
        print(f"\n✅ 沒有發現過長段落問題！")
    
    # 計算解決問題的效果 (專注於解決過長問題)
    problem_solving_score = 0
    
    # 主要指標：沒有嚴重過長段落 (50%)
    if len(very_long) == 0:
        problem_solving_score += 50
    elif len(very_long) <= 1:
        problem_solving_score += 30
    elif len(very_long) <= 3:
        problem_solving_score += 10
    
    # 次要指標：控制一般過長段落 (30%)
    if len(long) == 0:
        problem_solving_score += 30
    elif len(long) <= 2:
        problem_solving_score += 20
    elif len(long) <= 5:
        problem_solving_score += 10
    
    # 理想段落比例 (20%)
    problem_solving_score += (len(good) / len(segments)) * 20
    
    print(f"\n📈 解決段落過長問題效果: {problem_solving_score:.1f}/100")
    
    if problem_solving_score >= 80:
        rating = "🏆 優秀 - 完美解決過長問題"
    elif problem_solving_score >= 60:
        rating = "✅ 良好 - 大幅改善過長問題"
    elif problem_solving_score >= 40:
        rating = "⚠️ 一般 - 部分改善過長問題"
    else:
        rating = "❌ 不佳 - 未解決過長問題"
    
    print(f"🎯 問題解決評級: {rating}")
    
    return {
        'total_segments': len(segments),
        'avg_length': sum(lengths)/len(lengths),
        'max_length': max(lengths),
        'very_long_count': len(very_long),
        'long_count': len(long),
        'good_count': len(good),
        'short_count': len(short),
        'problem_solving_score': problem_solving_score,
        'rating': rating,
        'problem_segments': problem_segments
    }

def main():
    """正確的全面測試"""
    print("🎯 正確測試：解決 SRT 段落過長問題")
    print("=" * 80)
    print("根據用戶需求：段落過長是問題，需要找到更短、更合理的分段方案")
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
    
    # 專業 Prompt - 針對段落過長問題
    anti_long_segment_prompt = """財經新聞轉錄。重要要求：
1. 避免段落過長 - 每段最多 25 個字符
2. 在自然停頓處分段，不要把多句話合併在一個段落
3. 保持語義完整，但優先考慮段落長度控制
4. 正確識別：台積電、NVIDIA、ADR、那斯達克、比特幣
5. 使用繁體中文和適當標點符號"""
    
    # 1. OpenAI Whisper-1 基準 (SRT)
    print(f"\n📊 測試 1: OpenAI Whisper-1 基準 SRT")
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="srt",
                language="zh"
            )
        
        processing_time = time.time() - start_time
        print(f"✅ 處理完成 (時間: {processing_time:.2f}秒)")
        
        with open("test1_whisper1_baseline.srt", "w", encoding="utf-8") as f:
            f.write(transcription)
        
        analysis = analyze_srt_for_long_segments(transcription, "Whisper-1 基準")
        results.append(('Whisper-1 基準', analysis, transcription))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 2. OpenAI Whisper-1 + 專業 Prompt (SRT)
    print(f"\n📊 測試 2: OpenAI Whisper-1 + 專業 Prompt SRT")
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="srt",
                prompt=anti_long_segment_prompt,
                language="zh"
            )
        
        processing_time = time.time() - start_time
        print(f"✅ 處理完成 (時間: {processing_time:.2f}秒)")
        
        with open("test2_whisper1_prompt.srt", "w", encoding="utf-8") as f:
            f.write(transcription)
        
        analysis = analyze_srt_for_long_segments(transcription, "Whisper-1 + 專業Prompt")
        results.append(('Whisper-1 + 專業Prompt', analysis, transcription))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 3. OpenAI Whisper-1 詞彙級自定義 SRT
    print(f"\n📊 測試 3: OpenAI Whisper-1 詞彙級自定義 SRT")
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"],
                language="zh"
            )
        
        processing_time = time.time() - start_time
        print(f"✅ 處理完成 (時間: {processing_time:.2f}秒)")
        print(f"📝 獲得 {len(transcription.words)} 個詞彙的時間戳記")
        
        # 創建自定義 SRT (控制段落長度)
        custom_srt = create_custom_srt_from_words(transcription.words, max_chars=25, max_duration=3.0)
        
        with open("test3_whisper1_word_level.srt", "w", encoding="utf-8") as f:
            f.write(custom_srt)
        
        analysis = analyze_srt_for_long_segments(custom_srt, "Whisper-1 詞彙級自定義")
        results.append(('Whisper-1 詞彙級自定義', analysis, custom_srt))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 4. Groq Whisper Large v3 基準
    print(f"\n📊 測試 4: Groq Whisper Large v3 基準")
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
        print(f"✅ 處理完成 (時間: {processing_time:.2f}秒)")
        
        srt_content = create_srt_from_segments(transcription.segments)
        
        with open("test4_groq_baseline.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        analysis = analyze_srt_for_long_segments(srt_content, "Groq Large v3 基準")
        results.append(('Groq Large v3 基準', analysis, srt_content))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 5. Groq Whisper Large v3 + 專業 Prompt
    print(f"\n📊 測試 5: Groq Whisper Large v3 + 專業 Prompt")
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                response_format="verbose_json",
                prompt=anti_long_segment_prompt,
                language="zh"
            )
        
        processing_time = time.time() - start_time
        print(f"✅ 處理完成 (時間: {processing_time:.2f}秒)")
        
        srt_content = create_srt_from_segments(transcription.segments)
        
        with open("test5_groq_prompt.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        analysis = analyze_srt_for_long_segments(srt_content, "Groq Large v3 + 專業Prompt")
        results.append(('Groq Large v3 + 專業Prompt', analysis, srt_content))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 最終比較 - 專注於解決段落過長問題
    print(f"\n" + "=" * 80)
    print(f"🎯 解決段落過長問題 - 最終比較結果")
    print("=" * 80)
    
    if results:
        # 按解決問題效果排序
        results.sort(key=lambda x: x[1]['problem_solving_score'], reverse=True)
        
        print(f"📈 解決段落過長問題效果排行:")
        
        for i, (method, analysis, content) in enumerate(results, 1):
            print(f"\n  {i}. {method}")
            print(f"     問題解決效果: {analysis['problem_solving_score']:.1f}/100")
            print(f"     🚨 嚴重過長段落: {analysis['very_long_count']} 個")
            print(f"     ⚠️ 過長段落: {analysis['long_count']} 個")
            print(f"     ✅ 理想段落: {analysis['good_count']} 個 ({analysis['good_count']/analysis['total_segments']*100:.1f}%)")
            print(f"     評級: {analysis['rating']}")
            
            if analysis['very_long_count'] == 0 and analysis['long_count'] <= 2:
                print(f"     🎉 成功解決您的段落過長問題！")
        
        # 最佳解決方案
        best_solution = results[0]
        print(f"\n🏆 最佳解決方案: {best_solution[0]}")
        print(f"   問題解決效果: {best_solution[1]['problem_solving_score']:.1f}/100")
        print(f"   {best_solution[1]['rating']}")
        
        if best_solution[1]['very_long_count'] == 0:
            print(f"   ✅ 完全解決了嚴重過長段落問題")
        
        if best_solution[1]['long_count'] <= 2:
            print(f"   ✅ 過長段落控制良好")
    
    print(f"\n🎉 正確測試完成！")
    return results

if __name__ == "__main__":
    main()
