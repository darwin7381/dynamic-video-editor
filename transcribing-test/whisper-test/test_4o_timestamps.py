#!/usr/bin/env python3
"""
重新測試 OpenAI 4o 模型的時間戳記支援
基於最新文檔資訊
"""

import os
from dotenv import load_dotenv
import time
from openai import OpenAI

# 載入環境變數
load_dotenv()

def test_4o_models_timestamps():
    """重新測試 4o 模型的時間戳記支援"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    print("🔍 重新測試 OpenAI 4o 模型的時間戳記支援")
    print("=" * 60)
    
    # 測試配置
    test_cases = [
        # 4o-transcribe 的各種嘗試
        {
            "model": "gpt-4o-transcribe",
            "response_format": "verbose_json",
            "timestamp_granularities": ["segment"],
            "description": "4o-transcribe + 段落級時間戳記"
        },
        {
            "model": "gpt-4o-transcribe", 
            "response_format": "verbose_json",
            "timestamp_granularities": ["word"],
            "description": "4o-transcribe + 詞彙級時間戳記"
        },
        {
            "model": "gpt-4o-transcribe",
            "response_format": "json",
            "timestamp_granularities": ["segment"],
            "description": "4o-transcribe + JSON + 段落級"
        },
        # 4o-mini-transcribe 的各種嘗試
        {
            "model": "gpt-4o-mini-transcribe",
            "response_format": "verbose_json", 
            "timestamp_granularities": ["segment"],
            "description": "4o-mini + 段落級時間戳記"
        },
        {
            "model": "gpt-4o-mini-transcribe",
            "response_format": "json",
            "timestamp_granularities": ["word"],
            "description": "4o-mini + JSON + 詞彙級"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n--- {test_case['description']} ---")
        
        try:
            start_time = time.time()
            
            # 構建參數
            params = {
                "model": test_case["model"],
                "file": open(audio_file, "rb"),
                "response_format": test_case["response_format"],
                "language": "zh"
            }
            
            # 添加時間戳記粒度
            if "timestamp_granularities" in test_case:
                params["timestamp_granularities"] = test_case["timestamp_granularities"]
            
            transcription = client.audio.transcriptions.create(**params)
            
            processing_time = time.time() - start_time
            
            print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
            
            # 詳細檢查回應結構
            print(f"📊 回應類型: {type(transcription)}")
            
            # 檢查基本屬性
            if hasattr(transcription, 'text'):
                print(f"📝 文字: {transcription.text[:100]}...")
            
            if hasattr(transcription, 'language'):
                print(f"🌍 語言: {transcription.language}")
                
            if hasattr(transcription, 'duration'):
                print(f"⏱️ 時長: {transcription.duration} 秒")
            
            # 檢查時間戳記
            has_segments = hasattr(transcription, 'segments') and transcription.segments
            has_words = hasattr(transcription, 'words') and transcription.words
            
            if has_segments:
                print(f"📊 段落級時間戳記: ✅ ({len(transcription.segments)} 個段落)")
                # 顯示第一個段落
                first_seg = transcription.segments[0]
                print(f"   第一段: [{first_seg.start}-{first_seg.end}] {first_seg.text}")
            else:
                print(f"📊 段落級時間戳記: ❌")
            
            if has_words:
                print(f"📝 詞彙級時間戳記: ✅ ({len(transcription.words)} 個詞彙)")
                # 顯示前幾個詞彙
                for i, word in enumerate(transcription.words[:5]):
                    print(f"   詞彙 {i+1}: [{word.start}-{word.end}] '{word.word}'")
            else:
                print(f"📝 詞彙級時間戳記: ❌")
            
            results.append({
                'config': test_case['description'],
                'model': test_case['model'],
                'success': True,
                'processing_time': processing_time,
                'has_segments': has_segments,
                'has_words': has_words,
                'segment_count': len(transcription.segments) if has_segments else 0,
                'word_count': len(transcription.words) if has_words else 0
            })
            
        except Exception as e:
            print(f"❌ 失敗 - 錯誤: {str(e)}")
            results.append({
                'config': test_case['description'],
                'model': test_case['model'],
                'success': False,
                'error': str(e)
            })
        
        time.sleep(1)
    
    # 總結
    print(f"\n" + "=" * 60)
    print(f"📊 4o 模型時間戳記支援測試結果")
    print("=" * 60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"總測試: {len(results)}")
    print(f"成功: {len(successful)}")
    print(f"失敗: {len(failed)}")
    
    if successful:
        print(f"\n✅ 支援時間戳記的配置:")
        for result in successful:
            if result['has_segments'] or result['has_words']:
                print(f"  - {result['config']}")
                print(f"    段落級: {'✅' if result['has_segments'] else '❌'} ({result['segment_count']})")
                print(f"    詞彙級: {'✅' if result['has_words'] else '❌'} ({result['word_count']})")
        
        if not any(r['has_segments'] or r['has_words'] for r in successful):
            print("  ❌ 所有成功的測試都不包含時間戳記")
    
    if failed:
        print(f"\n❌ 失敗的測試:")
        for result in failed:
            print(f"  - {result['config']}: {result['error']}")
    
    return results

if __name__ == "__main__":
    test_4o_models_timestamps()
