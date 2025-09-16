#!/usr/bin/env python3
"""
基於正確用法的 OpenAI 語音轉文字模型測試
根據實際測試結果制定的正確使用方法
"""

import os
from dotenv import load_dotenv
import time
import json
from openai import OpenAI

# 載入環境變數
load_dotenv()

def create_custom_srt_from_words(words, max_chars=40, max_duration=3.0):
    """使用詞彙級時間戳記創建自定義 SRT - 這是解決段落過長的關鍵！"""
    if not words:
        return "無詞彙資訊可用"
    
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
        
        # 清理詞彙（去除前後空格）
        word = word.strip()
        if not word:
            continue
            
        # 如果是第一個詞或需要開始新段落
        if (current_subtitle['start'] is None or 
            len(current_subtitle['text'] + word) > max_chars or
            (end_time - current_subtitle['start']) > max_duration):
            
            # 保存當前字幕段落
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
    
    return generate_srt_content(subtitles)

def generate_srt_content(subtitles):
    """生成標準 SRT 格式內容"""
    srt_content = []
    
    for i, subtitle in enumerate(subtitles, 1):
        start_time = format_srt_time(subtitle['start'])
        end_time = format_srt_time(subtitle['end'])
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(subtitle['text'])
        srt_content.append("")  # 空行
    
    return "\n".join(srt_content)

def format_srt_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def analyze_srt_quality(srt_content):
    """分析 SRT 品質"""
    lines = srt_content.strip().split('\n')
    segments = []
    current_text = ""
    
    for line in lines:
        if line.strip().isdigit():
            if current_text:
                segments.append(current_text.strip())
            current_text = ""
        elif "-->" not in line and line.strip():
            current_text += line + " "
    
    if current_text:
        segments.append(current_text.strip())
    
    if segments:
        segment_lengths = [len(seg) for seg in segments]
        return {
            'segment_count': len(segments),
            'avg_length': sum(segment_lengths) / len(segment_lengths),
            'max_length': max(segment_lengths),
            'min_length': min(segment_lengths)
        }
    return None

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print("錯誤: 找不到音檔 test_audio.mp3")
        return
    
    print("🎯 正確用法測試 - 解決 SRT 段落過長問題")
    print("="*60)
    
    results = []
    
    # 1. 測試 Whisper-1 原始 SRT
    print("\n📊 第一部分：Whisper-1 原始 SRT 測試")
    print("-" * 40)
    
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            original_srt = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="srt",
                language="zh"
            )
        
        processing_time = time.time() - start_time
        
        print(f"✅ 原始 SRT 生成成功 - 處理時間: {processing_time:.2f} 秒")
        
        # 分析原始 SRT 品質
        original_quality = analyze_srt_quality(original_srt)
        print(f"原始 SRT 品質:")
        print(f"  段落數: {original_quality['segment_count']}")
        print(f"  平均長度: {original_quality['avg_length']:.1f} 字符")
        print(f"  最長段落: {original_quality['max_length']} 字符")
        print(f"  最短段落: {original_quality['min_length']} 字符")
        
        # 保存原始 SRT
        with open("original_srt.srt", "w", encoding="utf-8") as f:
            f.write(original_srt)
        print("原始 SRT 已保存: original_srt.srt")
        
        results.append({
            'method': 'whisper-1_original_srt',
            'processing_time': processing_time,
            'quality': original_quality,
            'success': True
        })
        
    except Exception as e:
        print(f"❌ 原始 SRT 測試失敗: {str(e)}")
        results.append({
            'method': 'whisper-1_original_srt',
            'success': False,
            'error': str(e)
        })
    
    # 2. 測試 Whisper-1 詞彙級時間戳記 + 自定義 SRT
    print(f"\n🚀 第二部分：Whisper-1 詞彙級時間戳記 + 自定義 SRT")
    print("-" * 40)
    
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            verbose_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"],  # 關鍵！同時獲得段落和詞彙級時間戳記
                language="zh"
            )
        
        processing_time = time.time() - start_time
        
        print(f"✅ 詞彙級時間戳記獲取成功 - 處理時間: {processing_time:.2f} 秒")
        print(f"段落數: {len(verbose_response.segments) if hasattr(verbose_response, 'segments') else 0}")
        print(f"詞彙數: {len(verbose_response.words) if hasattr(verbose_response, 'words') else 0}")
        
        # 使用詞彙級時間戳記創建自定義 SRT
        if hasattr(verbose_response, 'words') and verbose_response.words:
            print("\n創建自定義 SRT (最大 40 字符/段落, 最大 3 秒/段落)...")
            
            custom_srt = create_custom_srt_from_words(
                verbose_response.words,
                max_chars=40,
                max_duration=3.0
            )
            
            # 分析自定義 SRT 品質
            custom_quality = analyze_srt_quality(custom_srt)
            print(f"自定義 SRT 品質:")
            print(f"  段落數: {custom_quality['segment_count']}")
            print(f"  平均長度: {custom_quality['avg_length']:.1f} 字符")
            print(f"  最長段落: {custom_quality['max_length']} 字符")
            print(f"  最短段落: {custom_quality['min_length']} 字符")
            
            # 保存自定義 SRT
            with open("custom_word_level_srt.srt", "w", encoding="utf-8") as f:
                f.write(custom_srt)
            print("自定義 SRT 已保存: custom_word_level_srt.srt")
            
            results.append({
                'method': 'whisper-1_word_level_custom',
                'processing_time': processing_time,
                'quality': custom_quality,
                'success': True
            })
            
        else:
            print("❌ 沒有詞彙級時間戳記資訊")
            results.append({
                'method': 'whisper-1_word_level_custom',
                'success': False,
                'error': '沒有詞彙級時間戳記'
            })
            
    except Exception as e:
        print(f"❌ 詞彙級時間戳記測試失敗: {str(e)}")
        results.append({
            'method': 'whisper-1_word_level_custom',
            'success': False,
            'error': str(e)
        })
    
    # 3. 測試新模型（僅支援 JSON/TEXT 格式）
    print(f"\n⭐ 第三部分：新模型測試 (gpt-4o-transcribe & gpt-4o-mini-transcribe)")
    print("-" * 40)
    
    new_models = [
        ("gpt-4o-transcribe", "最新旗艦模型"),
        ("gpt-4o-mini-transcribe", "快速版本")
    ]
    
    for model, description in new_models:
        print(f"\n測試 {model} ({description})...")
        
        try:
            start_time = time.time()
            
            with open(audio_file, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    model=model,
                    file=f,
                    response_format="json",  # 新模型只支援 json 和 text
                    language="zh"
                )
            
            processing_time = time.time() - start_time
            
            text = transcription.text if hasattr(transcription, 'text') else str(transcription)
            
            print(f"✅ {model} 成功 - 處理時間: {processing_time:.2f} 秒")
            print(f"文字長度: {len(text)} 字符")
            print("文字預覽:")
            print(text[:200] + "..." if len(text) > 200 else text)
            
            # 保存轉錄結果
            filename = f"{model.replace('-', '_')}_transcription.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"轉錄結果已保存: {filename}")
            
            results.append({
                'method': model,
                'processing_time': processing_time,
                'text_length': len(text),
                'success': True
            })
            
        except Exception as e:
            print(f"❌ {model} 測試失敗: {str(e)}")
            results.append({
                'method': model,
                'success': False,
                'error': str(e)
            })
        
        time.sleep(1)  # 避免 API 限制
    
    # 4. 總結報告
    print("\n" + "="*60)
    print("📋 測試結果總結與建議")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"總測試數: {len(results)}")
    print(f"成功: {len(successful)}")
    print(f"失敗: {len(failed)}")
    
    if successful:
        print(f"\n✅ 成功的測試:")
        for result in successful:
            method = result['method']
            time_info = f"{result['processing_time']:.2f}秒"
            
            if 'quality' in result and result['quality']:
                quality = result['quality']
                quality_info = f" | 段落數: {quality['segment_count']}, 平均: {quality['avg_length']:.1f}字符, 最長: {quality['max_length']}字符"
            else:
                quality_info = ""
            
            print(f"  - {method}: {time_info}{quality_info}")
    
    if failed:
        print(f"\n❌ 失敗的測試:")
        for result in failed:
            print(f"  - {result['method']}: {result['error']}")
    
    # 5. 針對您問題的具體建議
    print(f"\n🎯 針對 SRT 段落過長問題的解決方案:")
    
    # 比較原始 SRT 和自定義 SRT
    original_result = next((r for r in results if r['method'] == 'whisper-1_original_srt' and r['success']), None)
    custom_result = next((r for r in results if r['method'] == 'whisper-1_word_level_custom' and r['success']), None)
    
    if original_result and custom_result:
        original_quality = original_result['quality']
        custom_quality = custom_result['quality']
        
        print(f"\n📊 品質比較:")
        print(f"原始 SRT  - 最長段落: {original_quality['max_length']} 字符, 平均: {original_quality['avg_length']:.1f} 字符")
        print(f"自定義 SRT - 最長段落: {custom_quality['max_length']} 字符, 平均: {custom_quality['avg_length']:.1f} 字符")
        
        if custom_quality['max_length'] < original_quality['max_length']:
            print("🎉 自定義 SRT 成功解決了段落過長問題！")
        else:
            print("⚠️  這個音檔的段落長度本身就不算太長，可能需要用其他音檔測試")
    
    print(f"\n💡 最終建議:")
    print(f"1. 如果您的音檔確實有段落過長問題，使用 whisper-1 + timestamp_granularities=['segment', 'word'] + 自定義轉換")
    print(f"2. 新模型 (gpt-4o-transcribe/gpt-4o-mini-transcribe) 轉錄品質更好，但不支援直接 SRT 輸出")
    print(f"3. 可以結合使用：新模型轉錄 + whisper-1 獲取時間戳記 + 自定義 SRT 生成")
    
    # 保存完整結果
    with open("correct_usage_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 完整測試結果已保存到: correct_usage_test_results.json")
    print("🎉 測試完成！")

if __name__ == "__main__":
    main()
