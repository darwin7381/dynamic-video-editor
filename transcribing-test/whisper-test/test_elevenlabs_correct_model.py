#!/usr/bin/env python3
"""
使用正確模型 ID 測試 ElevenLabs Scribe
"""

import os
from dotenv import load_dotenv
import requests
import json

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
    """從段落創建 SRT"""
    srt_content = []
    
    for i, segment in enumerate(segments, 1):
        start_time = format_srt_time(segment['start_time'])
        end_time = format_srt_time(segment['end_time'])
        text = segment['text'].strip()
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(text)
        srt_content.append("")
    
    return "\n".join(srt_content)

def analyze_elevenlabs_result(result, service_name):
    """分析 ElevenLabs 結果"""
    print(f"\n🎯 {service_name} 詳細分析")
    print("=" * 60)
    
    # 檢查結果結構
    print(f"📊 結果結構: {result.keys() if isinstance(result, dict) else type(result)}")
    
    # 獲取轉錄文字
    transcript_text = ""
    if 'transcript' in result:
        transcript_text = result['transcript']
    elif 'text' in result:
        transcript_text = result['text']
    else:
        print(f"❌ 找不到轉錄文字")
        return None
    
    print(f"📝 轉錄文字長度: {len(transcript_text)} 字符")
    print(f"📋 轉錄內容: {transcript_text}")
    
    # 檢查轉錄品質
    has_traditional = any(char in transcript_text for char in ['台積電', '聯電', '連準會', '納斯達克'])
    punctuation_count = transcript_text.count('，') + transcript_text.count('。') + transcript_text.count('！') + transcript_text.count('？')
    
    terms_found = 0
    if '台積電' in transcript_text:
        terms_found += 1
        print(f"  ✅ 台積電 識別正確")
    if 'NVIDIA' in transcript_text or '輝達' in transcript_text:
        terms_found += 1
        print(f"  ✅ NVIDIA/輝達 識別正確")
    if '納斯達克' in transcript_text:
        terms_found += 1
        print(f"  ✅ 納斯達克 識別正確")
    if '比特幣' in transcript_text:
        terms_found += 1
        print(f"  ✅ 比特幣 識別正確")
    
    print(f"\n📝 轉錄品質:")
    print(f"  語言: {'繁體中文 ✅' if has_traditional else '簡體中文 ❌'}")
    print(f"  標點符號: {punctuation_count} 個")
    print(f"  專業術語: {terms_found}/4 個")
    
    # 檢查時間戳記
    if 'segments' in result or 'chunks' in result:
        segments_key = 'segments' if 'segments' in result else 'chunks'
        segments = result[segments_key]
        print(f"📊 時間戳記段落: {len(segments)} 個")
        
        # 創建 SRT
        srt_content = create_srt_from_segments(segments)
        
        with open("elevenlabs_scribe_final.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"💾 SRT 已保存: elevenlabs_scribe_final.srt")
        
        # 分析段落長度
        segment_lengths = [len(seg['text']) for seg in segments]
        problem_count = sum(1 for length in segment_lengths if length > 30)
        
        print(f"\n📊 段落分析:")
        print(f"  最長段落: {max(segment_lengths)} 字符")
        print(f"  平均長度: {sum(segment_lengths)/len(segment_lengths):.1f} 字符")
        print(f"  問題段落 (>30字符): {problem_count} 個")
        
        # 與最佳方案比較
        print(f"\n🏆 與 Groq 最佳方案比較 (95.2分):")
        print(f"  ElevenLabs 最長段落: {max(segment_lengths)} vs 18 (最佳)")
        print(f"  ElevenLabs 問題段落: {problem_count} vs 0 (最佳)")
        
        # 計算評分
        segment_score = 50 if max(segment_lengths) <= 18 and problem_count == 0 else 40 if max(segment_lengths) <= 25 else 30
        quality_score = 0
        if has_traditional:
            quality_score += 20
        quality_score += min(punctuation_count * 2, 15)
        quality_score += terms_found * 3.75
        
        total_score = segment_score + quality_score
        print(f"  ElevenLabs 總評分: {total_score:.1f}/100")
        
        if total_score > 95:
            print(f"  🎉 ElevenLabs 比最佳方案更好！")
        else:
            print(f"  ⚠️ ElevenLabs 不如最佳方案")
        
        return {
            'success': True,
            'transcript_text': transcript_text,
            'srt_content': srt_content,
            'total_score': total_score,
            'max_length': max(segment_lengths),
            'problem_count': problem_count
        }
    else:
        print(f"❌ 沒有時間戳記資訊")
        return {
            'success': True,
            'transcript_text': transcript_text,
            'srt_content': None,
            'total_score': quality_score if 'quality_score' in locals() else 0
        }

def main():
    """測試 ElevenLabs Scribe 正確模型"""
    print("🎯 ElevenLabs Scribe 正確模型測試")
    print("=" * 80)
    
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    # 測試兩個可用的模型
    models_to_test = ["scribe_v1", "scribe_v1_experimental"]
    
    for model_id in models_to_test:
        print(f"\n📊 測試模型: {model_id}")
        
        try:
            url = "https://api.elevenlabs.io/v1/speech-to-text"
            
            headers = {
                "xi-api-key": elevenlabs_api_key
            }
            
            with open(audio_file, 'rb') as f:
                files = {
                    "file": (audio_file, f, "audio/mpeg")
                }
                
                data = {
                    "model_id": model_id
                }
                
                print(f"🔄 提交 {model_id} 轉錄...")
                response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
            
            print(f"📊 回應狀態: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {model_id} 轉錄成功")
                
                # 保存結果
                filename = f"elevenlabs_{model_id}_result.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"💾 結果已保存: {filename}")
                
                # 分析結果
                analysis = analyze_elevenlabs_result(result, f"ElevenLabs {model_id}")
                
                if analysis and analysis['success']:
                    print(f"🎯 {model_id} 最終評分: {analysis.get('total_score', 0):.1f}/100")
                
            else:
                print(f"❌ {model_id} 失敗: {response.text}")
                
        except Exception as e:
            print(f"❌ {model_id} 測試失敗: {str(e)}")
    
    print(f"\n🎉 ElevenLabs 所有模型測試完成！")

if __name__ == "__main__":
    main()
