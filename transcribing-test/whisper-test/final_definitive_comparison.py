#!/usr/bin/env python3
"""
最終確定性比較 - 使用正確的 API Key
測試所有最佳方案，包含 Groq 的詞彙級支援
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

def create_custom_srt_from_words(words, max_chars=18):
    """使用詞彙級時間戳記創建自定義 SRT"""
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
            
        # 智能分段
        if (current_subtitle['start'] is None or 
            len(current_subtitle['text'] + word) > max_chars):
            
            if current_subtitle['text']:
                subtitles.append(current_subtitle.copy())
            
            current_subtitle = {
                'start': start_time,
                'end': end_time,
                'text': word
            }
        else:
            current_subtitle['text'] += word
            current_subtitle['end'] = end_time
    
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

def comprehensive_evaluation(srt_content, method_name):
    """全面評估 - 段落長度和轉錄品質"""
    print(f"\n🎯 {method_name} - 全面評估")
    print("=" * 60)
    
    # 解析 SRT
    lines = srt_content.strip().split('\n')
    segments = []
    full_text = ""
    
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
                    full_text += text + " "
        i += 1
    
    if not segments:
        print("❌ 無法解析 SRT")
        return None
    
    lengths = [seg['length'] for seg in segments]
    problem_segments = [seg for seg in segments if seg['length'] > 30]
    very_long_segments = [seg for seg in segments if seg['length'] > 40]
    
    print(f"📊 段落統計:")
    print(f"  總段落: {len(segments)}")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  平均長度: {sum(lengths)/len(lengths):.1f} 字符")
    print(f"  問題段落 (>30字符): {len(problem_segments)} 個")
    print(f"  嚴重問題 (>40字符): {len(very_long_segments)} 個")
    
    # 轉錄品質檢查
    has_traditional = any(char in full_text for char in ['台積電', '聯電', '連準會', '納斯達克'])
    punctuation_count = full_text.count('，') + full_text.count('。') + full_text.count('！') + full_text.count('？')
    
    print(f"\n📝 轉錄品質:")
    print(f"  語言: {'繁體中文 ✅' if has_traditional else '簡體中文 ❌'}")
    print(f"  標點符號: {punctuation_count} 個")
    
    # 專業術語檢查
    terms_correct = 0
    if '台積電' in full_text:
        terms_correct += 1
        print(f"  ✅ 台積電 識別正確")
    elif '台积电' in full_text:
        print(f"  ⚠️ 台积电 (簡體)")
    
    if 'NVIDIA' in full_text or '輝達' in full_text:
        terms_correct += 1
        print(f"  ✅ NVIDIA/輝達 識別正確")
    elif '辉达' in full_text:
        print(f"  ⚠️ 辉达 (簡體)")
    
    if '納斯達克' in full_text:
        terms_correct += 1
        print(f"  ✅ 納斯達克 識別正確")
    elif '那斯达克' in full_text:
        print(f"  ⚠️ 那斯达克 (簡體)")
    
    if '比特幣' in full_text:
        terms_correct += 1
        print(f"  ✅ 比特幣 識別正確")
    elif '比特币' in full_text:
        print(f"  ⚠️ 比特币 (簡體)")
    
    print(f"  專業術語正確率: {terms_correct}/4 個")
    
    # 綜合評分
    segment_score = 0
    if max(lengths) <= 19:
        segment_score = 50  # 與 Whisper-1 基準相當或更好
    elif max(lengths) <= 25:
        segment_score = 40
    elif max(lengths) <= 30:
        segment_score = 30
    elif len(very_long_segments) == 0:
        segment_score = 20
    else:
        segment_score = 10
    
    quality_score = 0
    if has_traditional:
        quality_score += 20
    quality_score += min(punctuation_count * 2, 15)
    quality_score += terms_correct * 3.75
    
    total_score = segment_score + quality_score
    
    print(f"\n📈 評分:")
    print(f"  段落控制: {segment_score}/50")
    print(f"  轉錄品質: {quality_score:.1f}/50") 
    print(f"  總評分: {total_score:.1f}/100")
    
    return {
        'total_score': total_score,
        'segment_score': segment_score,
        'quality_score': quality_score,
        'max_length': max(lengths),
        'problem_count': len(problem_segments),
        'very_long_count': len(very_long_segments),
        'has_traditional': has_traditional,
        'punctuation_count': punctuation_count,
        'terms_correct': terms_correct,
        'segments': segments
    }

def main():
    """最終確定性比較"""
    print("🏆 最終確定性比較 - 找到真正最佳解決方案")
    print("=" * 80)
    
    # 正確的 API 設定
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
    
    # 最佳 Prompt
    best_prompt = "美國白宮直接把進口中國商品的關稅，從145%爽拉到245%。中美貿易戰火直接加大馬力。"
    
    # 1. Whisper-1 基準
    print(f"\n📊 測試 1: Whisper-1 基準")
    try:
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="srt",
                language="zh"
            )
        
        with open("final_whisper1_baseline_correct.srt", "w", encoding="utf-8") as f:
            f.write(transcription)
        
        analysis = comprehensive_evaluation(transcription, "Whisper-1 基準")
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
        
        with open("final_whisper1_best_prompt_correct.srt", "w", encoding="utf-8") as f:
            f.write(transcription)
        
        analysis = comprehensive_evaluation(transcription, "Whisper-1 + 最佳Prompt")
        results.append(('Whisper-1 + 最佳Prompt', analysis))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 3. Whisper-1 詞彙級自定義
    print(f"\n📊 測試 3: Whisper-1 詞彙級自定義")
    try:
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"],
                language="zh"
            )
        
        print(f"📝 獲得 {len(transcription.words)} 個詞彙時間戳記")
        
        custom_srt = create_custom_srt_from_words(transcription.words, max_chars=18)
        
        with open("final_whisper1_word_level_correct.srt", "w", encoding="utf-8") as f:
            f.write(custom_srt)
        
        analysis = comprehensive_evaluation(custom_srt, "Whisper-1 詞彙級自定義")
        results.append(('Whisper-1 詞彙級自定義', analysis))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 4. Groq 詞彙級自定義 (已確認支援)
    print(f"\n📊 測試 4: Groq 詞彙級自定義")
    try:
        with open(audio_file, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"],
                language="zh"
            )
        
        print(f"📝 獲得 {len(transcription.words)} 個詞彙時間戳記")
        
        custom_srt = create_custom_srt_from_words(transcription.words, max_chars=18)
        
        with open("final_groq_word_level.srt", "w", encoding="utf-8") as f:
            f.write(custom_srt)
        
        analysis = comprehensive_evaluation(custom_srt, "Groq 詞彙級自定義")
        results.append(('Groq 詞彙級自定義', analysis))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 5. Groq + 最佳 Prompt + 詞彙級
    print(f"\n📊 測試 5: Groq + 最佳 Prompt + 詞彙級")
    try:
        with open(audio_file, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"],
                prompt=best_prompt,
                language="zh"
            )
        
        print(f"📝 獲得 {len(transcription.words)} 個詞彙時間戳記")
        
        custom_srt = create_custom_srt_from_words(transcription.words, max_chars=18)
        
        with open("final_groq_prompt_word_level.srt", "w", encoding="utf-8") as f:
            f.write(custom_srt)
        
        analysis = comprehensive_evaluation(custom_srt, "Groq + Prompt + 詞彙級")
        results.append(('Groq + Prompt + 詞彙級', analysis))
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 最終排名和結論
    print(f"\n" + "=" * 80)
    print(f"🏆 最終確定性結果 - 真正比 Whisper-1 更好的方案")
    print("=" * 80)
    
    if results:
        # 按總評分排序
        results.sort(key=lambda x: x[1]['total_score'], reverse=True)
        
        print(f"📊 最終排名:")
        
        whisper1_baseline_score = None
        
        for i, (method, analysis) in enumerate(results, 1):
            print(f"\n  {i}. {method}")
            print(f"     總評分: {analysis['total_score']:.1f}/100")
            print(f"     段落控制: {analysis['segment_score']}/50 (最長 {analysis['max_length']} 字符)")
            print(f"     轉錄品質: {analysis['quality_score']:.1f}/50")
            print(f"     繁體中文: {'✅' if analysis['has_traditional'] else '❌'}")
            print(f"     專業術語: {analysis['terms_correct']}/4")
            
            if method == 'Whisper-1 基準':
                whisper1_baseline_score = analysis['total_score']
            elif whisper1_baseline_score:
                improvement = analysis['total_score'] - whisper1_baseline_score
                if improvement > 5:
                    print(f"     🎉 比 Whisper-1 好 {improvement:.1f} 分！")
                elif improvement > 0:
                    print(f"     ✅ 比 Whisper-1 略好 (+{improvement:.1f})")
                else:
                    print(f"     ❌ 不如 Whisper-1 ({improvement:.1f})")
        
        # 最終推薦
        winner = results[0]
        print(f"\n🏅 最終最佳解決方案: {winner[0]}")
        print(f"   總評分: {winner[1]['total_score']:.1f}/100")
        print(f"   最長段落: {winner[1]['max_length']} 字符")
        print(f"   問題段落: {winner[1]['problem_count']} 個")
        
        if winner[1]['total_score'] > (whisper1_baseline_score or 0):
            print(f"   🎉 確實比 Whisper-1 基準更好！")
        else:
            print(f"   ⚠️ 與 Whisper-1 基準相當或稍差")
    
    print(f"\n🎉 最終確定性比較完成！")
    return results

if __name__ == "__main__":
    main()
