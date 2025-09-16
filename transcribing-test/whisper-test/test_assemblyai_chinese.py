#!/usr/bin/env python3
"""
測試 AssemblyAI 的中文支援 (去除不支援的功能)
"""

import os
from dotenv import load_dotenv
import time
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
    """從段落資訊創建 SRT"""
    srt_content = []
    
    for i, segment in enumerate(segments, 1):
        start_time = format_srt_time(segment['start'])
        end_time = format_srt_time(segment['end'])
        text = segment['text'].strip()
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(text)
        srt_content.append("")
    
    return "\n".join(srt_content)

def analyze_srt_vs_best_solution(srt_content, service_name):
    """與最佳方案比較分析"""
    print(f"\n📺 {service_name} SRT 分析 vs 最佳方案")
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
    print(f"  總段落數: {len(segments)}")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  平均長度: {sum(lengths)/len(lengths):.1f} 字符")
    print(f"  問題段落 (>30字符): {len(problem_segments)} 個")
    print(f"  嚴重問題 (>40字符): {len(very_long_segments)} 個")
    
    # 顯示前10個段落
    print(f"\n📋 前10個段落內容:")
    for seg in segments[:10]:
        status = "🚨" if seg['length'] > 40 else "⚠️" if seg['length'] > 30 else "✅" if 15 <= seg['length'] <= 25 else "🔸"
        print(f"  {seg['id']:2d}. ({seg['length']:2d}字符) {status} {seg['text']}")
    
    # 轉錄品質檢查
    has_traditional = any(char in full_text for char in ['台積電', '聯電', '連準會', '納斯達克'])
    punctuation_count = full_text.count('，') + full_text.count('。') + full_text.count('！') + full_text.count('？')
    
    print(f"\n📝 轉錄品質:")
    print(f"  語言: {'繁體中文 ✅' if has_traditional else '簡體中文 ❌'}")
    print(f"  標點符號: {punctuation_count} 個")
    
    # 與最佳方案比較 (Groq + Prompt + 詞彙級: 95.2分)
    print(f"\n🏆 與最佳方案比較 (Groq 95.2分):")
    print(f"  {service_name} 最長段落: {max(lengths)} vs 18 (最佳)")
    print(f"  {service_name} 問題段落: {len(problem_segments)} vs 0 (最佳)")
    print(f"  {service_name} 繁體中文: {'✅' if has_traditional else '❌'} vs ✅ (最佳)")
    print(f"  {service_name} 標點符號: {punctuation_count} vs 7 (最佳)")
    
    # 判斷是否更好
    is_better = (max(lengths) <= 18 and 
                len(problem_segments) == 0 and 
                has_traditional and 
                punctuation_count >= 7)
    
    if is_better:
        print(f"  🎉 {service_name} 可能比最佳方案更好！")
    elif max(lengths) <= 18 and len(problem_segments) == 0:
        print(f"  ✅ {service_name} 在段落控制上與最佳方案相當")
    else:
        print(f"  ❌ {service_name} 不如最佳方案")
    
    return {
        'total_segments': len(segments),
        'max_length': max(lengths),
        'problem_count': len(problem_segments),
        'very_long_count': len(very_long_segments),
        'has_traditional': has_traditional,
        'punctuation_count': punctuation_count,
        'is_better': is_better,
        'segments': segments
    }

def main():
    """測試 AssemblyAI 中文支援"""
    print("🎯 AssemblyAI 中文語音轉文字測試")
    print("=" * 80)
    
    assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    try:
        # 上傳音檔
        print("📤 上傳音檔...")
        with open(audio_file, 'rb') as f:
            upload_response = requests.post(
                'https://api.assemblyai.com/v2/upload',
                headers={'authorization': assemblyai_api_key},
                files={'file': f}
            )
        
        if upload_response.status_code != 200:
            print(f"❌ 上傳失敗: {upload_response.text}")
            return
        
        upload_url = upload_response.json()['upload_url']
        print(f"✅ 上傳成功")
        
        # 提交轉錄任務 (只使用中文支援的功能)
        print("🔄 提交中文轉錄任務...")
        
        transcription_request = {
            'audio_url': upload_url,
            'language_code': 'zh',
            'speaker_labels': True,      # 多人辨識
            'punctuate': True,          # 標點符號
            'format_text': True         # 格式化文字
        }
        
        headers = {
            'authorization': assemblyai_api_key,
            'content-type': 'application/json'
        }
        
        response = requests.post(
            'https://api.assemblyai.com/v2/transcript',
            headers=headers,
            json=transcription_request
        )
        
        if response.status_code != 200:
            print(f"❌ 提交失敗: {response.text}")
            return
        
        transcript_id = response.json()['id']
        print(f"✅ 任務提交成功: {transcript_id}")
        
        # 等待完成
        print("⏳ 等待轉錄完成...")
        max_wait = 120
        waited = 0
        
        while waited < max_wait:
            response = requests.get(
                f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
                headers=headers
            )
            
            result = response.json()
            status = result['status']
            
            print(f"📊 狀態: {status} (等待 {waited}s)")
            
            if status == 'completed':
                print(f"✅ AssemblyAI 轉錄完成")
                
                # 保存完整結果
                with open("assemblyai_chinese_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                # 創建 SRT
                if 'segments' in result and result['segments']:
                    segments = []
                    for seg in result['segments']:
                        segments.append({
                            'start': seg['start'] / 1000,
                            'end': seg['end'] / 1000,
                            'text': seg['text']
                        })
                    
                    srt_content = create_srt_from_segments(segments)
                    
                    with open("assemblyai_chinese.srt", "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    print(f"💾 SRT 已保存: assemblyai_chinese.srt")
                    
                    # 詳細分析
                    analysis = analyze_srt_vs_best_solution(srt_content, "AssemblyAI")
                    
                    return analysis
                else:
                    print(f"❌ 沒有段落時間戳記")
                    return None
                
            elif status == 'error':
                print(f"❌ 轉錄失敗: {result.get('error', 'Unknown error')}")
                return None
            else:
                time.sleep(10)
                waited += 10
        
        print(f"❌ 等待超時")
        return None
        
    except Exception as e:
        print(f"❌ AssemblyAI 測試失敗: {str(e)}")
        return None

if __name__ == "__main__":
    main()
