#!/usr/bin/env python3
"""
確實測試 AssemblyAI 的段落級輸出
使用正確的 API 方法
"""

import os
from dotenv import load_dotenv
import requests
import json
import time
from datetime import timedelta

# 載入環境變數
load_dotenv()

def format_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = td.total_seconds() % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def test_assemblyai_segment_with_direct_api():
    """使用直接 API 調用測試 AssemblyAI 段落級"""
    print(f"\n🚀 AssemblyAI Universal-1 段落級測試 (直接 API)")
    print("=" * 60)
    
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    audio_file = "../audio-tts-mp3-20250523032437-WJdKQdwW.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 音檔不存在: {audio_file}")
        return None
    
    try:
        # 步驟1: 上傳音檔
        print(f"📤 步驟1: 上傳音檔...")
        upload_url = "https://api.assemblyai.com/v2/upload"
        headers = {"authorization": api_key}
        
        with open(audio_file, 'rb') as f:
            upload_response = requests.post(upload_url, headers=headers, files={'file': f})
        
        if upload_response.status_code != 200:
            print(f"❌ 上傳失敗: {upload_response.status_code}")
            print(f"錯誤: {upload_response.text}")
            return None
        
        audio_url = upload_response.json()['upload_url']
        print(f"✅ 音檔上傳成功: {audio_url}")
        
        # 步驟2: 開始轉錄 (要求段落級數據)
        print(f"📤 步驟2: 開始轉錄...")
        transcript_url = "https://api.assemblyai.com/v2/transcript"
        
        transcript_request = {
            "audio_url": audio_url,
            "language_code": "zh",
            "punctuate": True,
            "format_text": True,
            "auto_chapters": False,
            "summarization": False,
            "summary_model": "informative",
            "summary_type": "bullets"
        }
        
        transcript_response = requests.post(transcript_url, json=transcript_request, headers=headers)
        
        if transcript_response.status_code != 200:
            print(f"❌ 轉錄請求失敗: {transcript_response.status_code}")
            print(f"錯誤: {transcript_response.text}")
            return None
        
        transcript_id = transcript_response.json()['id']
        print(f"✅ 轉錄請求成功，ID: {transcript_id}")
        
        # 步驟3: 輪詢轉錄狀態
        print(f"⏳ 步驟3: 等待轉錄完成...")
        polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        
        while True:
            polling_response = requests.get(polling_url, headers=headers)
            transcript_result = polling_response.json()
            
            status = transcript_result['status']
            print(f"📊 轉錄狀態: {status}")
            
            if status == 'completed':
                print(f"✅ 轉錄完成！")
                break
            elif status == 'error':
                print(f"❌ 轉錄失敗: {transcript_result.get('error')}")
                return None
            else:
                print(f"⏳ 等待中... (5秒後重試)")
                time.sleep(5)
        
        # 步驟4: 獲取段落級數據
        print(f"📥 步驟4: 獲取段落級數據...")
        
        # 保存完整結果
        with open("assemblyai_segment_real_result.json", "w", encoding="utf-8") as f:
            json.dump(transcript_result, f, ensure_ascii=False, indent=2)
        print(f"💾 完整結果已保存: assemblyai_segment_real_result.json")
        
        # 嘗試獲取不同級別的段落數據
        segments = []
        segment_type = "unknown"
        
        # 方法1: 檢查 sentences
        sentences_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}/sentences"
        sentences_response = requests.get(sentences_url, headers=headers)
        
        if sentences_response.status_code == 200:
            sentences_data = sentences_response.json()
            if 'sentences' in sentences_data and sentences_data['sentences']:
                print(f"✅ 獲取句子級數據: {len(sentences_data['sentences'])} 個句子")
                
                for sentence in sentences_data['sentences']:
                    segments.append({
                        'text': sentence['text'],
                        'start': sentence['start'] / 1000.0,
                        'end': sentence['end'] / 1000.0,
                        'confidence': sentence.get('confidence', 0)
                    })
                segment_type = "sentences"
                
                # 保存句子數據
                with open("assemblyai_sentences_data.json", "w", encoding="utf-8") as f:
                    json.dump(sentences_data, f, ensure_ascii=False, indent=2)
                print(f"💾 句子數據已保存: assemblyai_sentences_data.json")
        
        # 方法2: 檢查 paragraphs
        if not segments:
            paragraphs_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}/paragraphs"
            paragraphs_response = requests.get(paragraphs_url, headers=headers)
            
            if paragraphs_response.status_code == 200:
                paragraphs_data = paragraphs_response.json()
                if 'paragraphs' in paragraphs_data and paragraphs_data['paragraphs']:
                    print(f"✅ 獲取段落級數據: {len(paragraphs_data['paragraphs'])} 個段落")
                    
                    for paragraph in paragraphs_data['paragraphs']:
                        segments.append({
                            'text': paragraph['text'],
                            'start': paragraph['start'] / 1000.0,
                            'end': paragraph['end'] / 1000.0,
                            'confidence': paragraph.get('confidence', 0)
                        })
                    segment_type = "paragraphs"
                    
                    # 保存段落數據
                    with open("assemblyai_paragraphs_data.json", "w", encoding="utf-8") as f:
                        json.dump(paragraphs_data, f, ensure_ascii=False, indent=2)
                    print(f"💾 段落數據已保存: assemblyai_paragraphs_data.json")
        
        # 方法3: 手動分割 (如果沒有自動段落)
        if not segments:
            print(f"⚠️ 沒有自動段落，手動分割文本")
            text = transcript_result['text']
            duration = transcript_result.get('audio_duration', 30000) / 1000.0
            
            # 按句號分割
            sentences = text.split('。')
            segment_duration = duration / len(sentences) if sentences else duration
            
            for idx, sentence in enumerate(sentences):
                if sentence.strip():
                    segments.append({
                        'text': sentence.strip() + ('。' if idx < len(sentences) - 1 else ''),
                        'start': idx * segment_duration,
                        'end': (idx + 1) * segment_duration,
                        'confidence': transcript_result.get('confidence', 0)
                    })
            segment_type = "manual_split"
        
        # 生成段落級 SRT
        if segments:
            srt_content = ""
            for i, seg in enumerate(segments, 1):
                text = seg['text'].strip()
                start = seg['start']
                end = seg['end']
                
                srt_content += f"{i}\n"
                srt_content += f"{format_time(start)} --> {format_time(end)}\n"
                srt_content += f"{text}\n\n"
            
            # 保存段落級 SRT
            with open("assemblyai_segment_real.srt", "w", encoding="utf-8") as f:
                f.write(srt_content)
            print(f"💾 段落級 SRT 已保存: assemblyai_segment_real.srt")
            
            # 分析段落特性
            lengths = [len(seg['text'].strip()) for seg in segments]
            print(f"📊 AssemblyAI 段落分析:")
            print(f"  段落類型: {segment_type}")
            print(f"  總段落數: {len(segments)}")
            print(f"  平均長度: {sum(lengths) / len(lengths):.1f} 字符")
            print(f"  最長段落: {max(lengths)} 字符")
            print(f"  最短段落: {min(lengths)} 字符")
            print(f"  長段落數: {sum(1 for l in lengths if l > 25)} 個 (>25字符)")
            
            # 創建分析結果
            analysis_result = {
                'transcript_result': transcript_result,
                'segments': segments,
                'segment_type': segment_type,
                'analysis': {
                    'total_segments': len(segments),
                    'avg_length': sum(lengths) / len(lengths),
                    'max_length': max(lengths),
                    'min_length': min(lengths),
                    'long_segments_count': sum(1 for l in lengths if l > 25)
                }
            }
            
            return analysis_result
        else:
            print(f"❌ 沒有有效的段落數據")
            return None
            
    except Exception as e:
        print(f"❌ AssemblyAI 測試錯誤: {str(e)}")
        return None

def main():
    """主測試函數"""
    print("🎯 AssemblyAI 段落級確實測試")
    print("=" * 80)
    
    # 測試 AssemblyAI 段落級
    result = test_assemblyai_segment_with_direct_api()
    
    if result:
        print(f"\n✅ AssemblyAI 段落級測試成功！")
        print(f"📁 生成的文件:")
        print(f"  - assemblyai_segment_real.srt (段落級 SRT)")
        print(f"  - assemblyai_segment_real_result.json (完整結果)")
        print(f"  - assemblyai_sentences_data.json (句子數據，如果有)")
        print(f"  - assemblyai_paragraphs_data.json (段落數據，如果有)")
    else:
        print(f"\n❌ AssemblyAI 段落級測試失敗")
    
    return result

if __name__ == "__main__":
    main()
