#!/usr/bin/env python3
"""
測試 ElevenLabs 和 AssemblyAI 的語音轉文字模型
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

def analyze_transcription_quality(content, method_name):
    """分析轉錄品質"""
    print(f"\n🎯 {method_name} - 品質分析")
    print("=" * 60)
    
    # 檢查語言
    has_traditional = any(char in content for char in ['台積電', '聯電', '連準會', '納斯達克', '準會'])
    print(f"📝 語言: {'繁體中文 ✅' if has_traditional else '簡體中文 ❌'}")
    
    # 檢查標點符號
    punctuation_count = content.count('，') + content.count('。') + content.count('！') + content.count('？')
    print(f"📖 標點符號: {punctuation_count} 個")
    
    # 檢查專業術語
    terms_found = []
    if '台積電' in content:
        terms_found.append('台積電 ✅')
    elif '台积电' in content:
        terms_found.append('台积电 (簡體)')
    
    if 'NVIDIA' in content or '輝達' in content:
        terms_found.append('NVIDIA/輝達 ✅')
    elif '辉达' in content:
        terms_found.append('辉达 (簡體)')
    
    if '納斯達克' in content:
        terms_found.append('納斯達克 ✅')
    elif '那斯达克' in content:
        terms_found.append('那斯达克 (簡體)')
    
    if '比特幣' in content:
        terms_found.append('比特幣 ✅')
    elif '比特币' in content:
        terms_found.append('比特币 (簡體)')
    
    print(f"🏢 專業術語: {', '.join(terms_found) if terms_found else '無識別'}")
    
    # 顯示內容預覽
    print(f"\n📋 內容預覽:")
    print(f"  {content[:200]}...")
    
    return {
        'has_traditional': has_traditional,
        'punctuation_count': punctuation_count,
        'terms_found': len(terms_found),
        'content': content
    }

def test_elevenlabs(api_key, audio_file):
    """測試 ElevenLabs 語音轉文字"""
    print(f"\n🚀 測試 ElevenLabs 語音轉文字")
    print("=" * 60)
    
    try:
        # ElevenLabs API 端點 (需要確認正確的端點)
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 嘗試不同的 API 端點
        endpoints_to_try = [
            'https://api.elevenlabs.io/v1/speech-to-text',
            'https://api.elevenlabs.io/v1/audio/transcribe',
            'https://api.elevenlabs.io/v1/transcribe'
        ]
        
        for endpoint in endpoints_to_try:
            print(f"嘗試端點: {endpoint}")
            
            try:
                with open(audio_file, 'rb') as f:
                    files = {'audio': f}
                    response = requests.post(endpoint, headers=headers, files=files, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ ElevenLabs 成功")
                    print(f"📊 回應: {result}")
                    
                    # 分析結果
                    if 'text' in result:
                        analysis = analyze_transcription_quality(result['text'], "ElevenLabs")
                        return ('ElevenLabs', analysis, result['text'])
                    elif 'transcript' in result:
                        analysis = analyze_transcription_quality(result['transcript'], "ElevenLabs")
                        return ('ElevenLabs', analysis, result['transcript'])
                    else:
                        print(f"⚠️ 未知回應格式: {result}")
                else:
                    print(f"❌ HTTP {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ 請求錯誤: {str(e)}")
        
        print(f"❌ 所有 ElevenLabs 端點都失敗")
        return None
        
    except Exception as e:
        print(f"❌ ElevenLabs 測試失敗: {str(e)}")
        return None

def test_assemblyai(api_key, audio_file):
    """測試 AssemblyAI 語音轉文字"""
    print(f"\n🚀 測試 AssemblyAI Universal-1")
    print("=" * 60)
    
    try:
        # AssemblyAI API
        headers = {
            'authorization': api_key,
            'content-type': 'application/json'
        }
        
        # 1. 上傳音檔
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
        print(f"✅ 上傳成功: {upload_url}")
        
        # 2. 提交轉錄任務
        print("🔄 提交轉錄任務...")
        transcription_request = {
            'audio_url': upload_url,
            'language_code': 'zh',
            'speaker_labels': True,  # 啟用多人辨識
            'punctuate': True,       # 啟用標點符號
            'format_text': True      # 格式化文字
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
        
        # 3. 等待完成
        print("⏳ 等待轉錄完成...")
        while True:
            response = requests.get(
                f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
                headers=headers
            )
            
            result = response.json()
            status = result['status']
            
            print(f"📊 狀態: {status}")
            
            if status == 'completed':
                print(f"✅ AssemblyAI 轉錄完成")
                
                # 分析結果
                transcript_text = result['text']
                analysis = analyze_transcription_quality(transcript_text, "AssemblyAI")
                
                # 檢查是否有時間戳記資訊
                if 'segments' in result:
                    print(f"📊 獲得 {len(result['segments'])} 個段落的時間戳記")
                    
                    # 創建 SRT
                    segments = []
                    for seg in result['segments']:
                        segments.append({
                            'start': seg['start'] / 1000,  # 轉換為秒
                            'end': seg['end'] / 1000,
                            'text': seg['text']
                        })
                    
                    srt_content = create_srt_from_segments(segments)
                    
                    with open("assemblyai_result.srt", "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    print(f"💾 SRT 已保存: assemblyai_result.srt")
                    
                    return ('AssemblyAI', analysis, srt_content)
                else:
                    return ('AssemblyAI', analysis, transcript_text)
                
            elif status == 'error':
                print(f"❌ 轉錄失敗: {result.get('error', 'Unknown error')}")
                return None
            else:
                time.sleep(5)  # 等待5秒後再檢查
                
    except Exception as e:
        print(f"❌ AssemblyAI 測試失敗: {str(e)}")
        return None

def main():
    """測試 ElevenLabs 和 AssemblyAI"""
    print("🎯 測試 ElevenLabs 和 AssemblyAI 語音轉文字模型")
    print("=" * 80)
    
    # API Keys
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    results = []
    
    # 測試 ElevenLabs
    elevenlabs_result = test_elevenlabs(elevenlabs_api_key, audio_file)
    if elevenlabs_result:
        results.append(elevenlabs_result)
    
    # 測試 AssemblyAI
    assemblyai_result = test_assemblyai(assemblyai_api_key, audio_file)
    if assemblyai_result:
        results.append(assemblyai_result)
    
    # 與現有最佳方案比較
    print(f"\n" + "=" * 80)
    print(f"🏆 新模型 vs 現有最佳方案比較")
    print("=" * 80)
    
    # 現有最佳方案的基準
    current_best = {
        'name': 'Groq + Prompt + 詞彙級',
        'score': 95.2,
        'max_length': 18,
        'has_traditional': True,
        'punctuation_count': 7,
        'terms_found': 3
    }
    
    print(f"📊 現有最佳方案: {current_best['name']} (95.2分)")
    
    if results:
        for service_name, analysis, content in results:
            print(f"\n🔍 {service_name} vs 現有最佳方案:")
            print(f"  語言: {'繁體中文' if analysis['has_traditional'] else '簡體中文'}")
            print(f"  標點符號: {analysis['punctuation_count']} vs {current_best['punctuation_count']} (現有)")
            print(f"  專業術語: {analysis['terms_found']}/4 vs {current_best['terms_found']}/4 (現有)")
            
            # 簡單評分
            service_score = 0
            if analysis['has_traditional']:
                service_score += 20
            service_score += min(analysis['punctuation_count'] * 2, 15)
            service_score += analysis['terms_found'] * 3.75
            
            print(f"  轉錄品質評分: {service_score:.1f}/50")
            
            if service_score > current_best['score'] - 50:  # 只比較轉錄品質部分
                print(f"  🎉 {service_name} 轉錄品質優秀！")
            else:
                print(f"  ⚠️ {service_name} 轉錄品質一般")
    else:
        print(f"😞 ElevenLabs 和 AssemblyAI 測試都失敗")
    
    print(f"\n🎉 ElevenLabs 和 AssemblyAI 測試完成！")
    return results

if __name__ == "__main__":
    main()
