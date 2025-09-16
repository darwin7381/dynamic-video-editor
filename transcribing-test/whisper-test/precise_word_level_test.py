#!/usr/bin/env python3
"""
精準的詞彙級時間戳記測試
修復 AssemblyAI 解析問題，公平比較兩個服務
"""

import os
import json

def format_srt_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def create_precise_srt_from_words(words, service_name, target_chars=18):
    """精確從詞彙級時間戳記創建 SRT"""
    if not words:
        return "無詞彙資訊"
    
    segments = []
    current_segment = {
        'start': None,
        'end': None,
        'text': ''
    }
    
    for word in words:
        # 處理不同服務的格式
        if service_name == "ElevenLabs":
            word_text = word['text'].strip()
            start_time = word['start']
            end_time = word['end']
        else:  # AssemblyAI
            word_text = word['text'].strip()
            start_time = word['start'] / 1000  # 轉換為秒
            end_time = word['end'] / 1000
        
        if not word_text:
            continue
            
        # 智能分段邏輯
        if current_segment['start'] is None:
            current_segment['start'] = start_time
            current_segment['end'] = end_time
            current_segment['text'] = word_text
        elif len(current_segment['text'] + word_text) > target_chars:
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
    
    return "\n".join(srt_content), segments

def analyze_service_capabilities(data, service_name):
    """分析服務的詳細能力"""
    print(f"\n🔍 {service_name} 詳細能力分析")
    print("=" * 60)
    
    if service_name == "ElevenLabs":
        transcript_text = data['text']
        words = data['words']
        
        print(f"📊 基本資訊:")
        print(f"  語言檢測: {data.get('language_code', 'N/A')}")
        print(f"  語言信心度: {data.get('language_probability', 'N/A')}")
        print(f"  轉錄文字長度: {len(transcript_text)} 字符")
        print(f"  詞彙數量: {len(words)} 個")
        
        print(f"\n🔍 功能支援:")
        print(f"  ✅ 詞彙級時間戳記: {len(words)} 個詞彙")
        print(f"  ❌ 多人辨識: 不支援")
        
        # 檢查詞彙級時間戳記品質
        if words:
            time_gaps = []
            for i in range(1, min(10, len(words))):
                gap = words[i]['start'] - words[i-1]['end']
                time_gaps.append(gap)
            
            avg_gap = sum(time_gaps) / len(time_gaps) if time_gaps else 0
            print(f"  📏 詞彙間隔平均: {avg_gap:.3f} 秒 (時間戳記精確度)")
        
    else:  # AssemblyAI
        transcript_text = data['text']
        words = data.get('words', [])
        
        print(f"📊 基本資訊:")
        print(f"  語言設定: {data.get('language_code', 'N/A')}")
        print(f"  轉錄狀態: {data.get('status', 'N/A')}")
        print(f"  轉錄文字長度: {len(transcript_text)} 字符")
        print(f"  詞彙數量: {len(words)} 個")
        
        print(f"\n🔍 功能支援:")
        if words:
            print(f"  ✅ 詞彙級時間戳記: {len(words)} 個詞彙")
            
            # 檢查說話者標識
            speakers = set()
            for word in words[:20]:  # 檢查前20個詞彙
                if 'speaker' in word:
                    speakers.add(word['speaker'])
            
            if speakers:
                print(f"  ✅ 多人辨識: {len(speakers)} 個說話者 ({', '.join(speakers)})")
            else:
                print(f"  ❌ 多人辨識: 未檢測到說話者標識")
            
            # 檢查信心度
            confidences = [word.get('confidence', 0) for word in words[:10]]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            print(f"  📊 轉錄信心度: {avg_confidence:.3f} (前10個詞彙平均)")
        else:
            print(f"  ❌ 詞彙級時間戳記: 不支援")
    
    return transcript_text, words

def precise_quality_comparison(transcript_text, srt_segments, service_name):
    """精確的品質比較"""
    print(f"\n📊 {service_name} 精確品質評估")
    print("=" * 60)
    
    # 段落控制分析
    lengths = [len(seg['text']) for seg in srt_segments]
    max_length = max(lengths)
    avg_length = sum(lengths) / len(lengths)
    problem_count = sum(1 for l in lengths if l > 30)
    very_long_count = sum(1 for l in lengths if l > 40)
    ideal_count = sum(1 for l in lengths if 15 <= l <= 25)
    
    print(f"📏 段落控制:")
    print(f"  總段落數: {len(srt_segments)}")
    print(f"  最長段落: {max_length} 字符")
    print(f"  平均長度: {avg_length:.1f} 字符")
    print(f"  理想段落 (15-25字符): {ideal_count} 個 ({ideal_count/len(srt_segments)*100:.1f}%)")
    print(f"  問題段落 (>30字符): {problem_count} 個")
    print(f"  嚴重問題 (>40字符): {very_long_count} 個")
    
    # 轉錄品質分析
    punctuation_count = transcript_text.count('，') + transcript_text.count('。') + transcript_text.count('！') + transcript_text.count('？')
    punctuation_count += transcript_text.count(',') + transcript_text.count('.') + transcript_text.count('!') + transcript_text.count('?')
    
    # 專業術語識別 (不區分簡繁體)
    terms_found = 0
    term_details = []
    
    if '台積電' in transcript_text or '台积电' in transcript_text:
        terms_found += 1
        term_details.append('台積電/台积电 ✅')
    
    if 'NVIDIA' in transcript_text or '輝達' in transcript_text or '辉达' in transcript_text:
        terms_found += 1
        term_details.append('NVIDIA/輝達/辉达 ✅')
    
    if '納斯達克' in transcript_text or '那斯达克' in transcript_text:
        terms_found += 1
        term_details.append('納斯達克/那斯达克 ✅')
    
    if '比特幣' in transcript_text or '比特币' in transcript_text:
        terms_found += 1
        term_details.append('比特幣/比特币 ✅')
    
    print(f"\n📝 轉錄品質:")
    print(f"  標點符號: {punctuation_count} 個")
    print(f"  專業術語: {terms_found}/4 個")
    for term in term_details:
        print(f"    - {term}")
    
    # 顯示最佳段落示例
    print(f"\n📋 段落品質示例:")
    ideal_segments = [seg for seg in srt_segments if 15 <= len(seg['text']) <= 25]
    if ideal_segments:
        print(f"  理想段落示例:")
        for seg in ideal_segments[:3]:
            print(f"    ({len(seg['text'])}字符) {seg['text']}")
    
    if problem_count > 0:
        problem_segments = [seg for seg in srt_segments if len(seg['text']) > 30]
        print(f"  問題段落示例:")
        for seg in problem_segments[:2]:
            print(f"    ({len(seg['text'])}字符) {seg['text'][:50]}...")
    
    # 計算公平評分
    segment_score = 0
    if max_length <= 18 and problem_count == 0:
        segment_score = 60
    elif max_length <= 20 and problem_count == 0:
        segment_score = 55
    elif max_length <= 25 and problem_count == 0:
        segment_score = 50
    elif max_length <= 30 and very_long_count == 0:
        segment_score = 40
    else:
        segment_score = 30
    
    accuracy_score = min(punctuation_count * 1.5, 15) + terms_found * 6.25
    total_score = segment_score + accuracy_score
    
    print(f"\n📈 精確評分:")
    print(f"  段落控制: {segment_score}/60")
    print(f"  轉錄準確度: {accuracy_score:.1f}/40")
    print(f"  總評分: {total_score:.1f}/100")
    
    return {
        'total_score': total_score,
        'segment_score': segment_score,
        'accuracy_score': accuracy_score,
        'max_length': max_length,
        'problem_count': problem_count,
        'ideal_count': ideal_count,
        'terms_found': terms_found,
        'punctuation_count': punctuation_count
    }

def main():
    """精準測試並公平比較"""
    print("🎯 精準詞彙級測試 - 公平比較 ElevenLabs 和 AssemblyAI")
    print("=" * 80)
    
    results = []
    
    # 1. 精準分析 ElevenLabs
    print(f"\n📊 精準分析 ElevenLabs Scribe V1")
    try:
        with open("elevenlabs_scribe_v1_result.json", "r", encoding="utf-8") as f:
            elevenlabs_data = json.load(f)
        
        transcript_text, words = analyze_service_capabilities(elevenlabs_data, "ElevenLabs")
        
        # 創建最佳 SRT
        srt_content, segments = create_precise_srt_from_words(words, "ElevenLabs", target_chars=18)
        
        with open("elevenlabs_precise_18chars.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"💾 精準 SRT 已保存: elevenlabs_precise_18chars.srt")
        
        # 精確評估
        analysis = precise_quality_comparison(transcript_text, segments, "ElevenLabs Scribe")
        results.append(('ElevenLabs Scribe', analysis))
        
    except Exception as e:
        print(f"❌ ElevenLabs 分析失敗: {str(e)}")
    
    # 2. 精準分析 AssemblyAI (修復解析)
    print(f"\n📊 精準分析 AssemblyAI Universal-1 (修復版)")
    try:
        with open("assemblyai_chinese_result.json", "r", encoding="utf-8") as f:
            assemblyai_data = json.load(f)
        
        transcript_text, words = analyze_service_capabilities(assemblyai_data, "AssemblyAI")
        
        # 創建最佳 SRT (修復版)
        srt_content, segments = create_precise_srt_from_words(words, "AssemblyAI", target_chars=18)
        
        with open("assemblyai_precise_18chars.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"💾 精準 SRT 已保存: assemblyai_precise_18chars.srt")
        
        # 精確評估
        analysis = precise_quality_comparison(transcript_text, segments, "AssemblyAI Universal-1")
        results.append(('AssemblyAI Universal-1', analysis))
        
    except Exception as e:
        print(f"❌ AssemblyAI 分析失敗: {str(e)}")
    
    # 3. 最終精準比較
    print(f"\n" + "=" * 80)
    print(f"🏆 精準比較結果 - 詞彙級能力公平對決")
    print("=" * 80)
    
    # 重新評估 Groq 最佳方案 (公平評分)
    groq_best_score = 60 + 25.2  # 段落控制60 + 轉錄品質25.2 (去除繁體優勢)
    
    print(f"📊 基準比較:")
    print(f"  Groq + Prompt + 詞彙級 (重新評分): {groq_best_score:.1f}/100")
    print(f"    段落控制: 60/60 (18字符)")
    print(f"    轉錄準確度: 25.2/40 (7個標點符號 + 3個術語)")
    
    if results:
        print(f"\n📈 新服務詞彙級能力排名:")
        
        # 按評分排序
        results.sort(key=lambda x: x[1]['total_score'], reverse=True)
        
        for i, (service_name, analysis) in enumerate(results, 1):
            print(f"\n  {i}. {service_name}: {analysis['total_score']:.1f}/100")
            print(f"     段落控制: {analysis['segment_score']}/60 (最長 {analysis['max_length']} 字符)")
            print(f"     轉錄準確度: {analysis['accuracy_score']:.1f}/40")
            print(f"     理想段落: {analysis['ideal_count']} 個")
            print(f"     問題段落: {analysis['problem_count']} 個")
            print(f"     專業術語: {analysis['terms_found']}/4 個")
            print(f"     標點符號: {analysis['punctuation_count']} 個")
            
            # 與 Groq 比較
            score_diff = analysis['total_score'] - groq_best_score
            if score_diff > 5:
                print(f"     🎉 比 Groq 最佳方案好 {score_diff:.1f} 分！")
            elif score_diff > 0:
                print(f"     ✅ 比 Groq 最佳方案略好 (+{score_diff:.1f})")
            elif score_diff > -5:
                print(f"     ⚠️ 接近 Groq 最佳方案 ({score_diff:.1f})")
            else:
                print(f"     ❌ 不如 Groq 最佳方案 ({score_diff:.1f})")
        
        # 最終結論
        best_service = results[0]
        if best_service[1]['total_score'] > groq_best_score:
            print(f"\n🎉 確認發現更好的方案！")
            print(f"🏆 新的詞彙級冠軍: {best_service[0]}")
            print(f"   評分: {best_service[1]['total_score']:.1f}/100")
            print(f"   優勢: 比 Groq 好 {best_service[1]['total_score'] - groq_best_score:.1f} 分")
        else:
            print(f"\n📊 結論: Groq 最佳方案仍然領先")
    
    print(f"\n🎉 精準詞彙級測試完成！")
    return results

if __name__ == "__main__":
    main()
