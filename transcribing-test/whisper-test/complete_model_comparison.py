#!/usr/bin/env python3
"""
完整的語音轉文字模型比較測試
基於正確的 API 文檔資訊
"""

import os
from dotenv import load_dotenv
import time
import json
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

def create_srt_from_words(words, max_chars=25, max_duration=3.0):
    """使用詞彙級時間戳記創建理想長度的 SRT"""
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

def evaluate_srt_quality(srt_content, model_name):
    """評估 SRT 品質 - 專注於解決段落過長問題"""
    print(f"\n🎯 {model_name} - 解決段落過長問題評估")
    print("=" * 60)
    
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
        print("❌ 無法解析 SRT 內容")
        return None
    
    lengths = [seg['length'] for seg in segments]
    
    print(f"📊 段落長度統計:")
    print(f"  總段落數: {len(segments)}")
    print(f"  平均長度: {sum(lengths)/len(lengths):.1f} 字符")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  最短段落: {min(lengths)} 字符")
    
    # 按您的需求分類段落
    perfect_length = [l for l in lengths if 15 <= l <= 30]  # 理想字幕長度
    acceptable_length = [l for l in lengths if 10 <= l <= 40]  # 可接受長度
    too_long = [l for l in lengths if l > 40]  # 過長 (您的主要問題)
    too_short = [l for l in lengths if l < 10]  # 過短
    
    print(f"\n🎯 針對您的問題分析:")
    print(f"  理想長度 (15-30字符): {len(perfect_length)} 個 ({len(perfect_length)/len(segments)*100:.1f}%)")
    print(f"  可接受長度 (10-40字符): {len(acceptable_length)} 個 ({len(acceptable_length)/len(segments)*100:.1f}%)")
    print(f"  🚨 過長段落 (>40字符): {len(too_long)} 個 ({len(too_long)/len(segments)*100:.1f}%)")
    print(f"  過短段落 (<10字符): {len(too_short)} 個 ({len(too_short)/len(segments)*100:.1f}%)")
    
    # 顯示問題段落
    if too_long:
        print(f"\n⚠️ 發現的過長段落 (>40字符):")
        for seg in segments:
            if seg['length'] > 40:
                print(f"  段落 {seg['id']}: {seg['length']} 字符")
                print(f"    時間: {seg['time']}")
                print(f"    內容: {seg['text']}")
                print()
    
    # 問題解決效果評分
    problem_solving_score = 0
    
    # 主要指標：沒有過長段落 (50%)
    if len(too_long) == 0:
        problem_solving_score += 50
    elif len(too_long) <= 2:
        problem_solving_score += 30
    elif len(too_long) <= 5:
        problem_solving_score += 10
    
    # 理想段落比例 (30%)
    problem_solving_score += (len(perfect_length) / len(segments)) * 30
    
    # 可接受段落比例 (20%)
    problem_solving_score += (len(acceptable_length) / len(segments)) * 20
    
    print(f"\n📈 問題解決效果評分: {problem_solving_score:.1f}/100")
    
    if problem_solving_score >= 80:
        rating = "🏆 優秀 - 完美解決您的問題"
    elif problem_solving_score >= 60:
        rating = "✅ 良好 - 大幅改善您的問題"
    elif problem_solving_score >= 40:
        rating = "⚠️ 一般 - 部分解決您的問題"
    else:
        rating = "❌ 不佳 - 未能解決您的問題"
    
    print(f"🎯 整體評級: {rating}")
    
    return {
        'total_segments': len(segments),
        'avg_length': sum(lengths)/len(lengths),
        'max_length': max(lengths),
        'perfect_count': len(perfect_length),
        'acceptable_count': len(acceptable_length),
        'too_long_count': len(too_long),
        'too_short_count': len(too_short),
        'problem_solving_score': problem_solving_score,
        'rating': rating
    }

def test_model_comprehensive(client, model, audio_file, provider="OpenAI"):
    """全面測試單個模型的所有能力"""
    print(f"\n🚀 全面測試 {provider} {model}")
    print("=" * 60)
    
    results = []
    
    # 針對您的問題設計的專業 Prompt
    optimized_prompt = """這是財經新聞內容。請轉錄並優化為字幕格式：
- 每段落 15-30 字符
- 在自然停頓處分段
- 保持語義完整
- 正確識別：台積電、聯電、日月光、NVIDIA、ADR、那斯達克、費半、比特幣
- 使用繁體中文
- 適當標點符號"""
    
    # 測試配置
    test_configs = []
    
    if "gpt-4o" in model:
        # 4o 模型的正確測試方法
        test_configs = [
            ("JSON基本", "json", None, None),
            ("JSON+段落時間戳記", "json", ["segment"], None),
            ("JSON+詞彙時間戳記", "json", ["word"], None), 
            ("JSON+全時間戳記", "json", ["segment", "word"], None),
            ("JSON+專業Prompt", "json", ["segment", "word"], optimized_prompt)
        ]
    elif model == "whisper-1":
        # Whisper-1 的測試方法
        test_configs = [
            ("基準SRT", "srt", None, None),
            ("詳細JSON", "verbose_json", ["segment", "word"], None),
            ("專業Prompt+SRT", "srt", None, optimized_prompt),
            ("專業Prompt+詳細JSON", "verbose_json", ["segment", "word"], optimized_prompt)
        ]
    elif "whisper-large-v3" in model:
        # Groq Whisper Large v3 的測試方法
        test_configs = [
            ("基準", "verbose_json", None, None),
            ("專業Prompt", "verbose_json", None, optimized_prompt)
        ]
    
    for config_name, response_format, timestamp_granularities, prompt in test_configs:
        print(f"\n--- 配置: {config_name} ---")
        
        try:
            start_time = time.time()
            
            # 構建 API 參數
            params = {
                "model": model,
                "file": open(audio_file, "rb"),
                "response_format": response_format,
                "language": "zh"
            }
            
            if prompt:
                params["prompt"] = prompt
                print(f"📝 使用專業 Prompt")
            
            if timestamp_granularities:
                params["timestamp_granularities"] = timestamp_granularities
                print(f"⏱️ 時間戳記粒度: {timestamp_granularities}")
            
            transcription = client.audio.transcriptions.create(**params)
            
            processing_time = time.time() - start_time
            
            print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
            
            # 檢查結果類型
            print(f"📊 回應類型: {type(transcription).__name__}")
            
            # 獲取文字
            if hasattr(transcription, 'text'):
                text = transcription.text
                print(f"📝 文字長度: {len(text)} 字符")
            else:
                text = str(transcription)
                print(f"📝 內容長度: {len(text)} 字符")
            
            # 檢查時間戳記支援
            has_segments = hasattr(transcription, 'segments') and transcription.segments
            has_words = hasattr(transcription, 'words') and transcription.words
            
            segment_count = len(transcription.segments) if has_segments else 0
            word_count = len(transcription.words) if has_words else 0
            
            print(f"📊 段落級時間戳記: {'✅' if has_segments else '❌'} ({segment_count} 個)")
            print(f"📝 詞彙級時間戳記: {'✅' if has_words else '❌'} ({word_count} 個)")
            
            # 創建 SRT
            srt_content = None
            srt_analysis = None
            
            if response_format == "srt":
                srt_content = text
            elif has_segments:
                srt_content = create_srt_from_segments(transcription.segments)
            elif has_words:
                srt_content = create_srt_from_words(transcription.words)
            
            if srt_content:
                # 保存 SRT
                filename = f"{provider.lower()}_{model.replace('-', '_').replace('/', '_')}_{config_name.replace(' ', '_').replace('+', '_')}.srt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                print(f"💾 SRT 已保存: {filename}")
                
                # 評估 SRT 品質
                srt_analysis = evaluate_srt_quality(srt_content, f"{provider} {model} {config_name}")
            
            # 顯示文字品質預覽
            print(f"📖 轉錄品質預覽:")
            print(f"  {text[:200]}...")
            
            results.append({
                'provider': provider,
                'model': model,
                'config': config_name,
                'response_format': response_format,
                'timestamp_granularities': timestamp_granularities,
                'prompt': prompt is not None,
                'success': True,
                'processing_time': processing_time,
                'text': text,
                'has_segments': has_segments,
                'has_words': has_words,
                'segment_count': segment_count,
                'word_count': word_count,
                'srt_content': srt_content,
                'srt_analysis': srt_analysis
            })
            
        except Exception as e:
            print(f"❌ 失敗 - 錯誤: {str(e)}")
            results.append({
                'provider': provider,
                'model': model,
                'config': config_name,
                'success': False,
                'error': str(e)
            })
        
        time.sleep(1)
    
    return results

def main():
    """主測試函數 - 找到比 Whisper-1 更好的模型"""
    print("🎯 完整語音轉文字模型比較 - 尋找比 Whisper-1 更好的解決方案")
    print("=" * 80)
    
    # API 設定
    openai_api_key = os.getenv("OPENAI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    all_results = []
    
    # 1. 測試 OpenAI whisper-1 (基準)
    print(f"\n📊 第一部分：OpenAI Whisper-1 (基準模型)")
    openai_client = OpenAI(api_key=openai_api_key)
    whisper1_results = test_model_comprehensive(openai_client, "whisper-1", audio_file, "OpenAI")
    all_results.extend(whisper1_results)
    
    # 2. 測試 OpenAI 新模型 (正確方法)
    print(f"\n📊 第二部分：OpenAI 新一代模型 (正確測試)")
    for model in ["gpt-4o-transcribe", "gpt-4o-mini-transcribe"]:
        model_results = test_model_comprehensive(openai_client, model, audio_file, "OpenAI")
        all_results.extend(model_results)
    
    # 3. 測試 Groq Whisper Large v3
    print(f"\n📊 第三部分：Groq Whisper Large v3")
    groq_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    groq_results = test_model_comprehensive(groq_client, "whisper-large-v3", audio_file, "Groq")
    all_results.extend(groq_results)
    
    # 4. 分析和排名
    print(f"\n" + "=" * 80)
    print(f"🏆 尋找比 Whisper-1 更好的解決方案")
    print("=" * 80)
    
    # 獲取所有成功且有 SRT 的結果
    srt_results = [r for r in all_results if r['success'] and r.get('srt_analysis')]
    
    if srt_results:
        # 按問題解決效果排序
        srt_results.sort(key=lambda x: x['srt_analysis']['problem_solving_score'], reverse=True)
        
        print(f"📈 解決您問題的效果排行榜:")
        
        whisper1_baseline = None
        
        for i, result in enumerate(srt_results, 1):
            analysis = result['srt_analysis']
            model_info = f"{result['provider']} {result['model']} ({result['config']})"
            
            # 記錄 whisper-1 基準
            if result['model'] == 'whisper-1' and 'baseline' in result['config'].lower():
                whisper1_baseline = analysis
            
            print(f"  {i}. {model_info}")
            print(f"     問題解決度: {analysis['problem_solving_score']:.1f}/100")
            print(f"     過長段落: {analysis['too_long_count']} 個")
            print(f"     理想段落: {analysis['perfect_count']} 個 ({analysis['perfect_count']/analysis['total_segments']*100:.1f}%)")
            print(f"     處理速度: {result['processing_time']:.2f} 秒")
            print(f"     整體評級: {analysis['rating']}")
            
            # 與 whisper-1 比較
            if whisper1_baseline and result['model'] != 'whisper-1':
                improvement = analysis['problem_solving_score'] - whisper1_baseline['problem_solving_score']
                if improvement > 10:
                    print(f"     🎉 比 Whisper-1 改善 {improvement:.1f} 分！")
                elif improvement > 0:
                    print(f"     ✅ 比 Whisper-1 略有改善 (+{improvement:.1f} 分)")
                else:
                    print(f"     ❌ 不如 Whisper-1 ({improvement:.1f} 分)")
            
            print()
        
        # 找出最佳解決方案
        best_solution = srt_results[0]
        print(f"🏅 最佳解決方案: {best_solution['provider']} {best_solution['model']} ({best_solution['config']})")
        print(f"   問題解決度: {best_solution['srt_analysis']['problem_solving_score']:.1f}/100")
        print(f"   {best_solution['srt_analysis']['rating']}")
        
        # 速度冠軍
        fastest = min(srt_results, key=lambda x: x['processing_time'])
        print(f"\n⚡ 速度冠軍: {fastest['provider']} {fastest['model']} - {fastest['processing_time']:.2f} 秒")
    
    # 5. 時間戳記支援總結
    print(f"\n📊 時間戳記支援總結:")
    
    models_with_segments = [r for r in all_results if r['success'] and r['has_segments']]
    models_with_words = [r for r in all_results if r['success'] and r['has_words']]
    
    print(f"支援段落級時間戳記:")
    for result in models_with_segments:
        print(f"  ✅ {result['provider']} {result['model']} ({result['segment_count']} 段落)")
    
    print(f"支援詞彙級時間戳記:")
    for result in models_with_words:
        print(f"  ✅ {result['provider']} {result['model']} ({result['word_count']} 詞彙)")
    
    # 6. 保存完整結果
    with open("complete_model_comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 完整比較結果已保存到: complete_model_comparison_results.json")
    print("🎉 完整測試完成！")

if __name__ == "__main__":
    main()
