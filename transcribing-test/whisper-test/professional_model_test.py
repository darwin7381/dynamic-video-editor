#!/usr/bin/env python3
"""
專業語音轉文字模型測試
使用針對性的 Prompt 解決 SRT 段落過長問題
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

def analyze_srt_readability(srt_content, model_name):
    """實際分析 SRT 的可讀性和字幕品質"""
    print(f"\n📖 {model_name} - 字幕可讀性分析")
    print("=" * 60)
    
    lines = srt_content.strip().split('\n')
    segments = []
    current_segment = {"id": None, "time": None, "text": ""}
    
    for line in lines:
        if line.strip().isdigit():
            if current_segment["text"]:
                segments.append(current_segment.copy())
            current_segment = {"id": int(line), "time": None, "text": ""}
        elif "-->" in line:
            current_segment["time"] = line.strip()
        elif line.strip():
            current_segment["text"] += line + " "
    
    if current_segment["text"]:
        segments.append(current_segment)
    
    # 實際內容分析
    print(f"📊 字幕統計:")
    print(f"  總段落數: {len(segments)}")
    
    segment_lengths = [len(seg["text"].strip()) for seg in segments]
    avg_length = sum(segment_lengths) / len(segment_lengths)
    max_length = max(segment_lengths)
    min_length = min(segment_lengths)
    
    print(f"  平均段落長度: {avg_length:.1f} 字符")
    print(f"  最長段落: {max_length} 字符")
    print(f"  最短段落: {min_length} 字符")
    
    # 字幕可讀性評估
    ideal_segments = [s for s in segment_lengths if 15 <= s <= 35]  # 理想的字幕長度
    too_short = [s for s in segment_lengths if s < 10]
    too_long = [s for s in segment_lengths if s > 40]
    
    print(f"\n📈 字幕可讀性評估:")
    print(f"  理想長度 (15-35字符): {len(ideal_segments)} 個 ({len(ideal_segments)/len(segments)*100:.1f}%)")
    print(f"  過短 (<10字符): {len(too_short)} 個 ({len(too_short)/len(segments)*100:.1f}%)")
    print(f"  過長 (>40字符): {len(too_long)} 個 ({len(too_long)/len(segments)*100:.1f}%)")
    
    # 分析語義完整性
    complete_sentences = 0
    has_punctuation = 0
    
    print(f"\n📝 語義品質分析:")
    print(f"實際字幕內容示例:")
    
    for i, seg in enumerate(segments[:8]):  # 分析前8個段落
        text = seg["text"].strip()
        time_info = seg["time"]
        
        # 檢查完整性和標點符號
        is_complete = text.endswith(('。', '！', '？', '.', '!', '?', '，', ','))
        has_punct = any(p in text for p in ['，', '。', '！', '？', ',', '.', '!', '?', '、'])
        
        if is_complete:
            complete_sentences += 1
        if has_punct:
            has_punctuation += 1
        
        # 評估這個段落的品質
        length_score = "✅" if 15 <= len(text) <= 35 else "⚠️" if len(text) > 40 else "🔸"
        complete_score = "✅" if is_complete else "❌"
        punct_score = "✅" if has_punct else "❌"
        
        print(f"  {i+1}. [{time_info}] ({len(text)}字符) {length_score}")
        print(f"     內容: {text}")
        print(f"     完整性: {complete_score} | 標點: {punct_score}")
        print()
    
    completion_rate = complete_sentences / len(segments) * 100
    punctuation_rate = has_punctuation / len(segments) * 100
    
    print(f"📊 整體品質指標:")
    print(f"  語義完整度: {completion_rate:.1f}% ({complete_sentences}/{len(segments)})")
    print(f"  標點符號率: {punctuation_rate:.1f}% ({has_punctuation}/{len(segments)})")
    
    # 字幕顯示適用性評估
    readability_score = (len(ideal_segments)/len(segments) * 0.4 + 
                        completion_rate/100 * 0.3 + 
                        punctuation_rate/100 * 0.3)
    
    print(f"  字幕可讀性評分: {readability_score*100:.1f}/100")
    
    if readability_score > 0.8:
        quality_level = "🏆 優秀"
    elif readability_score > 0.6:
        quality_level = "✅ 良好"
    elif readability_score > 0.4:
        quality_level = "⚠️ 一般"
    else:
        quality_level = "❌ 需改善"
    
    print(f"  整體評級: {quality_level}")
    
    return {
        'total_segments': len(segments),
        'avg_length': avg_length,
        'max_length': max_length,
        'min_length': min_length,
        'ideal_segments': len(ideal_segments),
        'too_short': len(too_short),
        'too_long': len(too_long),
        'completion_rate': completion_rate,
        'punctuation_rate': punctuation_rate,
        'readability_score': readability_score * 100,
        'quality_level': quality_level
    }

def test_model_with_professional_prompt(client, model, audio_file, base_url=None):
    """使用專業 Prompt 測試模型"""
    
    if base_url:
        client = OpenAI(api_key=client.api_key, base_url=base_url)
    
    # 針對您的問題設計的專業 Prompt
    professional_prompt = """請將語音轉錄為適合字幕顯示的格式。每個字幕段落應該：
1. 長度控制在 20-35 個字符之間
2. 在語義完整的地方自然斷句
3. 避免在詞彙中間斷開
4. 保持時間同步的準確性
5. 添加適當的標點符號
這是一段財經新聞內容，包含股市、公司名稱等專業術語。"""
    
    results = []
    
    # 測試不同的配置
    test_configs = [
        ("無 Prompt", "", None),
        ("專業字幕 Prompt", professional_prompt, None),
        ("段落級時間戳記", professional_prompt, ["segment"]),
        ("詞彙級時間戳記", professional_prompt, ["word"]),
        ("段落+詞彙級", professional_prompt, ["segment", "word"])
    ]
    
    for config_name, prompt, timestamp_granularities in test_configs:
        print(f"\n--- 測試配置: {config_name} ---")
        
        try:
            start_time = time.time()
            
            # 構建 API 參數
            params = {
                "model": model,
                "file": open(audio_file, "rb"),
                "language": "zh"
            }
            
            # 添加 prompt
            if prompt:
                params["prompt"] = prompt
            
            # 根據模型決定格式和時間戳記
            if "gpt-4o" in model:
                params["response_format"] = "verbose_json"  # 嘗試 verbose_json
                if timestamp_granularities:
                    params["timestamp_granularities"] = timestamp_granularities
            elif model == "whisper-1":
                params["response_format"] = "verbose_json"
                if timestamp_granularities:
                    params["timestamp_granularities"] = timestamp_granularities
            elif "whisper-large-v3" in model:
                params["response_format"] = "verbose_json"
            
            transcription = client.audio.transcriptions.create(**params)
            
            processing_time = time.time() - start_time
            
            print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
            
            # 分析結果
            text = transcription.text if hasattr(transcription, 'text') else str(transcription)
            print(f"📝 文字長度: {len(text)} 字符")
            print(f"🌍 檢測語言: {transcription.language if hasattr(transcription, 'language') else 'N/A'}")
            
            # 檢查時間戳記支援
            has_segments = hasattr(transcription, 'segments') and transcription.segments
            has_words = hasattr(transcription, 'words') and transcription.words
            
            if has_segments:
                print(f"📊 段落數: {len(transcription.segments)}")
            if has_words:
                print(f"📝 詞彙數: {len(transcription.words)}")
            
            # 創建 SRT (如果有段落資訊)
            srt_content = None
            if has_segments:
                srt_content = create_srt_from_segments(transcription.segments)
                
                # 保存 SRT
                filename = f"{model.replace('-', '_').replace('/', '_')}_{config_name.replace(' ', '_').replace('+', '_')}.srt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                print(f"💾 SRT 已保存: {filename}")
            
            # 顯示文字品質
            print(f"📖 文字品質預覽:")
            print(f"  {text[:150]}...")
            
            results.append({
                'model': model,
                'config': config_name,
                'prompt': prompt,
                'timestamp_granularities': timestamp_granularities,
                'success': True,
                'processing_time': processing_time,
                'text': text,
                'has_segments': has_segments,
                'has_words': has_words,
                'segment_count': len(transcription.segments) if has_segments else 0,
                'word_count': len(transcription.words) if has_words else 0,
                'srt_content': srt_content
            })
            
        except Exception as e:
            print(f"❌ 失敗 - 錯誤: {str(e)}")
            results.append({
                'model': model,
                'config': config_name,
                'success': False,
                'error': str(e)
            })
        
        time.sleep(1)  # 避免 API 限制
    
    return results

def main():
    """主測試函數"""
    print("🎯 專業語音轉文字模型測試 - 解決 SRT 段落過長問題")
    print("=" * 80)
    
    # API 金鑰
    openai_api_key = os.getenv("OPENAI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    # 初始化客戶端
    openai_client = OpenAI(api_key=openai_api_key)
    groq_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    
    all_results = []
    
    # 1. 測試 OpenAI whisper-1
    print(f"\n🔍 第一部分：OpenAI Whisper-1 專業測試")
    whisper1_results = test_model_with_professional_prompt(openai_client, "whisper-1", audio_file)
    all_results.extend(whisper1_results)
    
    # 2. 重新測試 OpenAI 新模型 (使用正確的參數)
    print(f"\n🔍 第二部分：OpenAI 新模型專業測試")
    for model in ["gpt-4o-transcribe", "gpt-4o-mini-transcribe"]:
        print(f"\n🚀 測試 {model}")
        model_results = test_model_with_professional_prompt(openai_client, model, audio_file)
        all_results.extend(model_results)
    
    # 3. 測試 Groq Whisper Large v3
    print(f"\n🔍 第三部分：Groq Whisper Large v3 專業測試")
    groq_results = test_model_with_professional_prompt(groq_client, "whisper-large-v3", audio_file, "https://api.groq.com/openai/v1")
    all_results.extend(groq_results)
    
    # 4. 深度分析所有生成的 SRT
    print(f"\n" + "=" * 80)
    print(f"📖 SRT 字幕品質深度分析")
    print("=" * 80)
    
    srt_analyses = {}
    successful_srt_results = [r for r in all_results if r['success'] and r.get('srt_content')]
    
    for result in successful_srt_results:
        analysis_key = f"{result['model']}_{result['config']}"
        analysis = analyze_srt_readability(result['srt_content'], analysis_key)
        srt_analyses[analysis_key] = analysis
        
        # 保存分析結果
        result['srt_analysis'] = analysis
    
    # 5. 綜合比較和推薦
    print(f"\n" + "=" * 80)
    print(f"🏆 綜合比較與推薦")
    print("=" * 80)
    
    if srt_analyses:
        print(f"📊 模型表現排行榜 (按字幕可讀性評分):")
        
        # 按可讀性評分排序
        sorted_analyses = sorted(srt_analyses.items(), key=lambda x: x[1]['readability_score'], reverse=True)
        
        for i, (model_config, analysis) in enumerate(sorted_analyses, 1):
            print(f"  {i}. {model_config}")
            print(f"     可讀性評分: {analysis['readability_score']:.1f}/100 {analysis['quality_level']}")
            print(f"     理想段落比例: {analysis['ideal_segments']}/{analysis['total_segments']} ({analysis['ideal_segments']/analysis['total_segments']*100:.1f}%)")
            print(f"     語義完整度: {analysis['completion_rate']:.1f}%")
            print(f"     標點符號率: {analysis['punctuation_rate']:.1f}%")
            print()
        
        # 找出最佳解決方案
        best_overall = sorted_analyses[0]
        print(f"🏅 最佳整體表現: {best_overall[0]}")
        print(f"   評分: {best_overall[1]['readability_score']:.1f}/100")
        
        # 針對不同需求的推薦
        print(f"\n🎯 針對不同需求的推薦:")
        
        # 最短段落
        shortest_avg = min(srt_analyses.items(), key=lambda x: x[1]['avg_length'])
        print(f"  最短段落: {shortest_avg[0]} (平均 {shortest_avg[1]['avg_length']:.1f} 字符)")
        
        # 最少過長段落
        least_long = min(srt_analyses.items(), key=lambda x: x[1]['too_long'])
        print(f"  最少過長段落: {least_long[0]} ({least_long[1]['too_long']} 個過長段落)")
        
        # 最高完整度
        highest_completion = max(srt_analyses.items(), key=lambda x: x[1]['completion_rate'])
        print(f"  最高語義完整度: {highest_completion[0]} ({highest_completion[1]['completion_rate']:.1f}%)")
    
    # 6. 保存完整結果
    with open("professional_model_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            'test_results': all_results,
            'srt_analyses': srt_analyses
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 完整測試結果已保存到: professional_model_test_results.json")
    print("🎉 專業測試完成！")

if __name__ == "__main__":
    main()
