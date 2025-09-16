#!/usr/bin/env python3
"""
最終 ElevenLabs 和 AssemblyAI 完整測試
基於發現的詞彙級時間戳記創建最佳 SRT
"""

import os
import requests
import json
import assemblyai as aai
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def format_srt_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def create_optimized_srt_from_words(words, max_chars=18, service_name=""):
    """從詞彙級時間戳記創建優化的 SRT"""
    if not words:
        return "無詞彙資訊"
    
    segments = []
    current_segment = {
        'start': None,
        'end': None,
        'text': ''
    }
    
    for word in words:
        # 處理不同服務的詞彙格式
        if service_name == "ElevenLabs":
            word_text = word['text'].strip()
            start_time = word['start']
            end_time = word['end']
        else:  # AssemblyAI
            word_text = word.text.strip()
            start_time = word.start / 1000
            end_time = word.end / 1000
        
        if not word_text:
            continue
            
        if current_segment['start'] is None:
            current_segment['start'] = start_time
            current_segment['end'] = end_time
            current_segment['text'] = word_text
        elif len(current_segment['text'] + word_text) > max_chars:
            # 完成當前段落
            segments.append(current_segment.copy())
            # 開始新段落
            current_segment = {
                'start': start_time,
                'end': end_time,
                'text': word_text
            }
        else:
            # 添加到當前段落
            current_segment['text'] += word_text
            current_segment['end'] = end_time
    
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

def comprehensive_evaluation(srt_content, transcript_text, service_name):
    """全面評估服務品質"""
    print(f"\n🎯 {service_name} 全面品質評估")
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
    problem_segments = [seg for seg in segments if seg['length'] > 30]
    very_long_segments = [seg for seg in segments if seg['length'] > 40]
    
    print(f"📊 段落控制分析:")
    print(f"  總段落數: {len(segments)}")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  平均長度: {sum(lengths)/len(lengths):.1f} 字符")
    print(f"  問題段落 (>30字符): {len(problem_segments)} 個")
    print(f"  嚴重問題 (>40字符): {len(very_long_segments)} 個")
    
    # 轉錄品質分析
    has_traditional = any(char in transcript_text for char in ['台積電', '聯電', '連準會', '納斯達克'])
    punctuation_count = transcript_text.count('，') + transcript_text.count('。') + transcript_text.count('！') + transcript_text.count('？')
    
    terms_found = 0
    if '台積電' in transcript_text:
        terms_found += 1
        print(f"  ✅ 台積電 識別正確")
    if 'NVIDIA' in transcript_text or '輝達' in transcript_text or '辉达' in transcript_text:
        terms_found += 1
        print(f"  ✅ NVIDIA/輝達 識別正確")
    if '納斯達克' in transcript_text or '那斯达克' in transcript_text:
        terms_found += 1
        print(f"  ✅ 納斯達克 識別正確")
    if '比特幣' in transcript_text or '比特币' in transcript_text:
        terms_found += 1
        print(f"  ✅ 比特幣 識別正確")
    
    print(f"\n📝 轉錄品質分析:")
    print(f"  語言: {'繁體中文 ✅' if has_traditional else '簡體中文 ❌'}")
    print(f"  標點符號: {punctuation_count} 個")
    print(f"  專業術語: {terms_found}/4 個")
    
    # 顯示代表性段落
    print(f"\n📋 前5個段落:")
    for seg in segments[:5]:
        status = "🚨" if seg['length'] > 40 else "⚠️" if seg['length'] > 30 else "✅" if 15 <= seg['length'] <= 25 else "🔸"
        print(f"  {seg['id']}. ({seg['length']}字符) {status} {seg['text']}")
    
    # 計算評分
    segment_score = 0
    if max(lengths) <= 18 and len(problem_segments) == 0:
        segment_score = 50
    elif max(lengths) <= 25 and len(very_long_segments) == 0:
        segment_score = 40
    elif len(very_long_segments) == 0:
        segment_score = 30
    else:
        segment_score = 20
    
    quality_score = 0
    if has_traditional:
        quality_score += 20
    quality_score += min(punctuation_count * 1, 15)  # 標點符號評分
    quality_score += terms_found * 3.75
    
    total_score = segment_score + quality_score
    
    print(f"\n📈 評分:")
    print(f"  段落控制: {segment_score}/50")
    print(f"  轉錄品質: {quality_score:.1f}/50")
    print(f"  總評分: {total_score:.1f}/100")
    
    # 與最佳方案比較
    print(f"\n🏆 與 Groq 最佳方案比較 (95.2分):")
    if total_score > 95:
        print(f"  🎉 {service_name} 比最佳方案更好！")
        verdict = "更好"
    elif total_score > 85:
        print(f"  ✅ {service_name} 接近最佳方案")
        verdict = "接近"
    else:
        print(f"  ❌ {service_name} 不如最佳方案")
        verdict = "不如"
    
    return {
        'total_score': total_score,
        'segment_score': segment_score,
        'quality_score': quality_score,
        'max_length': max(lengths),
        'problem_count': len(problem_segments),
        'verdict': verdict,
        'segments': segments
    }

def main():
    """最終完整測試"""
    print("🎯 ElevenLabs 和 AssemblyAI 最終完整測試")
    print("=" * 80)
    
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY_2")
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    results = []
    
    # 1. 測試 ElevenLabs Scribe (使用詞彙級時間戳記)
    print(f"\n🚀 測試 ElevenLabs Scribe 詞彙級 SRT")
    try:
        # 讀取之前的結果
        with open("elevenlabs_scribe_v1_result.json", "r", encoding="utf-8") as f:
            elevenlabs_result = json.load(f)
        
        if 'words' in elevenlabs_result and elevenlabs_result['words']:
            print(f"📝 ElevenLabs 有 {len(elevenlabs_result['words'])} 個詞彙時間戳記")
            
            # 創建優化的 SRT
            optimized_srt = create_optimized_srt_from_words(
                elevenlabs_result['words'], 
                max_chars=18, 
                service_name="ElevenLabs"
            )
            
            with open("elevenlabs_optimized.srt", "w", encoding="utf-8") as f:
                f.write(optimized_srt)
            print(f"💾 優化 SRT 已保存: elevenlabs_optimized.srt")
            
            # 全面評估
            analysis = comprehensive_evaluation(
                optimized_srt, 
                elevenlabs_result['text'], 
                "ElevenLabs Scribe"
            )
            
            if analysis:
                results.append(('ElevenLabs Scribe', analysis))
        
    except Exception as e:
        print(f"❌ ElevenLabs 分析失敗: {str(e)}")
    
    # 2. 測試 AssemblyAI (檢查現有結果)
    print(f"\n🚀 分析 AssemblyAI 現有結果")
    try:
        # 讀取 AssemblyAI 轉錄文字
        with open("assemblyai_transcript.txt", "r", encoding="utf-8") as f:
            assemblyai_text = f.read()
        
        # 讀取 AssemblyAI SRT
        with open("assemblyai_custom.srt", "r", encoding="utf-8") as f:
            assemblyai_srt = f.read()
        
        print(f"📝 AssemblyAI 轉錄文字長度: {len(assemblyai_text)} 字符")
        
        # 全面評估
        analysis = comprehensive_evaluation(
            assemblyai_srt,
            assemblyai_text,
            "AssemblyAI Universal-1"
        )
        
        if analysis:
            results.append(('AssemblyAI Universal-1', analysis))
        
    except Exception as e:
        print(f"❌ AssemblyAI 分析失敗: {str(e)}")
    
    # 3. 最終比較和更新報告
    print(f"\n" + "=" * 80)
    print(f"🏆 最終測試結果 - 更新 9/12 報告")
    print("=" * 80)
    
    current_best = {
        'name': 'Groq + Prompt + 詞彙級',
        'score': 95.2
    }
    
    print(f"📊 現有最佳方案: {current_best['name']} ({current_best['score']}分)")
    
    if results:
        # 按評分排序
        results.sort(key=lambda x: x[1]['total_score'], reverse=True)
        
        print(f"\n📈 新測試服務排名:")
        for i, (service_name, analysis) in enumerate(results, 1):
            print(f"  {i}. {service_name}: {analysis['total_score']:.1f}/100")
            print(f"     段落控制: {analysis['segment_score']}/50 (最長 {analysis['max_length']} 字符)")
            print(f"     轉錄品質: {analysis['quality_score']:.1f}/50")
            print(f"     問題段落: {analysis['problem_count']} 個")
            print(f"     評估: {analysis['verdict']} 最佳方案")
        
        # 檢查是否有更好的方案
        better_services = [r for r in results if r[1]['total_score'] > current_best['score']]
        
        if better_services:
            best_new = better_services[0]
            print(f"\n🎉 發現更好的方案！")
            print(f"🏆 新的最佳方案: {best_new[0]} ({best_new[1]['total_score']:.1f}分)")
            print(f"   比 Groq 方案好 {best_new[1]['total_score'] - current_best['score']:.1f} 分")
        else:
            print(f"\n📊 結論: Groq 最佳方案仍然是最好的")
            if results:
                closest = results[0]
                print(f"   最接近的是 {closest[0]} ({closest[1]['total_score']:.1f}分)")
    else:
        print(f"\n😞 沒有成功的測試結果")
    
    print(f"\n🎉 最終完整測試完成！")
    return results

if __name__ == "__main__":
    main()
