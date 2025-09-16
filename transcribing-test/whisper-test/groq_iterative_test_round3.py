#!/usr/bin/env python3
"""
Groq Whisper Large v3 迭代測試 - 第三輪 (最終輪)
基於前兩輪結果：基準測試最好，Prompt 會讓結果變差
嘗試非常保守的微調
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

def final_comparison_with_whisper1(analysis, test_name):
    """最終與 Whisper-1 比較"""
    whisper1_max_length = 19
    
    print(f"\n🏆 {test_name} - 最終比較結果:")
    print(f"  Groq 最長段落: {analysis['max_length']} 字符")
    print(f"  Whisper-1 最長段落: {whisper1_max_length} 字符")
    print(f"  Groq 問題段落: {analysis['problem_count']} 個")
    print(f"  Whisper-1 問題段落: 0 個")
    
    if analysis['max_length'] < whisper1_max_length and analysis['problem_count'] == 0:
        verdict = "🎉 Groq 確實比 Whisper-1 更好！"
        is_better = True
    elif analysis['max_length'] == whisper1_max_length and analysis['problem_count'] == 0:
        verdict = "✅ Groq 與 Whisper-1 相當"
        is_better = True
    else:
        verdict = "❌ Groq 不如 Whisper-1"
        is_better = False
    
    print(f"  🎯 結論: {verdict}")
    
    return is_better

def analyze_srt_final(srt_content, test_name):
    """最終分析 SRT 內容"""
    print(f"\n📺 {test_name} - 最終內容檢查")
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
    print(f"📏 長度範圍: {min(seg['length'] for seg in segments)} - {max(seg['length'] for seg in segments)} 字符")
    
    # 分類段落
    problem_segments = [seg for seg in segments if seg['length'] > 30]
    very_long_segments = [seg for seg in segments if seg['length'] > 40]
    
    # 只顯示關鍵資訊
    if problem_segments:
        print(f"\n🚨 問題段落 (>30字符): {len(problem_segments)} 個")
        for seg in problem_segments[:3]:  # 只顯示前3個
            print(f"  {seg['id']}. ({seg['length']}字符) {seg['text'][:50]}...")
    else:
        print(f"\n✅ 沒有問題段落 (>30字符)")
    
    return {
        'segments': segments,
        'total_segments': len(segments),
        'very_long_count': len(very_long_segments),
        'problem_count': len(problem_segments),
        'max_length': max(seg['length'] for seg in segments) if segments else 0,
        'avg_length': sum(seg['length'] for seg in segments) / len(segments) if segments else 0
    }

def main():
    """Groq Whisper Large v3 第三輪 (最終) 迭代測試"""
    print("🔄 Groq Whisper Large v3 - 第三輪 (最終) 迭代測試")
    print("=" * 80)
    print("策略：基於前兩輪結果，基準測試最好，嘗試非常保守的微調")
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
    
    # 第三輪測試：非常保守的微調
    round3_prompts = [
        ("純繁體中文", "使用繁體中文"),
        
        ("最小調整", "財經新聞。使用繁體中文。"),
        
        ("基準+標點", "財經新聞內容。使用繁體中文，適當標點符號。"),
        
        ("最終嘗試", "這是財經新聞。請使用繁體中文轉錄。")
    ]
    
    results = []
    
    # 先測試基準 (對照組)
    print(f"\n📊 對照組: 基準測試 (無 Prompt)")
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
        print(f"✅ 成功 (時間: {processing_time:.2f}秒)")
        
        srt_content = create_srt_from_segments(transcription.segments)
        
        with open("groq_round3_baseline.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        baseline_analysis = analyze_srt_final(srt_content, "Groq 基準")
        baseline_is_better = final_comparison_with_whisper1(baseline_analysis, "基準測試")
        
        results.append({
            'prompt_name': '基準測試',
            'analysis': baseline_analysis,
            'is_better': baseline_is_better,
            'srt_content': srt_content
        })
        
    except Exception as e:
        print(f"❌ 基準測試失敗: {str(e)}")
    
    # 測試保守的 Prompt
    for prompt_name, prompt_text in round3_prompts:
        print(f"\n📊 第三輪測試: {prompt_name}")
        print(f"Prompt: '{prompt_text}'")
        
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
            filename = f"groq_round3_{prompt_name.replace(' ', '_')}.srt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(srt_content)
            print(f"💾 已保存: {filename}")
            
            # 分析
            analysis = analyze_srt_final(srt_content, f"Groq {prompt_name}")
            is_better = final_comparison_with_whisper1(analysis, prompt_name)
            
            results.append({
                'prompt_name': prompt_name,
                'prompt_text': prompt_text,
                'analysis': analysis,
                'is_better': is_better,
                'srt_content': srt_content,
                'processing_time': processing_time
            })
            
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
        
        time.sleep(1)
    
    # 三輪測試最終總結
    print(f"\n" + "=" * 80)
    print(f"🏆 Groq Whisper Large v3 三輪迭代測試最終結論")
    print("=" * 80)
    
    better_solutions = [r for r in results if r['is_better']]
    
    if better_solutions:
        print(f"🎉 找到 {len(better_solutions)} 個比 Whisper-1 更好或相當的方案:")
        
        # 按最長段落排序
        better_solutions.sort(key=lambda x: x['analysis']['max_length'])
        
        for i, result in enumerate(better_solutions, 1):
            analysis = result['analysis']
            print(f"\n  {i}. {result['prompt_name']}")
            print(f"     最長段落: {analysis['max_length']} 字符 (vs Whisper-1 的 19)")
            print(f"     總段落數: {analysis['total_segments']}")
            print(f"     問題段落: {analysis['problem_count']} 個")
        
        # 最終推薦
        best_groq = better_solutions[0]
        print(f"\n🏅 Groq 的最佳方案: {best_groq['prompt_name']}")
        print(f"   最長段落: {best_groq['analysis']['max_length']} 字符")
        
        if best_groq['analysis']['max_length'] < 19:
            print(f"   🎉 確實比 Whisper-1 更好！")
            final_verdict = "Groq Whisper Large v3 確實比 Whisper-1 更好"
        else:
            print(f"   ✅ 與 Whisper-1 相當")
            final_verdict = "Groq Whisper Large v3 與 Whisper-1 相當"
    else:
        print(f"😞 三輪測試都沒有找到比 Whisper-1 更好的方案")
        print(f"   結論：Groq Whisper Large v3 無法超越 Whisper-1")
        final_verdict = "Groq Whisper Large v3 無法超越 Whisper-1"
    
    print(f"\n🎯 Groq Whisper Large v3 最終結論: {final_verdict}")
    print(f"🎉 三輪迭代測試完成！")
    
    return results

if __name__ == "__main__":
    main()
