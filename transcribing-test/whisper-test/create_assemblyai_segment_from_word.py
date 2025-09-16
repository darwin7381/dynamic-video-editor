#!/usr/bin/env python3
"""
從 AssemblyAI 詞彙級結果創建段落級版本
模擬真實的段落級分割
"""

import os
import json
from datetime import timedelta

def format_time(seconds):
    """將秒數轉換為 SRT 時間格式"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = td.total_seconds() % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def parse_srt_to_words(srt_filepath):
    """從 SRT 文件解析出詞彙級數據"""
    try:
        with open(srt_filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        blocks = content.split('\n\n')
        words = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # 解析時間戳
                timestamp_line = lines[1]
                start_str, end_str = timestamp_line.split(' --> ')
                
                # 轉換時間為秒
                def time_to_seconds(time_str):
                    time_str = time_str.replace(',', '.')
                    parts = time_str.split(':')
                    return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                
                start_time = time_to_seconds(start_str)
                end_time = time_to_seconds(end_str)
                text = lines[2]
                
                words.append({
                    'text': text,
                    'start': start_time,
                    'end': end_time,
                    'duration': end_time - start_time
                })
        
        return words
    except Exception as e:
        print(f"❌ 無法解析 SRT 文件: {str(e)}")
        return []

def create_natural_segments_from_words(words, target_length=30):
    """從詞彙級數據創建自然的段落級分割"""
    if not words:
        return []
    
    segments = []
    current_segment = {
        'text': '',
        'start': words[0]['start'],
        'end': words[0]['end']
    }
    
    for word in words:
        # 添加當前詞彙到段落
        current_segment['text'] += word['text']
        current_segment['end'] = word['end']
        
        # 判斷是否應該結束當前段落
        should_end_segment = False
        
        # 條件1: 遇到句號等結束符號
        if word['text'].endswith(('。', '！', '？', '.', '!', '?')):
            should_end_segment = True
        
        # 條件2: 長度超過目標長度且遇到逗號或其他停頓
        elif (len(current_segment['text']) > target_length and 
              word['text'].endswith(('，', '、', ',', ';', ':'))) :
            should_end_segment = True
        
        # 條件3: 長度超過最大限制
        elif len(current_segment['text']) > target_length * 1.5:
            should_end_segment = True
        
        if should_end_segment and current_segment['text'].strip():
            segments.append(current_segment.copy())
            
            # 開始新段落
            word_idx = words.index(word)
            if word_idx < len(words) - 1:
                next_word = words[word_idx + 1]
                current_segment = {
                    'text': '',
                    'start': next_word['start'],
                    'end': next_word['end']
                }
    
    # 添加最後一個段落
    if current_segment['text'].strip():
        segments.append(current_segment)
    
    return segments

def create_assemblyai_segment_from_existing():
    """從現有的 AssemblyAI 詞彙級結果創建段落級版本"""
    print(f"\n🚀 從 AssemblyAI 詞彙級創建段落級版本")
    print("=" * 60)
    
    # 檢查現有的 AssemblyAI 詞彙級文件
    word_level_file = "assemblyai_precise_18chars.srt"
    
    if not os.path.exists(word_level_file):
        print(f"❌ AssemblyAI 詞彙級文件不存在: {word_level_file}")
        return None
    
    print(f"✅ 讀取 AssemblyAI 詞彙級文件: {word_level_file}")
    
    # 解析詞彙級數據
    words = parse_srt_to_words(word_level_file)
    if not words:
        print(f"❌ 無法解析詞彙級數據")
        return None
    
    print(f"📝 解析得到 {len(words)} 個詞彙級段落")
    
    # 創建自然的段落級分割
    segments = create_natural_segments_from_words(words, target_length=25)
    print(f"🔄 創建了 {len(segments)} 個段落級段落")
    
    # 生成段落級 SRT
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
    
    # 創建結果數據
    result_data = {
        'source': 'converted_from_word_level',
        'original_file': word_level_file,
        'segments': segments,
        'segment_type': 'natural_sentences',
        'conversion_method': 'automatic_sentence_splitting'
    }
    
    # 保存結果數據
    with open("assemblyai_segment_real_result.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"💾 結果數據已保存: assemblyai_segment_real_result.json")
    
    # 分析段落特性
    lengths = [len(seg['text'].strip()) for seg in segments]
    print(f"📊 AssemblyAI 段落級分析:")
    print(f"  段落類型: 自然句子分割")
    print(f"  總段落數: {len(segments)}")
    print(f"  平均長度: {sum(lengths) / len(lengths):.1f} 字符")
    print(f"  最長段落: {max(lengths)} 字符")
    print(f"  最短段落: {min(lengths)} 字符")
    print(f"  長段落數: {sum(1 for l in lengths if l > 25)} 個 (>25字符)")
    
    # 顯示前幾個段落樣本
    print(f"\n📝 前5個段落樣本:")
    for i, seg in enumerate(segments[:5], 1):
        text = seg['text'].strip()
        print(f"  {i}. {text} ({len(text)} 字符)")
    
    return result_data

def main():
    """主函數"""
    print("🎯 AssemblyAI 段落級創建 (從詞彙級轉換)")
    print("=" * 80)
    
    result = create_assemblyai_segment_from_existing()
    
    if result:
        print(f"\n✅ AssemblyAI 段落級創建成功！")
        print(f"📁 生成的文件:")
        print(f"  - assemblyai_segment_real.srt (段落級 SRT)")
        print(f"  - assemblyai_segment_real_result.json (結果數據)")
    else:
        print(f"\n❌ AssemblyAI 段落級創建失敗")
    
    return result

if __name__ == "__main__":
    main()
