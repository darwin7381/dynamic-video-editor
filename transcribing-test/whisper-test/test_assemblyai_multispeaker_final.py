#!/usr/bin/env python3
"""
AssemblyAI 多人辨識完整測試
使用儲值後的新 API Key
"""

import os
import sys
from dotenv import load_dotenv
import requests
import json
import time

# 載入環境變數
load_dotenv()

def test_assemblyai_multispeaker_complete(api_key, audio_file):
    """完整測試 AssemblyAI 的多人辨識功能"""
    print(f"\n{'='*80}")
    print(f"🟢 AssemblyAI Universal-1 完整多人辨識測試")
    print(f"{'='*80}")
    
    try:
        # 步驟1: 上傳音檔
        print("\n📤 步驟1: 上傳音檔...")
        upload_url = "https://api.assemblyai.com/v2/upload"
        headers = {"authorization": api_key}
        
        with open(audio_file, 'rb') as f:
            upload_response = requests.post(upload_url, headers=headers, data=f)
        
        if upload_response.status_code != 200:
            print(f"❌ 上傳失敗: {upload_response.status_code}")
            print(f"   錯誤訊息: {upload_response.text}")
            return None
        
        audio_url = upload_response.json()['upload_url']
        print(f"✅ 上傳成功")
        print(f"   音檔 URL: {audio_url[:50]}...")
        
        # 步驟2: 創建轉錄任務（開啟所有相關功能）
        print("\n🚀 步驟2: 創建轉錄任務（開啟多人辨識）...")
        transcript_url = "https://api.assemblyai.com/v2/transcript"
        
        data = {
            "audio_url": audio_url,
            "language_code": "zh",
            "speaker_labels": True,  # 開啟多人辨識
            "punctuate": True,       # 自動標點
            "format_text": True      # 格式化文字
        }
        
        start_time = time.time()
        transcript_response = requests.post(transcript_url, json=data, headers=headers)
        
        if transcript_response.status_code != 200:
            print(f"❌ 創建任務失敗: {transcript_response.status_code}")
            print(f"   錯誤訊息: {transcript_response.text}")
            return None
        
        transcript_id = transcript_response.json()['id']
        print(f"✅ 任務已創建")
        print(f"   任務 ID: {transcript_id}")
        
        # 步驟3: 輪詢結果
        print("\n⏳ 步驟3: 等待轉錄完成...")
        polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        
        poll_count = 0
        while True:
            poll_count += 1
            time.sleep(3)
            
            polling_response = requests.get(polling_url, headers=headers)
            result = polling_response.json()
            status = result['status']
            
            if poll_count % 5 == 0:
                print(f"   輪詢中... ({poll_count}次，狀態: {status})")
            
            if status == 'completed':
                elapsed_time = time.time() - start_time
                print(f"\n✅ 轉錄完成！")
                print(f"⏱️  總處理時間: {elapsed_time:.2f} 秒")
                break
            elif status == 'error':
                print(f"❌ 轉錄錯誤: {result.get('error', 'Unknown error')}")
                return None
        
        # 步驟4: 保存完整結果
        print("\n💾 步驟4: 保存結果...")
        with open("assemblyai_multispeaker_complete_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ 完整結果已保存: assemblyai_multispeaker_complete_result.json")
        
        # 步驟5: 分析結果
        print(f"\n{'='*80}")
        print(f"📊 轉錄結果分析")
        print(f"{'='*80}")
        
        print(f"\n📝 基本資訊:")
        print(f"   文字長度: {len(result.get('text', ''))} 字符")
        print(f"   語言: {result.get('language_code', 'N/A')}")
        print(f"   音檔時長: {result.get('audio_duration', 0)} 秒")
        
        # 檢查詞彙級時間戳記
        words = result.get('words', [])
        print(f"\n📊 詞彙級時間戳記:")
        print(f"   支援狀態: {'✅ 支援' if words else '❌ 不支援'}")
        print(f"   總詞彙數: {len(words)}")
        if words:
            print(f"   第一個詞彙: {words[0]}")
            print(f"   最後一個詞彙: {words[-1]}")
        
        # 檢查多人辨識
        speakers_found = set()
        speaker_word_counts = {}
        
        for word in words:
            if 'speaker' in word:
                speaker = word['speaker']
                speakers_found.add(speaker)
                speaker_word_counts[speaker] = speaker_word_counts.get(speaker, 0) + 1
        
        print(f"\n🎤 多人辨識:")
        print(f"   支援狀態: {'✅ 支援' if speakers_found else '❌ 未檢測到'}")
        print(f"   檢測到說話者數量: {len(speakers_found)}")
        
        if speakers_found:
            print(f"   說話者列表: {sorted(speakers_found)}")
            print(f"\n   各說話者詞彙數量:")
            for speaker in sorted(speakers_found):
                count = speaker_word_counts[speaker]
                percentage = (count / len(words)) * 100
                print(f"     {speaker}: {count} 個詞彙 ({percentage:.1f}%)")
        
        # 檢查 Utterances
        utterances = result.get('utterances', [])
        print(f"\n💬 Utterances (按說話者分組的完整句子):")
        print(f"   總數量: {len(utterances)}")
        
        if utterances:
            print(f"\n   前5個 Utterances:")
            for i, utt in enumerate(utterances[:5], 1):
                speaker = utt.get('speaker', 'Unknown')
                text = utt.get('text', '')
                start = utt.get('start', 0) / 1000  # 轉換為秒
                end = utt.get('end', 0) / 1000
                print(f"   {i}. [{speaker}] ({start:.1f}s - {end:.1f}s)")
                print(f"      {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # 生成 SRT 檔案
        print(f"\n📝 生成 SRT 字幕檔...")
        srt_content = generate_srt_from_words(words, max_chars=18)
        
        with open("assemblyai_multispeaker_18chars.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        print(f"✅ SRT 檔案已生成: assemblyai_multispeaker_18chars.srt")
        
        # 生成帶說話者標識的 SRT
        if utterances:
            srt_with_speakers = generate_srt_with_speakers(utterances, max_chars=18)
            with open("assemblyai_multispeaker_with_speakers.srt", "w", encoding="utf-8") as f:
                f.write(srt_with_speakers)
            print(f"✅ 帶說話者標識的 SRT 已生成: assemblyai_multispeaker_with_speakers.srt")
        
        return {
            'success': True,
            'word_count': len(words),
            'speaker_count': len(speakers_found),
            'speakers': list(speakers_found),
            'utterances_count': len(utterances),
            'processing_time': elapsed_time,
            'text_length': len(result.get('text', '')),
            'audio_duration': result.get('audio_duration', 0)
        }
        
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

def generate_srt_with_speakers(utterances, max_chars=40):
    """從 utterances 生成帶說話者標識的 SRT"""
    srt_content = ""
    
    for i, utt in enumerate(utterances, 1):
        speaker = utt.get('speaker', 'Unknown')
        text = utt.get('text', '')
        start = utt.get('start', 0)
        end = utt.get('end', 0)
        
        # 在文字前加上說話者標識
        text_with_speaker = f"[{speaker}] {text}"
        
        srt_content += format_srt_segment(i, start, end, text_with_speaker)
    
    return srt_content

def format_srt_segment(index, start_ms, end_ms, text):
    """格式化 SRT 段落"""
    start_time = format_srt_time(start_ms)
    end_time = format_srt_time(end_ms)
    
    return f"{index}\n{start_time} --> {end_time}\n{text}\n\n"

def format_srt_time(milliseconds):
    """將毫秒轉換為 SRT 時間格式 (HH:MM:SS,mmm)"""
    seconds = int(milliseconds / 1000)
    ms = int(milliseconds % 1000)
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def main():
    """主測試函數"""
    print(f"\n{'='*80}")
    print(f"🎯 AssemblyAI Universal-1 多人辨識完整測試")
    print(f"{'='*80}")
    print(f"測試音檔: ../multispeaker-test.mp3")
    print(f"測試日期: 2025年10月19日")
    print(f"{'='*80}")
    
    # 檢查音檔
    audio_file = "../multispeaker-test.mp3"
    if not os.path.exists(audio_file):
        # 嘗試其他位置
        audio_file = "../multispeaker-test.MP3"
        if not os.path.exists(audio_file):
            print(f"❌ 錯誤: 找不到音檔")
            print(f"   嘗試了: ../multispeaker-test.mp3 和 ../multispeaker-test.MP3")
            return
    
    print(f"✅ 找到測試音檔: {audio_file}")
    
    # 獲取 API Key（嘗試兩個 key）
    assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
    assemblyai_key_2 = os.getenv("ASSEMBLYAI_API_KEY_2")
    
    # 嘗試第一個 key
    if assemblyai_key:
        print(f"✅ API Key 1 已載入: {assemblyai_key[:10]}...")
        test_key = assemblyai_key
    elif assemblyai_key_2:
        print(f"✅ API Key 2 已載入: {assemblyai_key_2[:10]}...")
        test_key = assemblyai_key_2
    else:
        print("❌ 錯誤: ASSEMBLYAI_API_KEY 未設定")
        print("請在 .env 檔案中設定 ASSEMBLYAI_API_KEY")
        return
    
    # 嘗試第一個 key
    result = test_assemblyai_multispeaker_complete(test_key, audio_file)
    
    # 如果第一個失敗，嘗試第二個
    if result is None and assemblyai_key and assemblyai_key_2 and test_key == assemblyai_key:
        print(f"\n⚠️  第一個 API Key 失敗，嘗試第二個...")
        print(f"✅ 使用 API Key 2: {assemblyai_key_2[:10]}...")
        result = test_assemblyai_multispeaker_complete(assemblyai_key_2, audio_file)
    
    if result:
        print(f"\n{'='*80}")
        print(f"🎉 測試完成！")
        print(f"{'='*80}")
        print(f"\n📊 測試摘要:")
        print(f"   ✅ 詞彙級時間戳記: {result['word_count']} 個詞彙")
        print(f"   ✅ 多人辨識: {result['speaker_count']} 個說話者")
        print(f"   ✅ Utterances: {result['utterances_count']} 段")
        print(f"   ⏱️  處理時間: {result['processing_time']:.2f} 秒")
        print(f"   📝 文字長度: {result['text_length']} 字符")
        print(f"   🎵 音檔時長: {result['audio_duration']} 秒")
        
        if result['speakers']:
            print(f"\n🎤 檢測到的說話者: {', '.join(result['speakers'])}")
        
        print(f"\n📁 生成的檔案:")
        print(f"   1. assemblyai_multispeaker_complete_result.json (完整結果)")
        print(f"   2. assemblyai_multispeaker_18chars.srt (18字符段落)")
        print(f"   3. assemblyai_multispeaker_with_speakers.srt (帶說話者標識)")
    else:
        print(f"\n❌ 測試失敗")

if __name__ == "__main__":
    main()

