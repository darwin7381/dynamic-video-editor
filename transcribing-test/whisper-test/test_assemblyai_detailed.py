#!/usr/bin/env python3
"""
詳細測試 AssemblyAI 的 SRT 生成和段落控制
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

def analyze_assemblyai_srt(srt_content):
    """詳細分析 AssemblyAI 的 SRT 品質"""
    print(f"\n📺 AssemblyAI SRT 詳細分析")
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
    
    print(f"📊 段落統計:")
    print(f"  總段落數: {len(segments)}")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  平均長度: {sum(lengths)/len(lengths):.1f} 字符")
    print(f"  問題段落 (>30字符): {len(problem_segments)} 個")
    
    # 顯示所有段落
    print(f"\n📋 所有段落內容:")
    for seg in segments:
        status = "🚨" if seg['length'] > 40 else "⚠️" if seg['length'] > 30 else "✅" if 15 <= seg['length'] <= 25 else "🔸"
        print(f"  {seg['id']:2d}. ({seg['length']:2d}字符) {status} {seg['text']}")
    
    # 與最佳方案比較
    print(f"\n🏆 與 Groq 最佳方案比較:")
    print(f"  AssemblyAI 最長段落: {max(lengths)} 字符")
    print(f"  Groq 最佳最長段落: 18 字符")
    print(f"  AssemblyAI 問題段落: {len(problem_segments)} 個")
    print(f"  Groq 最佳問題段落: 0 個")
    
    if max(lengths) <= 18 and len(problem_segments) == 0:
        print(f"  🎉 AssemblyAI 在段落控制上與 Groq 最佳方案相當或更好！")
        return True
    else:
        print(f"  ❌ AssemblyAI 在段落控制上不如 Groq 最佳方案")
        return False

def test_assemblyai_with_options(api_key, audio_file):
    """測試 AssemblyAI 的不同選項"""
    print(f"\n🚀 詳細測試 AssemblyAI Universal-1")
    print("=" * 60)
    
    try:
        # 上傳音檔
        print("📤 上傳音檔...")
        with open(audio_file, 'rb') as f:
            upload_response = requests.post(
                'https://api.assemblyai.com/v2/upload',
                headers={'authorization': api_key},
                files={'file': f}
            )
        
        if upload_response.status_code != 200:
            print(f"❌ 上傳失敗: {upload_response.text}")
            return None
        
        upload_url = upload_response.json()['upload_url']
        print(f"✅ 上傳成功")
        
        # 提交轉錄任務 (啟用所有功能)
        print("🔄 提交轉錄任務 (啟用多人辨識和其他功能)...")
        
        transcription_request = {
            'audio_url': upload_url,
            'language_code': 'zh',
            'speaker_labels': True,        # 多人辨識
            'speakers_expected': 1,        # 預期說話者數量
            'punctuate': True,            # 標點符號
            'format_text': True,          # 格式化文字
            'dual_channel': False,        # 單聲道
            'sentiment_analysis': True,   # 情感分析
            'entity_detection': True,     # 實體檢測
            'summarization': True,        # 摘要
            'auto_chapters': True         # 自動章節
        }
        
        headers = {
            'authorization': api_key,
            'content-type': 'application/json'
        }
        
        response = requests.post(
            'https://api.assemblyai.com/v2/transcript',
            headers=headers,
            json=transcription_request
        )
        
        if response.status_code != 200:
            print(f"❌ 提交失敗: {response.text}")
            return None
        
        transcript_id = response.json()['id']
        print(f"✅ 任務提交成功: {transcript_id}")
        
        # 等待完成
        print("⏳ 等待轉錄完成...")
        max_wait = 180  # 最多等待3分鐘
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
                with open("assemblyai_full_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"💾 完整結果已保存: assemblyai_full_result.json")
                
                # 分析轉錄文字
                transcript_text = result['text']
                print(f"\n📝 AssemblyAI 轉錄文字:")
                print(f"  長度: {len(transcript_text)} 字符")
                print(f"  內容: {transcript_text}")
                
                # 檢查語言和術語
                has_traditional = any(char in transcript_text for char in ['台積電', '聯電', '連準會', '納斯達克'])
                print(f"\n📊 品質檢查:")
                print(f"  繁體中文: {'✅' if has_traditional else '❌'}")
                
                # 檢查專業術語
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
                
                print(f"  專業術語識別: {terms_found}/4 個")
                
                # 檢查時間戳記和段落
                if 'words' in result and result['words']:
                    print(f"📝 詞彙級時間戳記: {len(result['words'])} 個詞彙")
                
                if 'segments' in result and result['segments']:
                    print(f"📊 段落數: {len(result['segments'])}")
                    
                    # 創建 SRT
                    segments = []
                    for seg in result['segments']:
                        segments.append({
                            'start': seg['start'] / 1000,
                            'end': seg['end'] / 1000,
                            'text': seg['text']
                        })
                    
                    srt_content = create_srt_from_segments(segments)
                    
                    with open("assemblyai_detailed_result.srt", "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    print(f"💾 SRT 已保存: assemblyai_detailed_result.srt")
                    
                    # 分析 SRT 段落品質
                    is_better = analyze_assemblyai_srt(srt_content)
                    
                    return {
                        'success': True,
                        'transcript_text': transcript_text,
                        'srt_content': srt_content,
                        'has_traditional': has_traditional,
                        'terms_found': terms_found,
                        'word_count': len(result['words']) if 'words' in result else 0,
                        'segment_count': len(result['segments']) if 'segments' in result else 0,
                        'is_better_than_groq': is_better
                    }
                else:
                    print(f"❌ 沒有段落時間戳記資訊")
                    return {
                        'success': True,
                        'transcript_text': transcript_text,
                        'has_traditional': has_traditional,
                        'terms_found': terms_found,
                        'srt_content': None
                    }
                
            elif status == 'error':
                print(f"❌ 轉錄失敗: {result.get('error', 'Unknown error')}")
                return None
            else:
                time.sleep(10)
                waited += 10
        
        print(f"❌ 等待超時")
        return None
        
    except Exception as e:
        print(f"❌ AssemblyAI 詳細測試失敗: {str(e)}")
        return None

def main():
    """詳細測試 AssemblyAI"""
    assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    result = test_assemblyai_with_options(assemblyai_api_key, audio_file)
    
    if result and result['success']:
        print(f"\n🎯 AssemblyAI 最終評估:")
        print(f"  繁體中文: {'✅' if result['has_traditional'] else '❌'}")
        print(f"  專業術語: {result['terms_found']}/4 個")
        
        if 'word_count' in result:
            print(f"  詞彙級時間戳記: {result['word_count']} 個")
        if 'segment_count' in result:
            print(f"  段落數: {result['segment_count']} 個")
        
        if result.get('is_better_than_groq'):
            print(f"  🎉 AssemblyAI 在段落控制上優於 Groq！")
        else:
            print(f"  ⚠️ AssemblyAI 在段落控制上不如 Groq")
    
    print(f"\n🎉 AssemblyAI 詳細測試完成！")

if __name__ == "__main__":
    main()
