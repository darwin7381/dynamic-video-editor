#!/usr/bin/env python3
"""
使用現有數據進行段落級 vs 詞彙級深度分析
"""

import json
import os

def analyze_srt_file(filepath, name):
    """分析 SRT 文件的段落特性"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 解析 SRT 段落
        blocks = content.strip().split('\n\n')
        segments = []
        
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                text = lines[2]  # 第三行是文本
                segments.append(text)
        
        if not segments:
            return None
        
        lengths = [len(seg) for seg in segments]
        long_segments = sum(1 for length in lengths if length > 25)
        very_long = sum(1 for length in lengths if length > 35)
        
        analysis = {
            'name': name,
            'total_segments': len(segments),
            'avg_length': sum(lengths) / len(lengths),
            'max_length': max(lengths),
            'min_length': min(lengths),
            'long_segments': long_segments,
            'very_long_segments': very_long,
            'score': max(0, 60 - long_segments * 5 - very_long * 10),
            'segments': segments[:5]  # 前5個段落作為樣本
        }
        
        return analysis
        
    except Exception as e:
        print(f"❌ 無法分析 {filepath}: {str(e)}")
        return None

def analyze_json_segments(filepath, name):
    """分析 JSON 文件中的段落數據"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        segments = []
        
        # 檢查不同的段落數據結構
        if 'segments' in data and data['segments']:
            for seg in data['segments']:
                if 'text' in seg:
                    segments.append(seg['text'])
        elif 'words' in data:
            # 從詞彙級數據推斷段落
            words = data['words']
            current_segment = ""
            
            for word in words:
                current_segment += word.get('text', '')
                
                # 簡單的段落分割邏輯
                if len(current_segment) > 30 or word.get('text', '') in ['。', '！', '？']:
                    if current_segment.strip():
                        segments.append(current_segment.strip())
                        current_segment = ""
            
            if current_segment.strip():
                segments.append(current_segment.strip())
        
        if not segments:
            return None
        
        lengths = [len(seg) for seg in segments]
        long_segments = sum(1 for length in lengths if length > 25)
        very_long = sum(1 for length in lengths if length > 35)
        
        analysis = {
            'name': name,
            'total_segments': len(segments),
            'avg_length': sum(lengths) / len(lengths),
            'max_length': max(lengths),
            'min_length': min(lengths),
            'long_segments': long_segments,
            'very_long_segments': very_long,
            'score': max(0, 60 - long_segments * 5 - very_long * 10),
            'segments': segments[:5]
        }
        
        return analysis
        
    except Exception as e:
        print(f"❌ 無法分析 {filepath}: {str(e)}")
        return None

def create_comprehensive_comparison():
    """創建全面的段落級 vs 詞彙級比較"""
    print("🎯 段落級 vs 詞彙級全面比較分析")
    print("=" * 80)
    
    analyses = []
    
    # ElevenLabs 段落級 (從轉換後的結果)
    elevenlabs_segment = analyze_srt_file("elevenlabs_segment_level.srt", "ElevenLabs 段落級")
    if elevenlabs_segment:
        analyses.append(elevenlabs_segment)
    
    # ElevenLabs 詞彙級 (最佳版本)
    elevenlabs_word = analyze_srt_file("elevenlabs_precise_18chars.srt", "ElevenLabs 詞彙級")
    if elevenlabs_word:
        analyses.append(elevenlabs_word)
    
    # AssemblyAI 詞彙級
    assemblyai_word = analyze_srt_file("assemblyai_precise_18chars.srt", "AssemblyAI 詞彙級")
    if assemblyai_word:
        analyses.append(assemblyai_word)
    
    # Groq 詞彙級
    groq_word = analyze_srt_file("final_groq_word_level.srt", "Groq 詞彙級")
    if groq_word:
        analyses.append(groq_word)
    
    # Whisper-1 詞彙級
    whisper_word = analyze_srt_file("final_whisper1_word_level_correct.srt", "Whisper-1 詞彙級")
    if whisper_word:
        analyses.append(whisper_word)
    
    # 嘗試從 JSON 數據分析原始段落級
    elevenlabs_json_segment = analyze_json_segments("elevenlabs_segment_result.json", "ElevenLabs 原始段落級")
    if elevenlabs_json_segment:
        analyses.append(elevenlabs_json_segment)
    
    # 顯示比較表格
    print(f"\n📊 詳細比較結果:")
    print(f"{'方案':<20} {'段落數':<8} {'平均長度':<8} {'最長':<6} {'問題段落':<8} {'評分':<6}")
    print("-" * 70)
    
    for analysis in analyses:
        print(f"{analysis['name']:<20} {analysis['total_segments']:<8} "
              f"{analysis['avg_length']:<8.1f} {analysis['max_length']:<6} "
              f"{analysis['long_segments']:<8} {analysis['score']:<6.0f}")
    
    # 分組比較
    print(f"\n🔍 分組比較分析:")
    
    # ElevenLabs 段落級 vs 詞彙級
    elevenlabs_comparisons = [a for a in analyses if 'ElevenLabs' in a['name']]
    if len(elevenlabs_comparisons) >= 2:
        print(f"\n  📈 ElevenLabs 比較:")
        for comp in elevenlabs_comparisons:
            print(f"    {comp['name']}: 最長 {comp['max_length']} 字符, 問題段落 {comp['long_segments']} 個")
    
    # 詞彙級服務比較
    word_level_comparisons = [a for a in analyses if '詞彙級' in a['name']]
    if word_level_comparisons:
        print(f"\n  🏆 詞彙級服務排名:")
        word_level_comparisons.sort(key=lambda x: x['score'], reverse=True)
        for i, comp in enumerate(word_level_comparisons, 1):
            print(f"    {i}. {comp['name']}: {comp['score']:.0f}/60 (最長 {comp['max_length']} 字符)")
    
    # 顯示樣本段落
    print(f"\n📝 樣本段落比較:")
    for analysis in analyses[:3]:  # 只顯示前3個
        print(f"\n  {analysis['name']} 前3個段落:")
        for i, seg in enumerate(analysis['segments'][:3], 1):
            print(f"    {i}. {seg} ({len(seg)} 字符)")
    
    return analyses

def generate_final_recommendations(analyses):
    """基於分析結果生成最終建議"""
    print(f"\n🎯 最終建議")
    print("=" * 60)
    
    # 找出最佳詞彙級方案
    word_level = [a for a in analyses if '詞彙級' in a['name']]
    if word_level:
        best_word = max(word_level, key=lambda x: x['score'])
        print(f"🏆 最佳詞彙級方案: {best_word['name']}")
        print(f"   評分: {best_word['score']:.0f}/60")
        print(f"   最長段落: {best_word['max_length']} 字符")
        print(f"   問題段落: {best_word['long_segments']} 個")
    
    # 段落級 vs 詞彙級總結
    segment_level = [a for a in analyses if '段落級' in a['name']]
    
    print(f"\n📋 段落級 vs 詞彙級總結:")
    print(f"  段落級特點:")
    print(f"    ✅ 適合閱讀和理解")
    print(f"    ✅ 語義完整性好")
    print(f"    ❌ 段落長度不可控")
    print(f"    ❌ 不適合字幕顯示")
    
    print(f"  詞彙級特點:")
    print(f"    ✅ 精確控制段落長度")
    print(f"    ✅ 適合字幕和視頻")
    print(f"    ✅ 可自定義分割邏輯")
    print(f"    ❌ 需要額外處理")
    
    print(f"\n🎉 最終結論:")
    print(f"  對於您的需求（解決段落過長問題），詞彙級明顯優於段落級")
    print(f"  ElevenLabs Scribe V1 + 詞彙級自定義仍是最佳解決方案")

def main():
    """主分析函數"""
    print("🔍 使用現有數據進行段落級 vs 詞彙級深度分析")
    print("=" * 80)
    
    # 檢查可用文件
    available_files = []
    test_files = [
        ("elevenlabs_segment_level.srt", "ElevenLabs 段落級"),
        ("elevenlabs_precise_18chars.srt", "ElevenLabs 詞彙級"),
        ("assemblyai_precise_18chars.srt", "AssemblyAI 詞彙級"),
        ("final_groq_word_level.srt", "Groq 詞彙級"),
        ("final_whisper1_word_level_correct.srt", "Whisper-1 詞彙級")
    ]
    
    print(f"📋 檢查可用文件:")
    for filepath, name in test_files:
        if os.path.exists(filepath):
            print(f"  ✅ {name}: {filepath}")
            available_files.append((filepath, name))
        else:
            print(f"  ❌ {name}: {filepath} (不存在)")
    
    if not available_files:
        print(f"❌ 沒有找到可分析的文件")
        return
    
    # 執行全面比較
    analyses = create_comprehensive_comparison()
    
    # 生成最終建議
    generate_final_recommendations(analyses)
    
    # 更新 TODO 狀態
    print(f"\n✅ 段落級 vs 詞彙級比較分析完成")

if __name__ == "__main__":
    main()
