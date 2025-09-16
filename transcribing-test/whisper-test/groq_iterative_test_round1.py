#!/usr/bin/env python3
"""
Groq Whisper Large v3 迭代測試 - 第一輪
基於實際結果分析問題並改進
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

def analyze_and_display_srt(srt_content, test_name):
    """分析 SRT 並顯示實際內容"""
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
    
    # 實際顯示內容並分析問題
    problem_segments = []
    very_long_segments = []
    
    print(f"\n📋 實際段落內容:")
    for seg in segments:
        if seg['length'] > 40:
            status = "🚨 嚴重過長 (主要問題!)"
            very_long_segments.append(seg)
            problem_segments.append(seg)
        elif seg['length'] > 30:
            status = "⚠️ 過長 (需改善)"
            problem_segments.append(seg)
        elif seg['length'] >= 15:
            status = "✅ 理想"
        else:
            status = "🔸 過短"
        
        print(f"  {seg['id']:2d}. ({seg['length']:2d}字符) {status}")
        print(f"      {seg['text']}")
        print()
    
    # 詳細分析問題
    print(f"🎯 問題分析:")
    print(f"  🚨 嚴重過長段落: {len(very_long_segments)} 個")
    print(f"  ⚠️ 總問題段落: {len(problem_segments)} 個")
    
    if problem_segments:
        print(f"\n🔍 問題段落詳細分析:")
        for seg in problem_segments:
            print(f"  段落 {seg['id']}: {seg['length']} 字符")
            print(f"    內容: {seg['text']}")
            
            # 分析問題原因
            issues = []
            if '。' in seg['text']:
                issues.append("包含句號，應該分段")
            if '，' in seg['text'] and seg['text'].count('，') >= 2:
                issues.append("包含多個逗號，可在逗號處分段")
            if '、' in seg['text']:
                issues.append("包含頓號，可在頓號處分段")
            
            if issues:
                print(f"    問題原因: {'; '.join(issues)}")
            print()
    
    # 生成下一輪的改進建議
    improvement_suggestions = []
    
    if very_long_segments:
        improvement_suggestions.append("必須強制要求在句號處分段")
        improvement_suggestions.append("必須強制要求段落不超過 25 字符")
    
    if len(problem_segments) > 3:
        improvement_suggestions.append("需要更嚴格的長度控制")
        improvement_suggestions.append("需要明確指定分段標點符號")
    
    return {
        'segments': segments,
        'total_segments': len(segments),
        'very_long_count': len(very_long_segments),
        'problem_count': len(problem_segments),
        'max_length': max(seg['length'] for seg in segments) if segments else 0,
        'avg_length': sum(seg['length'] for seg in segments) / len(segments) if segments else 0,
        'improvement_suggestions': improvement_suggestions,
        'problem_segments': problem_segments
    }

def main():
    """Groq Whisper Large v3 第一輪迭代測試"""
    print("🔄 Groq Whisper Large v3 - 第一輪迭代測試")
    print("=" * 80)
    print("目標：找到能讓 Groq Large v3 比 Whisper-1 更好的 Prompt")
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
    
    # 第一輪測試的 Prompt 設計
    round1_prompts = [
        ("基準測試", ""),
        
        ("嚴格長度控制", """財經新聞轉錄。嚴格要求：
- 每個段落最多 25 個字符，絕對不可超過
- 必須在句號「。」處分段
- 必須在問號「？」處分段
- 如果超過 25 字符，必須強制分段"""),
        
        ("標點符號分段", """轉錄財經新聞為字幕。分段規則：
- 遇到句號「。」立即分段
- 遇到問號「？」立即分段
- 遇到感嘆號「！」立即分段
- 如果沒有標點符號，每 20 字符強制分段
- 使用繁體中文"""),
        
        ("防止合併策略", """財經新聞字幕轉錄。防止段落過長策略：
- 禁止將多個完整句子合併在一個段落
- 每個段落只能包含一個主要概念
- 如果內容包含「還警告」「結果」「然後」等連接詞，必須分段
- 段落長度上限 25 字符""")
    ]
    
    results = []
    
    for prompt_name, prompt_text in round1_prompts:
        print(f"\n📊 測試: {prompt_name}")
        if prompt_text:
            print(f"Prompt: {prompt_text[:100]}...")
        
        try:
            start_time = time.time()
            
            params = {
                "model": "whisper-large-v3",
                "file": open(audio_file, "rb"),
                "response_format": "verbose_json",
                "language": "zh"
            }
            
            if prompt_text:
                params["prompt"] = prompt_text
            
            transcription = groq_client.audio.transcriptions.create(**params)
            
            processing_time = time.time() - start_time
            print(f"✅ 成功 (時間: {processing_time:.2f}秒)")
            
            # 創建 SRT
            srt_content = create_srt_from_segments(transcription.segments)
            
            # 保存結果
            filename = f"groq_round1_{prompt_name.replace(' ', '_')}.srt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(srt_content)
            print(f"💾 已保存: {filename}")
            
            # 實際分析內容
            analysis = analyze_and_display_srt(srt_content, f"Groq {prompt_name}")
            
            results.append({
                'prompt_name': prompt_name,
                'prompt_text': prompt_text,
                'analysis': analysis,
                'srt_content': srt_content,
                'processing_time': processing_time
            })
            
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
        
        time.sleep(1)
    
    # 第一輪結果分析
    print(f"\n" + "=" * 80)
    print(f"📊 第一輪測試結果分析")
    print("=" * 80)
    
    if results:
        # 與 Whisper-1 基準比較 (19 字符最長段落)
        whisper1_max_length = 19
        
        print(f"🎯 與 Whisper-1 基準比較 (最長段落 {whisper1_max_length} 字符):")
        
        better_results = []
        
        for result in results:
            analysis = result['analysis']
            print(f"\n  {result['prompt_name']}:")
            print(f"    最長段落: {analysis['max_length']} 字符")
            print(f"    問題段落: {analysis['problem_count']} 個")
            print(f"    嚴重過長: {analysis['very_long_count']} 個")
            
            if analysis['max_length'] <= whisper1_max_length and analysis['very_long_count'] == 0:
                print(f"    🎉 比 Whisper-1 更好或相當！")
                better_results.append(result)
            else:
                print(f"    ❌ 不如 Whisper-1")
        
        # 準備第二輪測試的改進建議
        print(f"\n🔧 第二輪測試改進方向:")
        
        if not better_results:
            print(f"  第一輪沒有找到比 Whisper-1 更好的方案")
            print(f"  需要更激進的 Prompt 策略")
            
            # 分析最常見的問題
            all_problem_segments = []
            for result in results:
                all_problem_segments.extend(result['analysis']['problem_segments'])
            
            if all_problem_segments:
                print(f"\n  常見問題模式:")
                common_issues = {}
                for seg in all_problem_segments:
                    text = seg['text']
                    if '還警告' in text:
                        common_issues['還警告句型'] = text
                    if '結果' in text and len(text) > 30:
                        common_issues['結果句型'] = text
                    if '比特幣' in text and len(text) > 30:
                        common_issues['比特幣句型'] = text
                
                for issue_type, example in common_issues.items():
                    print(f"    - {issue_type}: {example[:50]}...")
        else:
            best_result = min(better_results, key=lambda x: x['analysis']['max_length'])
            print(f"  第一輪最佳方案: {best_result['prompt_name']}")
            print(f"  可以進一步優化")
    
    print(f"\n📋 第二輪測試準備:")
    print(f"  基於第一輪結果，設計更精確的 Prompt")
    print(f"  針對發現的問題模式進行專門處理")
    
    print(f"\n🎉 第一輪迭代測試完成！")
    return results

if __name__ == "__main__":
    main()
