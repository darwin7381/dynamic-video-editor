#!/usr/bin/env python3
"""
正確測試 OpenAI 4o 模型的時間戳記支援
根據最新文檔，4o 模型確實支援 timestamp_granularities
"""

import os
from dotenv import load_dotenv
import time
from openai import OpenAI

# 載入環境變數
load_dotenv()

def test_4o_models_correct():
    """正確測試 4o 模型"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    print("🔍 正確測試 OpenAI 4o 模型的時間戳記支援")
    print("=" * 60)
    
    # 根據搜尋結果，4o 模型確實支援 timestamp_granularities
    test_cases = [
        {
            "model": "gpt-4o-transcribe",
            "response_format": "json",
            "timestamp_granularities": ["segment"],
            "description": "4o-transcribe JSON + 段落時間戳記"
        },
        {
            "model": "gpt-4o-transcribe",
            "response_format": "json", 
            "timestamp_granularities": ["word"],
            "description": "4o-transcribe JSON + 詞彙時間戳記"
        },
        {
            "model": "gpt-4o-transcribe",
            "response_format": "json",
            "timestamp_granularities": ["segment", "word"],
            "description": "4o-transcribe JSON + 段落+詞彙時間戳記"
        },
        {
            "model": "gpt-4o-mini-transcribe",
            "response_format": "json",
            "timestamp_granularities": ["segment"],
            "description": "4o-mini JSON + 段落時間戳記"
        },
        {
            "model": "gpt-4o-mini-transcribe",
            "response_format": "json",
            "timestamp_granularities": ["word"],
            "description": "4o-mini JSON + 詞彙時間戳記"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n--- {test_case['description']} ---")
        
        try:
            start_time = time.time()
            
            with open(audio_file, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    model=test_case["model"],
                    file=f,
                    response_format=test_case["response_format"],
                    timestamp_granularities=test_case["timestamp_granularities"],
                    language="zh"
                )
            
            processing_time = time.time() - start_time
            
            print(f"✅ 成功 - 處理時間: {processing_time:.2f} 秒")
            
            # 檢查回應結構
            print(f"📊 回應類型: {type(transcription)}")
            
            if hasattr(transcription, '__dict__'):
                print(f"📋 物件屬性:")
                for attr, value in transcription.__dict__.items():
                    if attr == 'text':
                        print(f"  {attr}: {len(str(value))} 字符")
                    elif attr in ['segments', 'words']:
                        if value:
                            print(f"  {attr}: {len(value)} 個")
                        else:
                            print(f"  {attr}: None")
                    else:
                        print(f"  {attr}: {str(value)[:50]}...")
            
            # 檢查時間戳記
            has_segments = hasattr(transcription, 'segments') and transcription.segments
            has_words = hasattr(transcription, 'words') and transcription.words
            
            if has_segments:
                print(f"🎉 發現段落級時間戳記: {len(transcription.segments)} 個段落")
                first_seg = transcription.segments[0]
                print(f"   第一段: [{first_seg.start:.2f}-{first_seg.end:.2f}] {first_seg.text}")
            
            if has_words:
                print(f"🎉 發現詞彙級時間戳記: {len(transcription.words)} 個詞彙")
                for i, word in enumerate(transcription.words[:3]):
                    print(f"   詞彙 {i+1}: [{word.start:.2f}-{word.end:.2f}] '{word.word}'")
            
            if not has_segments and not has_words:
                print(f"❌ 沒有發現任何時間戳記")
            
            results.append({
                'model': test_case['model'],
                'description': test_case['description'],
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
                'model': test_case['model'],
                'description': test_case['description'],
                'success': False,
                'error': str(e)
            })
        
        time.sleep(1)
    
    # 總結
    print(f"\n" + "=" * 60)
    print(f"📊 4o 模型時間戳記支援最終結論")
    print("=" * 60)
    
    successful = [r for r in results if r['success']]
    with_timestamps = [r for r in successful if r['has_segments'] or r['has_words']]
    
    if with_timestamps:
        print(f"🎉 確認！4o 模型支援時間戳記:")
        for result in with_timestamps:
            print(f"  ✅ {result['description']}")
            print(f"     段落級: {'✅' if result['has_segments'] else '❌'} ({result['segment_count']})")
            print(f"     詞彙級: {'✅' if result['has_words'] else '❌'} ({result['word_count']})")
    else:
        print(f"❌ 確認：4o 模型不支援時間戳記")
        print(f"   所有測試都沒有返回時間戳記資訊")
    
    return results

if __name__ == "__main__":
    test_4o_models_correct()
