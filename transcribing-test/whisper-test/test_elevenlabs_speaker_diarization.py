#!/usr/bin/env python3
"""
測試 ElevenLabs Scribe 的多人辨識功能
根據官方文檔，應該支援 speaker diarization
"""

import os
from dotenv import load_dotenv
import requests
import json

# 載入環境變數
load_dotenv()

def test_elevenlabs_with_speaker_diarization(api_key, audio_file):
    """測試 ElevenLabs 的多人辨識功能"""
    print(f"\n🚀 測試 ElevenLabs Scribe 多人辨識功能")
    print("=" * 60)
    
    try:
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        
        headers = {
            "xi-api-key": api_key
        }
        
        # 測試是否有多人辨識參數
        with open(audio_file, 'rb') as f:
            files = {
                "file": (audio_file, f, "audio/mpeg")
            }
            
            # 嘗試不同的參數組合
            test_configs = [
                {"model_id": "scribe_v1"},
                {"model_id": "scribe_v1_experimental"},
                {"model_id": "scribe_v1", "enable_speaker_diarization": "true"},
                {"model_id": "scribe_v1", "speaker_diarization": "true"},
                {"model_id": "scribe_v1", "diarization": "true"}
            ]
            
            for i, config in enumerate(test_configs, 1):
                print(f"\n📊 測試配置 {i}: {config}")
                
                try:
                    response = requests.post(url, headers=headers, files={"file": (audio_file, open(audio_file, 'rb'), "audio/mpeg")}, data=config, timeout=120)
                    
                    print(f"📊 回應狀態: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ 配置 {i} 成功")
                        
                        # 檢查是否有說話者資訊
                        if 'speakers' in result:
                            print(f"🎉 發現說話者資訊: {result['speakers']}")
                        
                        if 'words' in result:
                            words = result['words']
                            # 檢查詞彙中是否有說話者標識
                            speakers_in_words = set()
                            for word in words[:20]:  # 檢查前20個詞彙
                                if 'speaker' in word:
                                    speakers_in_words.add(word['speaker'])
                                elif 'speaker_id' in word:
                                    speakers_in_words.add(word['speaker_id'])
                            
                            if speakers_in_words:
                                print(f"🎉 詞彙中發現說話者標識: {speakers_in_words}")
                            else:
                                print(f"❌ 詞彙中沒有說話者標識")
                        
                        # 保存這個配置的結果
                        filename = f"elevenlabs_config_{i}_result.json"
                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                        print(f"💾 結果已保存: {filename}")
                        
                        # 如果這個配置有說話者資訊，返回結果
                        if 'speakers' in result or speakers_in_words:
                            print(f"🎉 找到支援多人辨識的配置！")
                            return result, config
                    else:
                        print(f"❌ 配置 {i} 失敗: {response.text}")
                
                except Exception as e:
                    print(f"❌ 配置 {i} 錯誤: {str(e)}")
        
        print(f"\n📊 所有配置測試完成")
        return None, None
        
    except Exception as e:
        print(f"❌ ElevenLabs 多人辨識測試失敗: {str(e)}")
        return None, None

def analyze_speaker_capabilities(result, config):
    """分析說話者辨識能力"""
    print(f"\n🔍 ElevenLabs 說話者辨識能力分析")
    print("=" * 60)
    
    print(f"📊 成功配置: {config}")
    
    # 檢查說話者相關功能
    if 'speakers' in result:
        speakers = result['speakers']
        print(f"✅ 說話者列表: {speakers}")
    
    if 'words' in result:
        words = result['words']
        print(f"📝 詞彙數量: {len(words)}")
        
        # 分析說話者分佈
        speaker_distribution = {}
        for word in words:
            speaker = word.get('speaker', word.get('speaker_id', 'unknown'))
            if speaker not in speaker_distribution:
                speaker_distribution[speaker] = 0
            speaker_distribution[speaker] += 1
        
        print(f"🎯 說話者分佈:")
        for speaker, count in speaker_distribution.items():
            print(f"  {speaker}: {count} 個詞彙")
    
    # 檢查其他功能
    if 'audio_events' in result:
        events = result['audio_events']
        print(f"🎵 音頻事件: {len(events)} 個")
    
    return speaker_distribution if 'speaker_distribution' in locals() else {}

def main():
    """測試 ElevenLabs 多人辨識功能"""
    print("🎯 ElevenLabs Scribe 多人辨識功能測試")
    print("=" * 80)
    print("根據官方文檔：支援 word-level timestamps, speaker diarization")
    print("=" * 80)
    
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    audio_file = "test_audio.mp3"
    
    if not os.path.exists(audio_file):
        print(f"❌ 錯誤: 找不到音檔 {audio_file}")
        return
    
    # 測試多人辨識功能
    result, successful_config = test_elevenlabs_with_speaker_diarization(elevenlabs_api_key, audio_file)
    
    if result and successful_config:
        print(f"🎉 ElevenLabs 多人辨識測試成功！")
        
        # 分析說話者能力
        speaker_info = analyze_speaker_capabilities(result, successful_config)
        
        print(f"\n🏆 ElevenLabs Scribe 完整功能確認:")
        print(f"  ✅ 詞彙級時間戳記: {len(result['words'])} 個詞彙")
        print(f"  ✅ 多人辨識: {len(speaker_info)} 個說話者")
        print(f"  ✅ 音頻事件標記: {'支援' if 'audio_events' in result else '未檢測到'}")
        
        return True
    else:
        print(f"😞 ElevenLabs 多人辨識測試失敗")
        print(f"可能需要不同的音檔或參數設定")
        return False

if __name__ == "__main__":
    main()
