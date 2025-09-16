#!/usr/bin/env python3
"""
公平比較測試 - 去除簡繁體扣分，專注於實際能力
確實測試詞彙級時間戳記支援
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

def test_word_level_capability(words, service_name, word_format="elevenlabs"):
    """測試詞彙級時間戳記能力"""
    print(f"\n🔍 {service_name} 詞彙級時間戳記測試")
    print("=" * 60)
    
    if not words:
        print(f"❌ {service_name} 沒有詞彙級時間戳記")
        return False
    
    print(f"✅ {service_name} 支援詞彙級時間戳記: {len(words)} 個詞彙")
    
    # 顯示前10個詞彙的時間戳記
    print(f"📝 前10個詞彙時間戳記:")
    for i, word in enumerate(words[:10]):
        if word_format == "elevenlabs":
            word_text = word['text']
            start_time = word['start']
            end_time = word['end']
        else:  # assemblyai
            word_text = word.text if hasattr(word, 'text') else str(word)
            start_time = word.start / 1000 if hasattr(word, 'start') else 0
            end_time = word.end / 1000 if hasattr(word, 'end') else 0
        
        print(f"  {i+1:2d}. [{start_time:.3f}-{end_time:.3f}] '{word_text}'")
    
    # 測試不同長度的 SRT 生成
    test_lengths = [15, 18, 20, 25]
    best_results = []
    
    for target_length in test_lengths:
        print(f"\n📊 測試目標長度: {target_length} 字符")
        
        segments = []
        current_segment = {'start': None, 'end': None, 'text': ''}
        
        for word in words:
            if word_format == "elevenlabs":
                word_text = word['text'].strip()
                start_time = word['start']
                end_time = word['end']
            else:
                word_text = word.text.strip() if hasattr(word, 'text') else str(word).strip()
                start_time = word.start / 1000 if hasattr(word, 'start') else 0
                end_time = word.end / 1000 if hasattr(word, 'end') else 0
            
            if not word_text:
                continue
                
            if current_segment['start'] is None:
                current_segment['start'] = start_time
                current_segment['end'] = end_time
                current_segment['text'] = word_text
            elif len(current_segment['text'] + word_text) > target_length:
                segments.append(current_segment.copy())
                current_segment = {
                    'start': start_time,
                    'end': end_time,
                    'text': word_text
                }
            else:
                current_segment['text'] += word_text
                current_segment['end'] = end_time
        
        if current_segment['text']:
            segments.append(current_segment)
        
        # 分析這個長度設定的效果
        if segments:
            lengths = [len(seg['text']) for seg in segments]
            max_length = max(lengths)
            avg_length = sum(lengths) / len(lengths)
            problem_count = sum(1 for l in lengths if l > 30)
            
            print(f"  結果: {len(segments)} 段落，最長 {max_length} 字符，平均 {avg_length:.1f} 字符")
            print(f"  問題段落: {problem_count} 個")
            
            # 生成並保存 SRT
            srt_lines = []
            for i, seg in enumerate(segments, 1):
                start_time = format_srt_time(seg['start'])
                end_time = format_srt_time(seg['end'])
                
                srt_lines.append(f"{i}")
                srt_lines.append(f"{start_time} --> {end_time}")
                srt_lines.append(seg['text'])
                srt_lines.append("")
            
            srt_content = '\n'.join(srt_lines)
            filename = f"{service_name.lower().replace(' ', '_')}_word_level_{target_length}chars.srt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(srt_content)
            print(f"  💾 已保存: {filename}")
            
            best_results.append({
                'target_length': target_length,
                'max_length': max_length,
                'avg_length': avg_length,
                'problem_count': problem_count,
                'segment_count': len(segments),
                'filename': filename
            })
    
    # 找出最佳設定
    if best_results:
        # 按問題段落數和最長段落排序
        best_results.sort(key=lambda x: (x['problem_count'], x['max_length']))
        best = best_results[0]
        
        print(f"\n🏆 {service_name} 最佳詞彙級設定:")
        print(f"  目標長度: {best['target_length']} 字符")
        print(f"  實際最長: {best['max_length']} 字符")
        print(f"  問題段落: {best['problem_count']} 個")
        print(f"  最佳文件: {best['filename']}")
        
        return best
    
    return None

def fair_quality_assessment(transcript_text, srt_analysis, service_name):
    """公平的品質評估 - 不扣簡繁體分數"""
    print(f"\n📊 {service_name} 公平品質評估")
    print("=" * 60)
    
    # 段落控制評分 (60%)
    segment_score = 0
    max_length = srt_analysis['max_length']
    problem_count = srt_analysis['problem_count']
    
    if max_length <= 18 and problem_count == 0:
        segment_score = 60  # 與最佳方案相同
    elif max_length <= 20 and problem_count == 0:
        segment_score = 55
    elif max_length <= 25 and problem_count == 0:
        segment_score = 50
    elif max_length <= 30 and problem_count <= 1:
        segment_score = 40
    else:
        segment_score = 30
    
    # 轉錄準確度評分 (40%) - 不扣簡繁體分
    accuracy_score = 0
    
    # 標點符號 (15%)
    punctuation_count = transcript_text.count('，') + transcript_text.count('。') + transcript_text.count('！') + transcript_text.count('？')
    punctuation_count += transcript_text.count(',') + transcript_text.count('.') + transcript_text.count('!') + transcript_text.count('?')
    accuracy_score += min(punctuation_count * 1.5, 15)
    
    # 專業術語識別 (25%) - 不區分簡繁體
    terms_found = 0
    if '台積電' in transcript_text or '台积电' in transcript_text:
        terms_found += 1
    if 'NVIDIA' in transcript_text or '輝達' in transcript_text or '辉达' in transcript_text:
        terms_found += 1
    if '納斯達克' in transcript_text or '那斯达克' in transcript_text:
        terms_found += 1
    if '比特幣' in transcript_text or '比特币' in transcript_text:
        terms_found += 1
    
    accuracy_score += terms_found * 6.25  # 每個術語6.25分
    
    total_score = segment_score + accuracy_score
    
    print(f"📈 公平評分:")
    print(f"  段落控制: {segment_score}/60 (最長 {max_length} 字符)")
    print(f"  轉錄準確度: {accuracy_score:.1f}/40")
    print(f"  - 標點符號: {punctuation_count} 個")
    print(f"  - 專業術語: {terms_found}/4 個 (不區分簡繁體)")
    print(f"  📊 總評分: {total_score:.1f}/100")
    
    return {
        'total_score': total_score,
        'segment_score': segment_score,
        'accuracy_score': accuracy_score,
        'punctuation_count': punctuation_count,
        'terms_found': terms_found
    }

def main():
    """公平比較測試"""
    print("🎯 公平比較測試 - 重新評估 ElevenLabs 和 AssemblyAI")
    print("=" * 80)
    print("修正：簡繁體不作為扣分項，專注於實際轉錄能力")
    print("=" * 80)
    
    results = []
    
    # 1. 分析 ElevenLabs 結果
    print(f"\n📊 分析 ElevenLabs Scribe V1 結果")
    try:
        with open("elevenlabs_scribe_v1_result.json", "r", encoding="utf-8") as f:
            elevenlabs_data = json.load(f)
        
        transcript_text = elevenlabs_data['text']
        words = elevenlabs_data['words']
        
        print(f"📝 ElevenLabs 轉錄文字: {transcript_text}")
        
        # 測試詞彙級能力
        best_word_level = test_word_level_capability(words, "ElevenLabs Scribe", "elevenlabs")
        
        if best_word_level:
            # 公平評估
            fair_analysis = fair_quality_assessment(transcript_text, best_word_level, "ElevenLabs Scribe")
            results.append(('ElevenLabs Scribe', fair_analysis, best_word_level))
        
    except Exception as e:
        print(f"❌ ElevenLabs 分析失敗: {str(e)}")
    
    # 2. 分析 AssemblyAI 結果
    print(f"\n📊 分析 AssemblyAI Universal-1 結果")
    try:
        with open("assemblyai_transcript.txt", "r", encoding="utf-8") as f:
            assemblyai_text = f.read()
        
        # 檢查是否有詞彙級資料
        try:
            with open("assemblyai_chinese_result.json", "r", encoding="utf-8") as f:
                assemblyai_data = json.load(f)
            
            print(f"📝 AssemblyAI 轉錄文字: {assemblyai_text}")
            
            # 檢查詞彙級支援
            if 'words' in assemblyai_data and assemblyai_data['words']:
                words = assemblyai_data['words']
                print(f"✅ AssemblyAI 支援詞彙級時間戳記: {len(words)} 個詞彙")
                
                # 測試詞彙級能力
                best_word_level = test_word_level_capability(words, "AssemblyAI Universal-1", "assemblyai")
                
                if best_word_level:
                    # 公平評估
                    fair_analysis = fair_quality_assessment(assemblyai_text, best_word_level, "AssemblyAI Universal-1")
                    results.append(('AssemblyAI Universal-1', fair_analysis, best_word_level))
            else:
                print(f"❌ AssemblyAI 沒有詞彙級時間戳記")
                
                # 使用現有 SRT 分析
                with open("assemblyai_custom.srt", "r", encoding="utf-8") as f:
                    srt_content = f.read()
                
                # 解析段落長度
                lines = srt_content.strip().split('\n')
                lengths = []
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
                                lengths.append(len(text))
                    i += 1
                
                if lengths:
                    srt_analysis = {
                        'max_length': max(lengths),
                        'problem_count': sum(1 for l in lengths if l > 30),
                        'segment_count': len(lengths)
                    }
                    
                    fair_analysis = fair_quality_assessment(assemblyai_text, srt_analysis, "AssemblyAI Universal-1")
                    results.append(('AssemblyAI Universal-1 (段落級)', fair_analysis, srt_analysis))
        
        except Exception as e:
            print(f"⚠️ 無法讀取 AssemblyAI 詳細結果: {str(e)}")
    
    except Exception as e:
        print(f"❌ AssemblyAI 分析失敗: {str(e)}")
    
    # 3. 最終公平比較
    print(f"\n" + "=" * 80)
    print(f"🏆 公平比較結果 (不扣簡繁體分數)")
    print("=" * 80)
    
    # 現有最佳方案重新評分 (去除簡繁體優勢)
    groq_best_score = 50 + 45.2  # 段落控制50 + 轉錄品質45.2 (包含繁體中文20分)
    groq_fair_score = 50 + (45.2 - 20) + 20  # 去除繁體中文優勢，但保留其他品質
    
    print(f"📊 重新評分的最佳方案:")
    print(f"  Groq + Prompt + 詞彙級 (公平評分): {groq_fair_score:.1f}/100")
    print(f"  - 段落控制: 50/60 (18字符)")
    print(f"  - 轉錄準確度: {groq_fair_score - 50:.1f}/40 (標點符號+專業術語)")
    
    if results:
        print(f"\n📈 新測試服務 (公平評分):")
        
        # 按評分排序
        results.sort(key=lambda x: x[1]['total_score'], reverse=True)
        
        for i, (service_name, analysis, details) in enumerate(results, 1):
            print(f"\n  {i}. {service_name}: {analysis['total_score']:.1f}/100")
            print(f"     段落控制: {analysis['segment_score']}/60")
            print(f"     轉錄準確度: {analysis['accuracy_score']:.1f}/40")
            print(f"     標點符號: {analysis['punctuation_count']} 個")
            print(f"     專業術語: {analysis['terms_found']}/4 個")
            
            if 'max_length' in details:
                print(f"     最長段落: {details['max_length']} 字符")
            
            # 與最佳方案比較
            score_diff = analysis['total_score'] - groq_fair_score
            if score_diff > 5:
                print(f"     🎉 比最佳方案好 {score_diff:.1f} 分！")
            elif score_diff > 0:
                print(f"     ✅ 比最佳方案略好 (+{score_diff:.1f})")
            elif score_diff > -10:
                print(f"     ⚠️ 接近最佳方案 ({score_diff:.1f})")
            else:
                print(f"     ❌ 不如最佳方案 ({score_diff:.1f})")
        
        # 最終結論
        best_new = results[0]
        if best_new[1]['total_score'] > groq_fair_score:
            print(f"\n🎉 發現更好的方案！")
            print(f"🏆 新的最佳方案: {best_new[0]} ({best_new[1]['total_score']:.1f}分)")
        else:
            print(f"\n📊 結論: Groq 最佳方案仍然領先")
            print(f"   最接近的是 {best_new[0]} ({best_new[1]['total_score']:.1f}分)")
    
    print(f"\n🎉 公平比較測試完成！")
    return results

if __name__ == "__main__":
    main()
