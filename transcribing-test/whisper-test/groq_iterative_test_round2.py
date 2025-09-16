#!/usr/bin/env python3
"""
Groq Whisper Large v3 迭代測試 - 第二輪
基於第一輪結果改進：基準測試已經很好，嘗試進一步優化
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

def compare_with_whisper1(analysis, test_name):
    """與 Whisper-1 基準比較"""
    whisper1_max_length = 19  # Whisper-1 的最長段落
    whisper1_problem_count = 0  # Whisper-1 沒有問題段落
    
    print(f"\n🏆 {test_name} vs Whisper-1 比較:")
    print(f"  最長段落: {analysis['max_length']} vs {whisper1_max_length} (Whisper-1)")
    print(f"  問題段落: {analysis['problem_count']} vs {whisper1_problem_count} (Whisper-1)")
    
    is_better = False
    improvements = []
    
    if analysis['max_length'] < whisper1_max_length:
        is_better = True
        improvements.append(f"最長段落更短 ({analysis['max_length']} vs {whisper1_max_length})")
    
    if analysis['problem_count'] <= whisper1_problem_count and analysis['very_long_count'] == 0:
        if analysis['max_length'] <= whisper1_max_length:
            is_better = True
            improvements.append("沒有段落過長問題且控制良好")
    
    if is_better:
        print(f"  🎉 比 Whisper-1 更好！改善: {', '.join(improvements)}")
        return True
    else:
        print(f"  ❌ 不如 Whisper-1")
        return False

def analyze_srt_detailed(srt_content, test_name):
    """詳細分析 SRT 內容"""
    print(f"\n📺 {test_name} - 實際內容分析")
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
    
    # 只顯示問題段落和優秀段落
    problem_segments = []
    very_long_segments = []
    good_segments = []
    
    for seg in segments:
        if seg['length'] > 40:
            status = "🚨 嚴重過長"
            very_long_segments.append(seg)
            problem_segments.append(seg)
        elif seg['length'] > 30:
            status = "⚠️ 過長"
            problem_segments.append(seg)
        elif 15 <= seg['length'] <= 25:
            status = "✅ 理想"
            good_segments.append(seg)
    
    # 顯示關鍵段落
    if problem_segments:
        print(f"\n🚨 問題段落:")
        for seg in problem_segments:
            print(f"  {seg['id']}. ({seg['length']}字符) {seg['text']}")
    
    if good_segments:
        print(f"\n✅ 優秀段落:")
        for seg in good_segments[:3]:  # 只顯示前3個
            print(f"  {seg['id']}. ({seg['length']}字符) {seg['text']}")
    
    print(f"\n📊 統計:")
    print(f"  嚴重過長 (>40字符): {len(very_long_segments)} 個")
    print(f"  一般過長 (>30字符): {len(problem_segments)} 個") 
    print(f"  理想長度 (15-25字符): {len(good_segments)} 個")
    
    return {
        'segments': segments,
        'total_segments': len(segments),
        'very_long_count': len(very_long_segments),
        'problem_count': len(problem_segments),
        'good_count': len(good_segments),
        'max_length': max(seg['length'] for seg in segments) if segments else 0,
        'avg_length': sum(seg['length'] for seg in segments) / len(segments) if segments else 0,
        'problem_segments': problem_segments
    }

def main():
    """Groq Whisper Large v3 第二輪迭代測試"""
    print("🔄 Groq Whisper Large v3 - 第二輪迭代測試")
    print("=" * 80)
    print("基於第一輪結果：基準測試已經很好 (19字符最長)，嘗試進一步優化")
    print("=" * 80)
    
    # API 設定
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    groq_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    
    # 第二輪測試：基於第一輪結果設計更精確的 Prompt
    round2_prompts = [
        ("輕微優化", """財經新聞轉錄。輕微調整：
- 使用繁體中文
- 適當添加標點符號
- 保持現有的短段落分段風格"""),
        
        ("理想長度優化", """財經新聞轉錄。段落長度優化：
- 目標段落長度：15-20 字符
- 過短段落可適當合併
- 保持語義完整
- 使用繁體中文"""),
        
        ("完美平衡", """財經新聞字幕轉錄。追求完美平衡：
- 段落長度控制在 16-22 字符之間
- 在自然停頓處分段
- 避免過短的段落 (<10字符)
- 絕對不要超過 25 字符
- 使用繁體中文和適當標點符號""")
    ]
    
    results = []
    
    for prompt_name, prompt_text in round2_prompts:
        print(f"\n📊 第二輪測試: {prompt_name}")
        print(f"Prompt 策略: {prompt_text[:100]}...")
        
        try:
            start_time = time.time()
            
            with open(audio_file, "rb") as f:
                transcription = groq_client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=f,
                    response_format="verbose_json",
                    prompt=prompt_text,
                    language="zh"
                )
            
            processing_time = time.time() - start_time
            print(f"✅ 成功 (時間: {processing_time:.2f}秒)")
            
            # 創建 SRT
            srt_content = create_srt_from_segments(transcription.segments)
            
            # 保存結果
            filename = f"groq_round2_{prompt_name.replace(' ', '_')}.srt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(srt_content)
            print(f"💾 已保存: {filename}")
            
            # 詳細分析
            analysis = analyze_srt_detailed(srt_content, f"Groq {prompt_name}")
            
            # 與 Whisper-1 比較
            is_better = compare_with_whisper1(analysis, prompt_name)
            
            results.append({
                'prompt_name': prompt_name,
                'prompt_text': prompt_text,
                'analysis': analysis,
                'is_better_than_whisper1': is_better,
                'srt_content': srt_content,
                'processing_time': processing_time
            })
            
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
        
        time.sleep(1)
    
    # 第二輪結果總結
    print(f"\n" + "=" * 80)
    print(f"📊 第二輪測試結果總結")
    print("=" * 80)
    
    better_solutions = [r for r in results if r['is_better_than_whisper1']]
    
    if better_solutions:
        print(f"🎉 第二輪找到 {len(better_solutions)} 個比 Whisper-1 更好的方案:")
        
        # 按最長段落長度排序 (越短越好)
        better_solutions.sort(key=lambda x: x['analysis']['max_length'])
        
        for i, result in enumerate(better_solutions, 1):
            analysis = result['analysis']
            print(f"\n  {i}. {result['prompt_name']}")
            print(f"     最長段落: {analysis['max_length']} 字符 (vs Whisper-1 的 19)")
            print(f"     問題段落: {analysis['problem_count']} 個")
            print(f"     理想段落: {analysis['good_count']} 個")
        
        # 準備第三輪測試
        best_round2 = better_solutions[0]
        print(f"\n🏆 第二輪最佳: {best_round2['prompt_name']}")
        print(f"   最長段落: {best_round2['analysis']['max_length']} 字符")
        
        if best_round2['analysis']['max_length'] < 15:
            print(f"\n📋 第三輪策略: 微調以增加理想長度段落")
        else:
            print(f"\n📋 第三輪策略: 已經很好，嘗試不同方向的優化")
    else:
        print(f"😞 第二輪沒有找到比 Whisper-1 更好的方案")
        print(f"   所有 Prompt 都讓結果變差")
        print(f"\n📋 第三輪策略: 回到基準測試，嘗試更保守的優化")
    
    print(f"\n🔄 準備進行第三輪測試...")
    return results

if __name__ == "__main__":
    main()
