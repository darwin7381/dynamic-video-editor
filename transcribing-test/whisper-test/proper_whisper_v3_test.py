#!/usr/bin/env python3
"""
正確測試 Whisper Large v3 vs Whisper-1 的實際效果比較
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

def analyze_real_srt_quality(srt_content, model_name):
    """實際分析 SRT 品質 - 專注於您的需求"""
    print(f"\n🔍 {model_name} - 實際 SRT 品質分析")
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
    
    print(f"📊 基本統計:")
    print(f"  總段落數: {len(segments)}")
    print(f"  平均長度: {sum(lengths)/len(lengths):.1f} 字符")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  最短段落: {min(lengths)} 字符")
    
    # 按您的標準分類
    too_long_40 = [l for l in lengths if l > 40]  # 嚴重過長
    too_long_30 = [l for l in lengths if l > 30]  # 過長
    ideal = [l for l in lengths if 15 <= l <= 25]  # 理想
    too_short = [l for l in lengths if l < 10]  # 過短
    
    print(f"\n🎯 針對字幕使用的分析:")
    print(f"  理想長度 (15-25字符): {len(ideal)} 個 ({len(ideal)/len(segments)*100:.1f}%)")
    print(f"  過長 (>30字符): {len(too_long_30)} 個 ({len(too_long_30)/len(segments)*100:.1f}%)")
    print(f"  嚴重過長 (>40字符): {len(too_long_40)} 個 ({len(too_long_40)/len(segments)*100:.1f}%)")
    print(f"  過短 (<10字符): {len(too_short)} 個 ({len(too_short)/len(segments)*100:.1f}%)")
    
    # 顯示實際內容
    print(f"\n📺 實際字幕內容檢查:")
    for i, seg in enumerate(segments[:8]):
        length_status = ""
        if seg['length'] > 40:
            length_status = "🚨 嚴重過長"
        elif seg['length'] > 30:
            length_status = "⚠️ 過長"
        elif 15 <= seg['length'] <= 25:
            length_status = "✅ 理想"
        elif seg['length'] < 10:
            length_status = "🔸 過短"
        else:
            length_status = "📏 可接受"
        
        print(f"  {seg['id']}. [{seg['time']}] ({seg['length']}字符) {length_status}")
        print(f"      {seg['text']}")
        print()
    
    # 計算實用性評分
    usability_score = 0
    
    # 沒有嚴重過長段落 (40分)
    if len(too_long_40) == 0:
        usability_score += 40
    elif len(too_long_40) <= 2:
        usability_score += 20
    
    # 理想段落比例 (30分)
    usability_score += (len(ideal) / len(segments)) * 30
    
    # 過長段落控制 (20分)
    if len(too_long_30) == 0:
        usability_score += 20
    elif len(too_long_30) <= 3:
        usability_score += 10
    
    # 過短段落控制 (10分)
    if len(too_short) / len(segments) < 0.2:
        usability_score += 10
    elif len(too_short) / len(segments) < 0.4:
        usability_score += 5
    
    print(f"📈 字幕實用性評分: {usability_score:.1f}/100")
    
    if usability_score >= 80:
        rating = "🏆 優秀"
    elif usability_score >= 60:
        rating = "✅ 良好"
    elif usability_score >= 40:
        rating = "⚠️ 一般"
    else:
        rating = "❌ 不佳"
    
    print(f"🎯 實用性評級: {rating}")
    
    return {
        'total_segments': len(segments),
        'avg_length': sum(lengths)/len(lengths),
        'max_length': max(lengths),
        'min_length': min(lengths),
        'ideal_count': len(ideal),
        'too_long_30_count': len(too_long_30),
        'too_long_40_count': len(too_long_40),
        'too_short_count': len(too_short),
        'usability_score': usability_score,
        'rating': rating,
        'ideal_ratio': len(ideal)/len(segments),
        'too_long_ratio': len(too_long_30)/len(segments)
    }

def main():
    """重新正確測試 Whisper Large v3 vs Whisper-1"""
    print("🎯 重新實測：尋找比 Whisper-1 更好的模型")
    print("=" * 80)
    
    # API 設定
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
    
    results = []
    
    # 1. 測試 OpenAI Whisper-1 基準
    print(f"\n📊 測試 1: OpenAI Whisper-1 (基準)")
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="srt",
                language="zh"
            )
        
        processing_time = time.time() - start_time
        print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
        
        # 保存結果
        with open("whisper1_baseline_final.srt", "w", encoding="utf-8") as f:
            f.write(transcription)
        
        # 分析品質
        analysis = analyze_real_srt_quality(transcription, "OpenAI Whisper-1 基準")
        
        results.append({
            'model': 'OpenAI Whisper-1',
            'config': '基準',
            'processing_time': processing_time,
            'analysis': analysis,
            'srt_content': transcription
        })
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 2. 測試 Groq Whisper Large v3 基準
    print(f"\n📊 測試 2: Groq Whisper Large v3 (基準)")
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
        print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
        print(f"📊 段落數: {len(transcription.segments)}")
        
        # 創建 SRT
        srt_content = create_srt_from_segments(transcription.segments)
        
        # 保存結果
        with open("groq_large_v3_baseline_final.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        # 分析品質
        analysis = analyze_real_srt_quality(srt_content, "Groq Whisper Large v3 基準")
        
        results.append({
            'model': 'Groq Whisper Large v3',
            'config': '基準',
            'processing_time': processing_time,
            'analysis': analysis,
            'srt_content': srt_content
        })
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 3. 測試 Groq Whisper Large v3 + 優化 Prompt
    print(f"\n📊 測試 3: Groq Whisper Large v3 + 優化 Prompt")
    
    optimized_prompt = """財經新聞轉錄。要求：
1. 段落長度 15-25 字符
2. 自然停頓分段
3. 保持語義完整
4. 正確識別：台積電、NVIDIA、ADR、那斯達克、比特幣
5. 適當標點符號"""
    
    try:
        start_time = time.time()
        
        with open(audio_file, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                response_format="verbose_json",
                prompt=optimized_prompt,
                language="zh"
            )
        
        processing_time = time.time() - start_time
        print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
        print(f"📊 段落數: {len(transcription.segments)}")
        
        # 創建 SRT
        srt_content = create_srt_from_segments(transcription.segments)
        
        # 保存結果
        with open("groq_large_v3_optimized_final.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        # 分析品質
        analysis = analyze_real_srt_quality(srt_content, "Groq Whisper Large v3 優化")
        
        results.append({
            'model': 'Groq Whisper Large v3',
            'config': '優化 Prompt',
            'processing_time': processing_time,
            'analysis': analysis,
            'srt_content': srt_content
        })
        
    except Exception as e:
        print(f"❌ 失敗: {str(e)}")
    
    # 4. 最終比較
    print(f"\n" + "=" * 80)
    print(f"🏆 實測結果：哪個模型真的比 Whisper-1 更好？")
    print("=" * 80)
    
    if len(results) >= 2:
        # 找到 Whisper-1 基準
        whisper1_result = next((r for r in results if 'Whisper-1' in r['model']), None)
        other_results = [r for r in results if 'Whisper-1' not in r['model']]
        
        if whisper1_result:
            whisper1_score = whisper1_result['analysis']['usability_score']
            whisper1_time = whisper1_result['processing_time']
            
            print(f"📊 Whisper-1 基準表現:")
            print(f"  實用性評分: {whisper1_score:.1f}/100")
            print(f"  處理速度: {whisper1_time:.2f} 秒")
            print(f"  評級: {whisper1_result['analysis']['rating']}")
            
            print(f"\n🚀 其他模型 vs Whisper-1 比較:")
            
            better_models = []
            
            for result in other_results:
                other_score = result['analysis']['usability_score']
                other_time = result['processing_time']
                
                score_diff = other_score - whisper1_score
                speed_improvement = ((whisper1_time - other_time) / whisper1_time) * 100
                
                print(f"\n  {result['model']} ({result['config']}):")
                print(f"    實用性評分: {other_score:.1f}/100 ({score_diff:+.1f})")
                print(f"    處理速度: {other_time:.2f} 秒 ({speed_improvement:+.1f}%)")
                print(f"    評級: {result['analysis']['rating']}")
                
                if score_diff > 5 or speed_improvement > 50:
                    print(f"    🎉 比 Whisper-1 更好！")
                    better_models.append(result)
                elif score_diff > 0:
                    print(f"    ✅ 略優於 Whisper-1")
                    better_models.append(result)
                else:
                    print(f"    ❌ 不如 Whisper-1")
            
            # 總結
            if better_models:
                print(f"\n🏅 找到 {len(better_models)} 個比 Whisper-1 更好的模型:")
                
                # 按綜合表現排序
                better_models.sort(key=lambda x: x['analysis']['usability_score'], reverse=True)
                
                for i, model in enumerate(better_models, 1):
                    analysis = model['analysis']
                    score_improvement = analysis['usability_score'] - whisper1_score
                    speed_improvement = ((whisper1_time - model['processing_time']) / whisper1_time) * 100
                    
                    print(f"  {i}. {model['model']} ({model['config']})")
                    print(f"     實用性提升: +{score_improvement:.1f} 分")
                    print(f"     速度提升: +{speed_improvement:.1f}%")
                    print(f"     理想段落: {analysis['ideal_count']} 個 ({analysis['ideal_ratio']*100:.1f}%)")
                    print(f"     過長段落: {analysis['too_long_30_count']} 個")
                
                # 最終推薦
                best_model = better_models[0]
                print(f"\n🏆 最佳推薦: {best_model['model']} ({best_model['config']})")
                print(f"   比 Whisper-1 好 {best_model['analysis']['usability_score'] - whisper1_score:.1f} 分")
                print(f"   {best_model['analysis']['rating']}")
                
            else:
                print(f"\n😞 沒有找到比 Whisper-1 更好的模型")
                print(f"   所有測試模型的表現都不如 Whisper-1")
    
    print(f"\n🎉 重新實測完成！")
    return results

if __name__ == "__main__":
    main()
