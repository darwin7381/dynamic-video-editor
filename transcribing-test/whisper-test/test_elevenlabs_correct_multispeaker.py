#!/usr/bin/env python3
"""
ElevenLabs Scribe V1 多人辨識正確測試
根據官方文檔：支援最多 32 個說話者辨識
官方文檔：https://elevenlabs.io/docs/capabilities/speech-to-text
"""

import os
import sys
from dotenv import load_dotenv
import requests
import json
import time

# 載入環境變數
load_dotenv()

def test_elevenlabs_speaker_diarization(api_key, audio_file):
    """
    測試 ElevenLabs Scribe V1 的多人辨識功能
    根據官方文檔，Scribe v1 支援：
    - 最多 32 個說話者辨識
    - 詞彙級時間戳記 (word-level timestamps)
    - 說話者標識 (speaker diarization)
    - 音頻事件標記 (audio events like laughter, applause)
    """
    print(f"\n{'='*80}")
    print(f"🔵 ElevenLabs Scribe V1 多人辨識測試（官方文檔確認）")
    print(f"{'='*80}")
    print(f"官方文檔：https://elevenlabs.io/docs/capabilities/speech-to-text")
    print(f"功能：最多 32 個說話者辨識")
    print(f"{'='*80}")
    
    try:
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        headers = {"xi-api-key": api_key}
        
        print(f"\n📤 上傳音檔並請求轉錄...")
        
        start_time = time.time()
        
        with open(audio_file, 'rb') as f:
            files = {"file": (audio_file, f, "audio/mpeg")}
            # 根據官方文檔，使用 scribe_v1 模型
            data = {"model_id": "scribe_v1"}
            
            response = requests.post(url, headers=headers, files=files, data=data, timeout=300)
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # 保存完整結果
            output_file = "elevenlabs_multispeaker_correct_result.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 轉錄成功！")
            print(f"⏱️  處理時間: {elapsed_time:.2f} 秒")
            
            # 分析結果
            print(f"\n{'='*80}")
            print(f"📊 轉錄結果分析")
            print(f"{'='*80}")
            
            # 基本資訊
            print(f"\n📝 基本資訊:")
            print(f"   語言: {result.get('language_code', 'N/A')}")
            print(f"   語言信心度: {result.get('language_probability', 0)*100:.1f}%")
            print(f"   文字長度: {len(result.get('text', ''))} 字符")
            
            # 檢查詞彙級時間戳記
            words = result.get('words', [])
            print(f"\n📊 詞彙級時間戳記:")
            print(f"   支援狀態: {'✅ 支援' if words else '❌ 不支援'}")
            print(f"   總詞彙數: {len(words)}")
            
            if words:
                print(f"\n   前3個詞彙樣本:")
                for i, word in enumerate(words[:3], 1):
                    print(f"   {i}. {word}")
            
            # 檢查多人辨識（speaker diarization）
            print(f"\n🎤 多人辨識（Speaker Diarization）:")
            
            speakers_found = set()
            speaker_word_counts = {}
            word_types = {}
            
            for word in words:
                # 檢查是否有 speaker_id 欄位
                if 'speaker_id' in word:
                    speaker = word['speaker_id']
                    speakers_found.add(speaker)
                    speaker_word_counts[speaker] = speaker_word_counts.get(speaker, 0) + 1
                
                # 統計詞彙類型
                word_type = word.get('type', 'unknown')
                word_types[word_type] = word_types.get(word_type, 0) + 1
            
            if speakers_found:
                print(f"   支援狀態: ✅ 確認支援")
                print(f"   檢測到說話者數量: {len(speakers_found)}")
                print(f"   說話者列表: {sorted(speakers_found)}")
                
                print(f"\n   各說話者詞彙數量:")
                for speaker in sorted(speakers_found):
                    count = speaker_word_counts[speaker]
                    percentage = (count / len(words)) * 100
                    print(f"     {speaker}: {count} 個詞彙 ({percentage:.1f}%)")
            else:
                print(f"   支援狀態: ❌ 未檢測到說話者")
                print(f"   注意: 可能是單人音檔或需要特定參數")
            
            # 檢查詞彙類型（word, spacing, audio_event）
            print(f"\n📝 詞彙類型分佈:")
            for word_type, count in word_types.items():
                percentage = (count / len(words)) * 100
                print(f"   {word_type}: {count} 個 ({percentage:.1f}%)")
            
            # 檢查音頻事件
            audio_events = [w for w in words if w.get('type') == 'audio_event']
            if audio_events:
                print(f"\n🎵 音頻事件標記:")
                print(f"   支援狀態: ✅ 支援")
                print(f"   檢測到事件數量: {len(audio_events)}")
                print(f"   前3個事件樣本:")
                for i, event in enumerate(audio_events[:3], 1):
                    print(f"   {i}. {event}")
            
            # 生成 SRT 檔案
            print(f"\n📝 生成字幕檔案...")
            
            # 1. 18字符段落 SRT
            srt_18chars = generate_srt_from_words(words, max_chars=18)
            with open("elevenlabs_multispeaker_18chars.srt", "w", encoding="utf-8") as f:
                f.write(srt_18chars)
            print(f"✅ 已生成: elevenlabs_multispeaker_18chars.srt")
            
            # 2. 帶說話者標識的 SRT（如果有說話者資訊）
            if speakers_found:
                srt_with_speakers = generate_srt_with_speakers(words, max_chars=40)
                with open("elevenlabs_multispeaker_with_speakers.srt", "w", encoding="utf-8") as f:
                    f.write(srt_with_speakers)
                print(f"✅ 已生成: elevenlabs_multispeaker_with_speakers.srt")
            
            print(f"\n💾 完整結果已保存: {output_file}")
            
            return {
                'success': True,
                'word_count': len(words),
                'speaker_count': len(speakers_found),
                'speakers': list(speakers_found),
                'processing_time': elapsed_time,
                'text_length': len(result.get('text', '')),
                'language': result.get('language_code', 'N/A'),
                'language_probability': result.get('language_probability', 0),
                'audio_events_count': len(audio_events),
                'word_types': word_types
            }
        else:
            print(f"❌ 轉錄失敗: {response.status_code}")
            print(f"   錯誤訊息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 異常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_srt_from_words(words, max_chars=18):
    """從詞彙級時間戳記生成 SRT（控制字數）"""
    srt_content = ""
    segment_index = 1
    current_segment = []
    current_text = ""
    segment_start = None
    
    for word in words:
        # 只處理 word 類型，跳過 spacing 和 audio_event
        if word.get('type') != 'word':
            continue
        
        word_text = word.get('text', '')
        word_start = word.get('start', 0)
        word_end = word.get('end', 0)
        
        if segment_start is None:
            segment_start = word_start
        
        # 檢查加入這個詞後是否超過字數限制
        potential_text = current_text + word_text
        if len(potential_text) > max_chars and current_segment:
            # 生成當前段落
            segment_end = current_segment[-1].get('end', word_start)
            srt_content += format_srt_segment(segment_index, segment_start, segment_end, current_text)
            
            # 開始新段落
            segment_index += 1
            current_segment = [word]
            current_text = word_text
            segment_start = word_start
        else:
            current_segment.append(word)
            current_text = potential_text
    
    # 處理最後一個段落
    if current_segment:
        segment_end = current_segment[-1].get('end', segment_start)
        srt_content += format_srt_segment(segment_index, segment_start, segment_end, current_text)
    
    return srt_content

def generate_srt_with_speakers(words, max_chars=40):
    """生成帶說話者標識的 SRT"""
    srt_content = ""
    segment_index = 1
    current_speaker = None
    current_segment = []
    current_text = ""
    segment_start = None
    
    for word in words:
        # 只處理 word 類型
        if word.get('type') != 'word':
            continue
        
        word_text = word.get('text', '')
        word_start = word.get('start', 0)
        word_end = word.get('end', 0)
        speaker = word.get('speaker_id', 'Unknown')
        
        # 如果說話者改變或超過字數限制，開始新段落
        if (current_speaker and speaker != current_speaker) or \
           (len(current_text + word_text) > max_chars and current_segment):
            # 生成當前段落
            segment_end = current_segment[-1].get('end', word_start)
            text_with_speaker = f"[{current_speaker}] {current_text}"
            srt_content += format_srt_segment(segment_index, segment_start, segment_end, text_with_speaker)
            
            # 開始新段落
            segment_index += 1
            current_segment = [word]
            current_text = word_text
            segment_start = word_start
            current_speaker = speaker
        else:
            if segment_start is None:
                segment_start = word_start
            if current_speaker is None:
                current_speaker = speaker
            current_segment.append(word)
            current_text += word_text
    
    # 處理最後一個段落
    if current_segment:
        segment_end = current_segment[-1].get('end', segment_start)
        text_with_speaker = f"[{current_speaker}] {current_text}"
        srt_content += format_srt_segment(segment_index, segment_start, segment_end, text_with_speaker)
    
    return srt_content

def format_srt_segment(index, start_sec, end_sec, text):
    """格式化 SRT 段落（時間單位：秒）"""
    start_time = format_srt_time(start_sec)
    end_time = format_srt_time(end_sec)
    
    return f"{index}\n{start_time} --> {end_time}\n{text}\n\n"

def format_srt_time(seconds):
    """將秒轉換為 SRT 時間格式 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def main():
    """主測試函數"""
    print(f"\n{'='*80}")
    print(f"🎯 ElevenLabs Scribe V1 多人辨識正確測試")
    print(f"{'='*80}")
    print(f"官方文檔確認: 支援最多 32 個說話者辨識")
    print(f"來源: https://elevenlabs.io/docs/capabilities/speech-to-text")
    print(f"{'='*80}")
    print(f"測試音檔: ../multispeaker-test.mp3")
    print(f"測試日期: 2025年10月19日")
    print(f"{'='*80}")
    
    # 檢查音檔
    audio_file = "../multispeaker-test.mp3"
    if not os.path.exists(audio_file):
        audio_file = "../multispeaker-test.MP3"
        if not os.path.exists(audio_file):
            print(f"❌ 錯誤: 找不到音檔")
            return
    
    print(f"✅ 找到測試音檔: {audio_file}")
    
    # 獲取 API Key
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not elevenlabs_key:
        print("❌ 錯誤: ELEVENLABS_API_KEY 未設定")
        return
    
    print(f"✅ API Key 已載入: {elevenlabs_key[:10]}...")
    
    # 執行測試
    result = test_elevenlabs_speaker_diarization(elevenlabs_key, audio_file)
    
    if result:
        print(f"\n{'='*80}")
        print(f"🎉 測試完成！")
        print(f"{'='*80}")
        print(f"\n📊 測試摘要:")
        print(f"   ✅ 詞彙級時間戳記: {result['word_count']} 個詞彙")
        print(f"   ✅ 多人辨識: {result['speaker_count']} 個說話者")
        print(f"   ⏱️  處理時間: {result['processing_time']:.2f} 秒")
        print(f"   📝 文字長度: {result['text_length']} 字符")
        print(f"   🌍 語言: {result['language']} ({result['language_probability']*100:.1f}%)")
        print(f"   🎵 音頻事件: {result['audio_events_count']} 個")
        
        if result['speakers']:
            print(f"\n🎤 檢測到的說話者: {', '.join(result['speakers'])}")
        else:
            print(f"\n⚠️  未檢測到多個說話者（可能是單人音檔）")
        
        print(f"\n📁 生成的檔案:")
        print(f"   1. elevenlabs_multispeaker_correct_result.json (完整結果)")
        print(f"   2. elevenlabs_multispeaker_18chars.srt (18字符段落)")
        if result['speakers']:
            print(f"   3. elevenlabs_multispeaker_with_speakers.srt (帶說話者標識)")
    else:
        print(f"\n❌ 測試失敗")

if __name__ == "__main__":
    main()



