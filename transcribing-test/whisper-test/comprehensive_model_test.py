#!/usr/bin/env python3
"""
全面測試所有語音轉文字模型的 Prompt 功能和實際效果
包括實際分析 SRT 內容品質和合理性
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

def analyze_srt_content_quality(srt_content, model_name):
    """實際分析 SRT 內容品質和合理性"""
    print(f"\n🔍 {model_name} SRT 內容品質分析")
    print("=" * 50)
    
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
    
    # 分析統計數據
    segment_lengths = [len(seg["text"].strip()) for seg in segments]
    
    print(f"📊 基本統計:")
    print(f"  總段落數: {len(segments)}")
    print(f"  平均段落長度: {sum(segment_lengths) / len(segment_lengths):.1f} 字符")
    print(f"  最長段落: {max(segment_lengths)} 字符")
    print(f"  最短段落: {min(segment_lengths)} 字符")
    
    # 分析段落長度分佈
    short_segments = [s for s in segment_lengths if s <= 10]
    medium_segments = [s for s in segment_lengths if 10 < s <= 25]
    long_segments = [s for s in segment_lengths if s > 25]
    
    print(f"📈 段落長度分佈:")
    print(f"  短段落 (≤10字符): {len(short_segments)} 個 ({len(short_segments)/len(segments)*100:.1f}%)")
    print(f"  中等段落 (11-25字符): {len(medium_segments)} 個 ({len(medium_segments)/len(segments)*100:.1f}%)")
    print(f"  長段落 (>25字符): {len(long_segments)} 個 ({len(long_segments)/len(segments)*100:.1f}%)")
    
    # 分析實際內容品質
    print(f"\n📝 內容品質分析:")
    
    # 檢查前 5 個段落的實際內容
    print(f"前 5 個段落實際內容:")
    for i, seg in enumerate(segments[:5]):
        text = seg["text"].strip()
        time_info = seg["time"]
        
        # 分析這個段落的合理性
        is_complete = text.endswith(('。', '！', '？', '.', '!', '?'))
        has_punctuation = any(p in text for p in ['，', '。', '！', '？', ',', '.', '!', '?'])
        
        print(f"  {i+1}. [{time_info}] ({len(text)}字符)")
        print(f"     內容: {text}")
        print(f"     完整性: {'✅ 完整句子' if is_complete else '❌ 不完整'}")
        print(f"     標點符號: {'✅ 有標點' if has_punctuation else '❌ 無標點'}")
        print()
    
    # 檢查是否有異常長的段落
    if long_segments:
        print(f"⚠️ 發現 {len(long_segments)} 個過長段落:")
        for i, seg in enumerate(segments):
            if len(seg["text"].strip()) > 25:
                text = seg["text"].strip()
                print(f"  段落 {seg['id']}: {len(text)} 字符")
                print(f"    內容: {text[:100]}{'...' if len(text) > 100 else ''}")
    
    return {
        'total_segments': len(segments),
        'avg_length': sum(segment_lengths) / len(segment_lengths),
        'max_length': max(segment_lengths),
        'min_length': min(segment_lengths),
        'short_segments': len(short_segments),
        'medium_segments': len(medium_segments),
        'long_segments': len(long_segments),
        'segments': segments[:5]  # 保存前 5 個段落用於比較
    }

def test_model_with_prompts(client, model, audio_file, prompts_to_test):
    """測試模型的 Prompt 功能"""
    print(f"\n🚀 測試 {model} 的 Prompt 功能")
    print("=" * 60)
    
    results = []
    
    for prompt_name, prompt_text in prompts_to_test:
        print(f"\n--- 測試 Prompt: {prompt_name} ---")
        print(f"Prompt 內容: {prompt_text}")
        
        try:
            start_time = time.time()
            
            # 根據模型類型調整參數
            params = {
                "model": model,
                "file": open(audio_file, "rb"),
                "language": "zh"
            }
            
            # 添加 prompt 參數
            if prompt_text:
                params["prompt"] = prompt_text
            
            # 根據模型決定格式
            if "gpt-4o" in model:
                params["response_format"] = "json"
            elif model == "whisper-1":
                params["response_format"] = "verbose_json"
                params["timestamp_granularities"] = ["segment", "word"]
            
            transcription = client.audio.transcriptions.create(**params)
            
            processing_time = time.time() - start_time
            
            print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
            
            # 獲取文字結果
            if hasattr(transcription, 'text'):
                text = transcription.text
            else:
                text = str(transcription)
            
            print(f"📝 文字長度: {len(text)} 字符")
            print(f"文字預覽: {text[:200]}...")
            
            # 如果有段落資訊，創建 SRT
            srt_content = None
            if hasattr(transcription, 'segments') and transcription.segments:
                print(f"📊 段落數: {len(transcription.segments)}")
                srt_content = create_srt_from_segments(transcription.segments)
                
                # 保存 SRT 文件
                filename = f"{model.replace('-', '_')}_{prompt_name.replace(' ', '_').lower()}.srt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                print(f"💾 SRT 已保存: {filename}")
            
            # 檢查詞彙級時間戳記
            word_count = 0
            if hasattr(transcription, 'words') and transcription.words:
                word_count = len(transcription.words)
                print(f"📝 詞彙級時間戳記: {word_count} 個詞彙")
            
            results.append({
                'model': model,
                'prompt_name': prompt_name,
                'prompt_text': prompt_text,
                'success': True,
                'processing_time': processing_time,
                'text': text,
                'text_length': len(text),
                'segment_count': len(transcription.segments) if hasattr(transcription, 'segments') and transcription.segments else 0,
                'word_count': word_count,
                'srt_content': srt_content
            })
            
        except Exception as e:
            print(f"❌ 失敗 - 錯誤: {str(e)}")
            results.append({
                'model': model,
                'prompt_name': prompt_name,
                'prompt_text': prompt_text,
                'success': False,
                'error': str(e)
            })
        
        time.sleep(1)  # 避免 API 限制
    
    return results

def test_groq_model(groq_client, audio_file, prompts_to_test):
    """測試 Groq Whisper Large v3"""
    print(f"\n🚀 測試 Groq Whisper Large v3 的 Prompt 功能")
    print("=" * 60)
    
    results = []
    
    for prompt_name, prompt_text in prompts_to_test:
        print(f"\n--- 測試 Prompt: {prompt_name} ---")
        print(f"Prompt 內容: {prompt_text}")
        
        try:
            start_time = time.time()
            
            params = {
                "model": "whisper-large-v3",
                "file": open(audio_file, "rb"),
                "response_format": "verbose_json",
                "language": "zh"
            }
            
            # 添加 prompt 參數
            if prompt_text:
                params["prompt"] = prompt_text
            
            transcription = groq_client.audio.transcriptions.create(**params)
            
            processing_time = time.time() - start_time
            
            print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
            print(f"📝 文字長度: {len(transcription.text)} 字符")
            print(f"文字預覽: {transcription.text[:200]}...")
            
            srt_content = None
            if transcription.segments:
                print(f"📊 段落數: {len(transcription.segments)}")
                srt_content = create_srt_from_segments(transcription.segments)
                
                # 保存 SRT 文件
                filename = f"groq_whisper_large_v3_{prompt_name.replace(' ', '_').lower()}.srt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                print(f"💾 SRT 已保存: {filename}")
            
            results.append({
                'model': 'groq-whisper-large-v3',
                'prompt_name': prompt_name,
                'prompt_text': prompt_text,
                'success': True,
                'processing_time': processing_time,
                'text': transcription.text,
                'text_length': len(transcription.text),
                'segment_count': len(transcription.segments) if transcription.segments else 0,
                'word_count': 0,  # Groq 不支援詞彙級
                'srt_content': srt_content
            })
            
        except Exception as e:
            print(f"❌ 失敗 - 錯誤: {str(e)}")
            results.append({
                'model': 'groq-whisper-large-v3',
                'prompt_name': prompt_name,
                'prompt_text': prompt_text,
                'success': False,
                'error': str(e)
            })
        
        time.sleep(1)
    
    return results

def main():
    """主測試函數"""
    print("🎯 全面語音轉文字模型測試 - 包含 Prompt 功能和品質分析")
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
    
    # 定義要測試的 Prompts
    prompts_to_test = [
        ("無 Prompt", ""),
        ("財經新聞", "以下是關於股市和金融市場的財經新聞報導。包含股票、匯率、經濟數據等專業術語。"),
        ("標點符號增強", "請正確添加標點符號，包括逗號、句號、問號和感嘆號。文字應該有適當的停頓和語調標記。"),
        ("專業術語", "這是一段包含 NVIDIA、台積電、ADR、那斯達克、比特幣等專業金融術語的內容。"),
        ("完整句子", "請將轉錄結果組織成完整的句子，每個句子都應該有明確的開始和結束。避免過長的句子。")
    ]
    
    # 測試所有模型
    all_results = []
    
    # 1. 測試 OpenAI whisper-1
    print(f"\n🔍 第一部分：OpenAI Whisper-1 測試")
    whisper1_results = test_model_with_prompts(openai_client, "whisper-1", audio_file, prompts_to_test)
    all_results.extend(whisper1_results)
    
    # 2. 測試 OpenAI 新模型
    print(f"\n🔍 第二部分：OpenAI 新模型測試")
    for model in ["gpt-4o-transcribe", "gpt-4o-mini-transcribe"]:
        model_results = test_model_with_prompts(openai_client, model, audio_file, prompts_to_test)
        all_results.extend(model_results)
    
    # 3. 測試 Groq Whisper Large v3
    print(f"\n🔍 第三部分：Groq Whisper Large v3 測試")
    groq_results = test_groq_model(groq_client, audio_file, prompts_to_test)
    all_results.extend(groq_results)
    
    # 4. 分析所有成功的 SRT 結果
    print(f"\n" + "=" * 80)
    print(f"📊 SRT 內容品質深度分析")
    print("=" * 80)
    
    srt_analyses = {}
    successful_results = [r for r in all_results if r['success'] and r.get('srt_content')]
    
    for result in successful_results:
        model_prompt = f"{result['model']}_{result['prompt_name']}"
        if result['srt_content']:
            analysis = analyze_srt_content_quality(result['srt_content'], model_prompt)
            srt_analyses[model_prompt] = analysis
    
    # 5. 比較分析
    if srt_analyses:
        print(f"\n" + "=" * 80)
        print(f"🏆 模型和 Prompt 效果比較")
        print("=" * 80)
        
        print(f"📈 段落長度比較:")
        for model_prompt, analysis in srt_analyses.items():
            print(f"  {model_prompt}:")
            print(f"    平均長度: {analysis['avg_length']:.1f} 字符")
            print(f"    最長段落: {analysis['max_length']} 字符") 
            print(f"    長段落比例: {analysis['long_segments']}/{analysis['total_segments']} ({analysis['long_segments']/analysis['total_segments']*100:.1f}%)")
            print()
        
        # 找出最佳表現
        best_avg = min(srt_analyses.items(), key=lambda x: x[1]['avg_length'])
        best_long_ratio = min(srt_analyses.items(), key=lambda x: x[1]['long_segments']/x[1]['total_segments'])
        
        print(f"🏅 最佳表現:")
        print(f"  最短平均段落: {best_avg[0]} ({best_avg[1]['avg_length']:.1f} 字符)")
        print(f"  最少長段落: {best_long_ratio[0]} ({best_long_ratio[1]['long_segments']}/{best_long_ratio[1]['total_segments']} = {best_long_ratio[1]['long_segments']/best_long_ratio[1]['total_segments']*100:.1f}%)")
    
    # 6. 保存完整結果
    with open("comprehensive_model_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            'test_results': all_results,
            'srt_analyses': srt_analyses
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 完整測試結果已保存到: comprehensive_model_test_results.json")
    print("🎉 測試完成！")

if __name__ == "__main__":
    main()
