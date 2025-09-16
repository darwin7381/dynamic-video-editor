#!/usr/bin/env python3
"""
針對 SRT 段落過長問題的專業解決方案測試
使用專業設計的 Prompt
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

def analyze_subtitle_quality(srt_content, model_name):
    """分析字幕品質 - 專注於實際使用體驗"""
    print(f"\n📺 {model_name} - 字幕實用性分析")
    print("=" * 50)
    
    lines = srt_content.strip().split('\n')
    segments = []
    
    i = 0
    while i < len(lines):
        if lines[i].strip().isdigit():
            segment_id = int(lines[i])
            if i + 2 < len(lines):
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
        print("❌ 無法解析 SRT 內容")
        return None
    
    # 實際字幕品質評估
    print(f"📊 字幕基本資訊:")
    print(f"  段落總數: {len(segments)}")
    
    lengths = [seg['length'] for seg in segments]
    avg_length = sum(lengths) / len(lengths)
    
    print(f"  平均長度: {avg_length:.1f} 字符")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  最短段落: {min(lengths)} 字符")
    
    # 字幕觀看體驗分析
    print(f"\n📺 觀看體驗分析:")
    
    # 理想字幕長度 (15-35 字符，適合螢幕顯示)
    ideal_count = sum(1 for l in lengths if 15 <= l <= 35)
    short_count = sum(1 for l in lengths if l < 15)
    long_count = sum(1 for l in lengths if l > 35)
    very_long_count = sum(1 for l in lengths if l > 50)
    
    print(f"  理想長度 (15-35字符): {ideal_count} 個 ({ideal_count/len(segments)*100:.1f}%)")
    print(f"  過短 (<15字符): {short_count} 個 ({short_count/len(segments)*100:.1f}%)")
    print(f"  過長 (>35字符): {long_count} 個 ({long_count/len(segments)*100:.1f}%)")
    print(f"  嚴重過長 (>50字符): {very_long_count} 個 ({very_long_count/len(segments)*100:.1f}%)")
    
    # 內容品質分析
    print(f"\n📖 內容品質檢查:")
    print(f"實際字幕內容 (前 6 個段落):")
    
    quality_issues = []
    
    for seg in segments[:6]:
        text = seg['text']
        time_info = seg['time']
        length = seg['length']
        
        # 檢查各種品質指標
        has_proper_ending = text.endswith(('。', '！', '？', '.', '!', '?'))
        has_punctuation = any(p in text for p in ['，', '。', '！', '？', ',', '.', '!', '?', '、'])
        is_readable_length = 15 <= length <= 35
        
        # 評估字幕品質
        quality_score = ""
        if is_readable_length:
            quality_score += "📏✅"
        else:
            quality_score += "📏❌"
            if length > 35:
                quality_issues.append(f"段落 {seg['id']} 過長 ({length} 字符)")
        
        if has_punctuation:
            quality_score += " 📝✅"
        else:
            quality_score += " 📝❌"
            quality_issues.append(f"段落 {seg['id']} 缺少標點符號")
        
        if has_proper_ending:
            quality_score += " 🔚✅"
        else:
            quality_score += " 🔚❌"
        
        print(f"  {seg['id']}. [{time_info}] ({length}字符) {quality_score}")
        print(f"      {text}")
        print()
    
    # 問題總結
    if quality_issues:
        print(f"⚠️ 發現的品質問題:")
        for issue in quality_issues[:5]:  # 只顯示前 5 個問題
            print(f"  - {issue}")
        if len(quality_issues) > 5:
            print(f"  - ... 還有 {len(quality_issues) - 5} 個問題")
    else:
        print(f"✅ 沒有發現明顯的品質問題")
    
    # 整體評級
    ideal_ratio = ideal_count / len(segments)
    long_ratio = long_count / len(segments)
    
    if ideal_ratio > 0.7 and long_ratio < 0.1:
        overall_rating = "🏆 優秀 - 適合直接使用"
    elif ideal_ratio > 0.5 and long_ratio < 0.2:
        overall_rating = "✅ 良好 - 稍作調整即可"
    elif ideal_ratio > 0.3 and long_ratio < 0.4:
        overall_rating = "⚠️ 一般 - 需要優化"
    else:
        overall_rating = "❌ 不佳 - 不適合字幕使用"
    
    print(f"\n🎯 整體評級: {overall_rating}")
    
    return {
        'total_segments': len(segments),
        'avg_length': avg_length,
        'ideal_count': ideal_count,
        'long_count': long_count,
        'very_long_count': very_long_count,
        'ideal_ratio': ideal_ratio,
        'long_ratio': long_ratio,
        'quality_issues': quality_issues,
        'overall_rating': overall_rating
    }

def main():
    """主測試函數 - 針對您的具體問題設計專業 Prompt"""
    
    # API 設定
    openai_api_key = os.getenv("OPENAI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    print("🎯 針對 SRT 段落過長問題的專業解決方案測試")
    print("=" * 80)
    
    # 根據您的具體問題設計的專業 Prompt
    targeted_prompt = """請轉錄這段財經新聞音頻，並確保輸出適合製作字幕：

要求：
1. 每個段落控制在 20-30 個中文字符
2. 在自然的語音停頓處分段
3. 保持語義完整，不要在句子中間斷開
4. 正確識別公司名稱：台積電、聯電、日月光、NVIDIA、ADR
5. 正確識別金融術語：那斯達克、費半、比特幣
6. 添加適當的標點符號，但不要過度使用

這是一段關於中美貿易戰和股市影響的新聞內容。"""
    
    # 初始化客戶端
    openai_client = OpenAI(api_key=openai_api_key)
    groq_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    
    test_results = []
    srt_analyses = {}
    
    # 測試 1: OpenAI whisper-1 (基準)
    print(f"\n📊 測試 1: OpenAI Whisper-1 (無 Prompt)")
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
        print(f"✅ 處理時間: {processing_time:.2f} 秒")
        
        srt_content = create_srt_from_segments(transcription.segments)
        with open("whisper1_baseline.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        analysis = analyze_subtitle_quality(srt_content, "Whisper-1 基準")
        srt_analyses["Whisper-1 基準"] = analysis
        
        test_results.append({
            'model': 'whisper-1',
            'config': '基準測試',
            'processing_time': processing_time,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"❌ Whisper-1 基準測試失敗: {str(e)}")
    
    # 測試 2: OpenAI whisper-1 (專業 Prompt)
    print(f"\n📊 測試 2: OpenAI Whisper-1 (專業 Prompt)")
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"],
                prompt=targeted_prompt,
                language="zh"
            )
        
        processing_time = time.time() - start_time
        print(f"✅ 處理時間: {processing_time:.2f} 秒")
        
        srt_content = create_srt_from_segments(transcription.segments)
        with open("whisper1_professional_prompt.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        analysis = analyze_subtitle_quality(srt_content, "Whisper-1 專業Prompt")
        srt_analyses["Whisper-1 專業Prompt"] = analysis
        
        test_results.append({
            'model': 'whisper-1',
            'config': '專業 Prompt',
            'processing_time': processing_time,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"❌ Whisper-1 專業 Prompt 測試失敗: {str(e)}")
    
    # 測試 3: Groq Whisper Large v3 (無 Prompt)
    print(f"\n📊 測試 3: Groq Whisper Large v3 (無 Prompt)")
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
        print(f"✅ 處理時間: {processing_time:.2f} 秒")
        
        srt_content = create_srt_from_segments(transcription.segments)
        with open("groq_large_v3_baseline.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        analysis = analyze_subtitle_quality(srt_content, "Groq Large v3 基準")
        srt_analyses["Groq Large v3 基準"] = analysis
        
        test_results.append({
            'model': 'groq-whisper-large-v3',
            'config': '基準測試',
            'processing_time': processing_time,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"❌ Groq Large v3 基準測試失敗: {str(e)}")
    
    # 測試 4: Groq Whisper Large v3 (專業 Prompt)
    print(f"\n📊 測試 4: Groq Whisper Large v3 (專業 Prompt)")
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                response_format="verbose_json",
                prompt=targeted_prompt,
                language="zh"
            )
        
        processing_time = time.time() - start_time
        print(f"✅ 處理時間: {processing_time:.2f} 秒")
        
        srt_content = create_srt_from_segments(transcription.segments)
        with open("groq_large_v3_professional_prompt.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        analysis = analyze_subtitle_quality(srt_content, "Groq Large v3 專業Prompt")
        srt_analyses["Groq Large v3 專業Prompt"] = analysis
        
        test_results.append({
            'model': 'groq-whisper-large-v3',
            'config': '專業 Prompt',
            'processing_time': processing_time,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"❌ Groq Large v3 專業 Prompt 測試失敗: {str(e)}")
    
    # 最終比較和推薦
    print(f"\n" + "=" * 80)
    print(f"🏆 解決 SRT 段落過長問題 - 最終推薦")
    print("=" * 80)
    
    if srt_analyses:
        # 按整體評級排序
        best_solutions = []
        
        for name, analysis in srt_analyses.items():
            # 計算解決問題的效果
            problem_solving_score = 0
            
            # 長段落控制 (40%)
            if analysis['long_ratio'] < 0.1:
                problem_solving_score += 40
            elif analysis['long_ratio'] < 0.2:
                problem_solving_score += 30
            elif analysis['long_ratio'] < 0.3:
                problem_solving_score += 20
            
            # 理想段落比例 (30%)
            problem_solving_score += analysis['ideal_ratio'] * 30
            
            # 沒有嚴重過長段落 (30%)
            if analysis['very_long_count'] == 0:
                problem_solving_score += 30
            elif analysis['very_long_count'] <= 2:
                problem_solving_score += 20
            
            best_solutions.append((name, analysis, problem_solving_score))
        
        # 排序
        best_solutions.sort(key=lambda x: x[2], reverse=True)
        
        print(f"🎯 解決方案排行榜:")
        for i, (name, analysis, score) in enumerate(best_solutions, 1):
            print(f"  {i}. {name} - 問題解決度: {score:.1f}/100")
            print(f"     過長段落: {analysis['long_count']} 個 ({analysis['long_ratio']*100:.1f}%)")
            print(f"     理想段落: {analysis['ideal_count']} 個 ({analysis['ideal_ratio']*100:.1f}%)")
            print(f"     整體評級: {analysis['overall_rating']}")
            print()
        
        # 最終推薦
        winner = best_solutions[0]
        print(f"🏅 最佳解決方案: {winner[0]}")
        print(f"   問題解決度: {winner[2]:.1f}/100")
        print(f"   {winner[1]['overall_rating']}")
    
    print(f"\n🎉 針對性測試完成！")

if __name__ == "__main__":
    main()
