#!/usr/bin/env python3
"""
修復 ElevenLabs Scribe 測試
使用正確的 multipart form data 格式
"""

import os
from dotenv import load_dotenv
import requests
import json

# 載入環境變數
load_dotenv()

def test_elevenlabs_scribe_fixed(api_key, audio_file):
    """修復後的 ElevenLabs Scribe 測試"""
    print(f"\n🚀 測試 ElevenLabs Scribe V1 (修復版)")
    print("=" * 60)
    
    try:
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        
        headers = {
            "xi-api-key": api_key
        }
        
        # 正確的 multipart form data 格式
        with open(audio_file, 'rb') as f:
            files = {
                "file": (audio_file, f, "audio/mpeg")
            }
            
            data = {
                "model_id": "scribe-v1"
            }
            
            print("🔄 提交 ElevenLabs Scribe 轉錄 (修復版)...")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        
        print(f"📊 回應狀態: {response.status_code}")
        print(f"📋 回應內容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ElevenLabs Scribe 轉錄成功")
            
            # 保存完整結果
            with open("elevenlabs_scribe_success.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 完整結果已保存: elevenlabs_scribe_success.json")
            
            return result
        else:
            print(f"❌ ElevenLabs API 錯誤 {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ElevenLabs 測試失敗: {str(e)}")
        return None

def main():
    """修復後的 ElevenLabs 測試"""
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    # 測試 ElevenLabs
    result = test_elevenlabs_scribe_fixed(elevenlabs_api_key, audio_file)
    
    if result:
        print(f"🎉 ElevenLabs 測試成功！")
        print(f"📋 結果: {result}")
    else:
        print(f"😞 ElevenLabs 測試失敗")
    
    print(f"\n🎉 ElevenLabs 修復測試完成！")

if __name__ == "__main__":
    main()
