#!/usr/bin/env python3
"""
正確測試 ElevenLabs Scribe 和 AssemblyAI
基於官方文檔的正確實現
"""

import os
from dotenv import load_dotenv
import time
import requests
import assemblyai as aai

# 載入環境變數
load_dotenv()

def format_srt_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def analyze_srt_quality(srt_content, service_name):
    """分析 SRT 品質並與最佳方案比較"""
    print(f"\n📺 {service_name} SRT 品質分析")
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
    
    # 轉錄品質
    has_traditional = any(char in full_text for char in ['台積電', '聯電', '連準會', '納斯達克'])
    punctuation_count = full_text.count('，') + full_text.count('。') + full_text.count('！') + full_text.count('？')
    
    terms_found = 0
    if '台積電' in full_text:
        terms_found += 1
    if 'NVIDIA' in full_text or '輝達' in full_text:
        terms_found += 1
    if '納斯達克' in full_text:
        terms_found += 1
    if '比特幣' in full_text:
        terms_found += 1
    
    print(f"\n📝 轉錄品質:")
    print(f"  語言: {'繁體中文 ✅' if has_traditional else '簡體中文 ❌'}")
    print(f"  標點符號: {punctuation_count} 個")
    print(f"  專業術語: {terms_found}/4 個")
    
    # 顯示前5個段落
    print(f"\n📋 前5個段落:")
    for seg in segments[:5]:
        status = "🚨" if seg['length'] > 40 else "⚠️" if seg['length'] > 30 else "✅" if 15 <= seg['length'] <= 25 else "🔸"
        print(f"  {seg['id']}. ({seg['length']}字符) {status} {seg['text']}")
    
    # 與最佳方案比較 (Groq + Prompt + 詞彙級: 95.2分)
    print(f"\n🏆 與最佳方案比較 (Groq 95.2分):")
    print(f"  {service_name} 最長段落: {max(lengths)} vs 18 (最佳)")
    print(f"  {service_name} 問題段落: {len(problem_segments)} vs 0 (最佳)")
    
    # 計算評分
    segment_score = 50 if max(lengths) <= 18 and len(problem_segments) == 0 else 40 if max(lengths) <= 25 else 30 if len(very_long_segments) == 0 else 20
    
    quality_score = 0
    if has_traditional:
        quality_score += 20
    quality_score += min(punctuation_count * 2, 15)
    quality_score += terms_found * 3.75
    
    total_score = segment_score + quality_score
    
    print(f"  {service_name} 總評分: {total_score:.1f}/100")
    
    if total_score > 95:
        print(f"  🎉 {service_name} 比最佳方案更好！")
        return True
    elif total_score > 85:
        print(f"  ✅ {service_name} 接近最佳方案")
        return False
    else:
        print(f"  ❌ {service_name} 不如最佳方案")
        return False

def test_elevenlabs_scribe(api_key, audio_file):
    """測試 ElevenLabs Scribe 模型"""
    print(f"\n🚀 測試 ElevenLabs Scribe V1")
    print("=" * 60)
    
    try:
        # ElevenLabs Speech-to-Text API 端點
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        
        headers = {
            "xi-api-key": api_key
        }
        
        # 準備文件
        with open(audio_file, 'rb') as f:
            files = {
                "audio": f,
                "model_id": (None, "scribe-v1")  # 使用 Scribe V1 模型
            }
            
            print("🔄 提交 ElevenLabs Scribe 轉錄...")
            response = requests.post(url, headers=headers, files=files, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ElevenLabs Scribe 轉錄成功")
            
            # 保存完整結果
            with open("elevenlabs_scribe_result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 完整結果已保存: elevenlabs_scribe_result.json")
            
            # 分析結果
            if 'transcript' in result:
                transcript_text = result['transcript']
                print(f"\n📝 ElevenLabs 轉錄文字:")
                print(f"  長度: {len(transcript_text)} 字符")
                print(f"  內容: {transcript_text}")
                
                # 檢查是否有時間戳記
                if 'segments' in result:
                    print(f"📊 段落數: {len(result['segments'])}")
                    
                    # 創建 SRT
                    segments = []
                    for seg in result['segments']:
                        segments.append({
                            'start': seg['start_time'],
                            'end': seg['end_time'], 
                            'text': seg['text']
                        })
                    
                    srt_content = create_srt_from_segments(segments)
                    
                    with open("elevenlabs_scribe.srt", "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    print(f"💾 SRT 已保存: elevenlabs_scribe.srt")
                    
                    # 分析 SRT 品質
                    is_better = analyze_srt_quality(srt_content, "ElevenLabs Scribe")
                    
                    return {
                        'success': True,
                        'transcript_text': transcript_text,
                        'srt_content': srt_content,
                        'is_better': is_better
                    }
                else:
                    print(f"⚠️ 沒有段落時間戳記，只有文字")
                    return {
                        'success': True,
                        'transcript_text': transcript_text,
                        'srt_content': None,
                        'is_better': False
                    }
            else:
                print(f"❌ 未知回應格式: {result}")
                return None
        else:
            print(f"❌ ElevenLabs API 錯誤 {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ElevenLabs 測試失敗: {str(e)}")
        return None

def create_srt_from_segments(segments):
    """從段落創建 SRT"""
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

def test_assemblyai_correct(api_key, audio_file):
    """正確測試 AssemblyAI (使用 export_srt 方法)"""
    print(f"\n🚀 測試 AssemblyAI Universal-1 (正確方法)")
    print("=" * 60)
    
    try:
        # 設定 API Key
        aai.settings.api_key = api_key
        
        print("🔄 開始 AssemblyAI 轉錄...")
        
        # 基本設定
        config = aai.TranscriptionConfig(
            language_code="zh",
            speaker_labels=True,
            punctuate=True,
            format_text=True
        )
        
        transcriber = aai.Transcriber(config=config)
        
        # 執行轉錄
        transcript = transcriber.transcribe(audio_file)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"❌ 轉錄失敗: {transcript.error}")
            return None
        
        print(f"✅ AssemblyAI 轉錄成功")
        
        # 保存轉錄文字
        with open("assemblyai_transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript.text)
        print(f"💾 轉錄文字已保存: assemblyai_transcript.txt")
        
        # 嘗試生成 SRT (使用官方方法)
        try:
            srt_content = transcript.export_srt()
            
            with open("assemblyai_official.srt", "w", encoding="utf-8") as f:
                f.write(srt_content)
            print(f"💾 官方 SRT 已保存: assemblyai_official.srt")
            
            # 分析 SRT 品質
            is_better = analyze_srt_quality(srt_content, "AssemblyAI")
            
            return {
                'success': True,
                'transcript_text': transcript.text,
                'srt_content': srt_content,
                'is_better': is_better
            }
            
        except Exception as e:
            print(f"⚠️ SRT 生成失敗: {str(e)}")
            
            # 如果有詞彙級時間戳記，手動創建 SRT
            if hasattr(transcript, 'words') and transcript.words:
                print(f"📝 使用詞彙級時間戳記手動創建 SRT...")
                
                segments = []
                current_segment = {'start': None, 'end': None, 'text': ''}
                
                for word in transcript.words:
                    word_text = word.text.strip()
                    if not word_text:
                        continue
                    
                    if current_segment['start'] is None:
                        current_segment['start'] = word.start / 1000
                        current_segment['end'] = word.end / 1000
                        current_segment['text'] = word_text
                    elif len(current_segment['text'] + ' ' + word_text) > 25:
                        segments.append(current_segment.copy())
                        current_segment = {
                            'start': word.start / 1000,
                            'end': word.end / 1000,
                            'text': word_text
                        }
                    else:
                        current_segment['text'] += ' ' + word_text
                        current_segment['end'] = word.end / 1000
                
                if current_segment['text']:
                    segments.append(current_segment)
                
                # 生成 SRT
                srt_lines = []
                for i, seg in enumerate(segments, 1):
                    start_time = format_srt_time(seg['start'])
                    end_time = format_srt_time(seg['end'])
                    
                    srt_lines.append(f"{i}")
                    srt_lines.append(f"{start_time} --> {end_time}")
                    srt_lines.append(seg['text'])
                    srt_lines.append("")
                
                srt_content = '\n'.join(srt_lines)
                
                with open("assemblyai_custom.srt", "w", encoding="utf-8") as f:
                    f.write(srt_content)
                print(f"💾 自定義 SRT 已保存: assemblyai_custom.srt")
                
                # 分析品質
                is_better = analyze_srt_quality(srt_content, "AssemblyAI (自定義)")
                
                return {
                    'success': True,
                    'transcript_text': transcript.text,
                    'srt_content': srt_content,
                    'is_better': is_better
                }
            else:
                return {
                    'success': True,
                    'transcript_text': transcript.text,
                    'srt_content': None,
                    'is_better': False
                }
        
    except Exception as e:
        print(f"❌ AssemblyAI 測試失敗: {str(e)}")
        return None

def main():
    """正確測試 ElevenLabs 和 AssemblyAI"""
    print("🎯 正確測試 ElevenLabs Scribe 和 AssemblyAI Universal-1")
    print("=" * 80)
    
    # API Keys
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    results = []
    
    # 1. 測試 ElevenLabs Scribe
    elevenlabs_result = test_elevenlabs_scribe(elevenlabs_api_key, audio_file)
    if elevenlabs_result:
        results.append(('ElevenLabs Scribe', elevenlabs_result))
    
    # 2. 測試 AssemblyAI
    assemblyai_result = test_assemblyai_correct(assemblyai_api_key, audio_file)
    if assemblyai_result:
        results.append(('AssemblyAI Universal-1', assemblyai_result))
    
    # 3. 最終比較
    print(f"\n" + "=" * 80)
    print(f"🏆 ElevenLabs 和 AssemblyAI vs 最佳方案比較")
    print("=" * 80)
    
    current_best = {
        'name': 'Groq + Prompt + 詞彙級',
        'score': 95.2,
        'max_length': 18,
        'problem_count': 0
    }
    
    print(f"📊 現有最佳方案: {current_best['name']} ({current_best['score']}分)")
    print(f"  最長段落: {current_best['max_length']} 字符")
    print(f"  問題段落: {current_best['problem_count']} 個")
    
    better_services = []
    
    for service_name, result in results:
        print(f"\n🔍 {service_name} 最終評估:")
        if result['success']:
            print(f"  ✅ 測試成功")
            if result['srt_content']:
                print(f"  ✅ 成功生成 SRT")
                if result['is_better']:
                    print(f"  🎉 比最佳方案更好！")
                    better_services.append(service_name)
                else:
                    print(f"  ⚠️ 不如最佳方案")
            else:
                print(f"  ❌ 無法生成 SRT")
        else:
            print(f"  ❌ 測試失敗")
    
    # 最終結論
    if better_services:
        print(f"\n🎉 找到 {len(better_services)} 個比最佳方案更好的服務:")
        for service in better_services:
            print(f"  - {service}")
    else:
        print(f"\n📊 結論: 現有的 Groq 最佳方案仍然是最好的")
    
    print(f"\n🎉 ElevenLabs 和 AssemblyAI 測試完成！")
    return results

if __name__ == "__main__":
    main()
