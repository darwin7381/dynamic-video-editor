#!/usr/bin/env python3
"""
最終段落級 vs 詞彙級詳細比較分析
使用實際成功生成的文件
"""

import os
import re

def parse_srt_file(filepath):
    """解析 SRT 文件並返回段落信息"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        # 分割成段落塊
        blocks = content.split('\n\n')
        segments = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                segment_id = lines[0]
                timestamp = lines[1]
                text = lines[2]
                
                segments.append({
                    'id': segment_id,
                    'timestamp': timestamp,
                    'text': text,
                    'length': len(text)
                })
        
        return segments
    except Exception as e:
        print(f"❌ 無法解析 {filepath}: {str(e)}")
        return []

def analyze_segments(segments, name):
    """分析段落特性"""
    if not segments:
        return None
    
    lengths = [seg['length'] for seg in segments]
    long_segments = [seg for seg in segments if seg['length'] > 25]
    very_long_segments = [seg for seg in segments if seg['length'] > 35]
    
    analysis = {
        'name': name,
        'total_segments': len(segments),
        'avg_length': sum(lengths) / len(lengths),
        'max_length': max(lengths),
        'min_length': min(lengths),
        'long_segments_count': len(long_segments),
        'very_long_segments_count': len(very_long_segments),
        'long_segments': long_segments,
        'very_long_segments': very_long_segments,
        'all_segments': segments
    }
    
    # 評分邏輯：基礎60分，每個長段落扣5分，每個超長段落扣10分
    score = 60 - (len(long_segments) * 5) - (len(very_long_segments) * 5)
    analysis['score'] = max(0, score)
    
    return analysis

def create_detailed_comparison():
    """創建詳細的段落級 vs 詞彙級比較"""
    print("🎯 段落級 vs 詞彙級最終詳細比較")
    print("=" * 80)
    
    # 定義要比較的文件
    files_to_compare = [
        ("elevenlabs_segment_real.srt", "ElevenLabs 段落級", "segment"),
        ("elevenlabs_precise_18chars.srt", "ElevenLabs 詞彙級", "word"),
        ("assemblyai_precise_18chars.srt", "AssemblyAI 詞彙級", "word"),
        ("final_groq_word_level.srt", "Groq 詞彙級", "word")
    ]
    
    analyses = []
    
    print("📋 解析文件...")
    for filepath, name, type_name in files_to_compare:
        if os.path.exists(filepath):
            print(f"  ✅ 解析 {name}: {filepath}")
            segments = parse_srt_file(filepath)
            analysis = analyze_segments(segments, name)
            if analysis:
                analysis['type'] = type_name
                analysis['filepath'] = filepath
                analyses.append(analysis)
        else:
            print(f"  ❌ 文件不存在: {filepath}")
    
    if not analyses:
        print("❌ 沒有可分析的文件")
        return
    
    # 顯示比較表格
    print(f"\n📊 詳細比較結果:")
    print(f"{'方案':<20} {'類型':<6} {'段落數':<8} {'平均長度':<8} {'最長':<6} {'問題段落':<8} {'評分':<6}")
    print("-" * 80)
    
    for analysis in analyses:
        print(f"{analysis['name']:<20} {analysis['type']:<6} {analysis['total_segments']:<8} "
              f"{analysis['avg_length']:<8.1f} {analysis['max_length']:<6} "
              f"{analysis['long_segments_count']:<8} {analysis['score']:<6.0f}")
    
    # 找出段落級和詞彙級的代表
    segment_level = [a for a in analyses if a['type'] == 'segment']
    word_level = [a for a in analyses if a['type'] == 'word']
    
    if segment_level and word_level:
        print(f"\n🔍 段落級 vs 詞彙級對比:")
        
        # ElevenLabs 段落級 vs 詞彙級
        elevenlabs_segment = next((a for a in segment_level if 'ElevenLabs' in a['name']), None)
        elevenlabs_word = next((a for a in word_level if 'ElevenLabs' in a['name']), None)
        
        if elevenlabs_segment and elevenlabs_word:
            print(f"\n  📈 ElevenLabs 對比:")
            print(f"    段落級: 最長 {elevenlabs_segment['max_length']} 字符, 問題段落 {elevenlabs_segment['long_segments_count']} 個")
            print(f"    詞彙級: 最長 {elevenlabs_word['max_length']} 字符, 問題段落 {elevenlabs_word['long_segments_count']} 個")
            print(f"    改善程度: 最長段落減少 {elevenlabs_segment['max_length'] - elevenlabs_word['max_length']} 字符")
        
        # 詞彙級服務排名
        print(f"\n  🏆 詞彙級服務排名:")
        word_level_sorted = sorted(word_level, key=lambda x: (-x['score'], x['max_length']))
        for i, analysis in enumerate(word_level_sorted, 1):
            print(f"    {i}. {analysis['name']}: {analysis['score']:.0f}/60 (最長 {analysis['max_length']} 字符)")
    
    # 顯示問題段落樣本
    print(f"\n📝 問題段落樣本 (>25字符):")
    for analysis in analyses:
        if analysis['long_segments']:
            print(f"\n  {analysis['name']} 問題段落:")
            for i, seg in enumerate(analysis['long_segments'][:3], 1):  # 只顯示前3個
                print(f"    {i}. {seg['text']} ({seg['length']} 字符)")
    
    # 顯示正常段落樣本
    print(f"\n✅ 正常段落樣本 (≤25字符):")
    for analysis in analyses:
        normal_segments = [seg for seg in analysis['all_segments'] if seg['length'] <= 25]
        if normal_segments:
            print(f"\n  {analysis['name']} 正常段落:")
            for i, seg in enumerate(normal_segments[:3], 1):  # 只顯示前3個
                print(f"    {i}. {seg['text']} ({seg['length']} 字符)")
    
    return analyses

def generate_final_report(analyses):
    """生成最終報告"""
    print(f"\n🏆 最終結論和建議")
    print("=" * 80)
    
    # 分類分析結果
    segment_level = [a for a in analyses if a['type'] == 'segment']
    word_level = [a for a in analyses if a['type'] == 'word']
    
    print(f"📊 測試成功統計:")
    print(f"  段落級測試: {len(segment_level)}/1 個服務成功 (ElevenLabs)")
    print(f"  詞彙級測試: {len(word_level)}/3 個服務成功")
    
    if segment_level and word_level:
        # 找出最佳方案
        best_segment = max(segment_level, key=lambda x: x['score'])
        best_word = max(word_level, key=lambda x: x['score'])
        
        print(f"\n🥇 最佳方案:")
        print(f"  段落級最佳: {best_segment['name']} ({best_segment['score']:.0f}/60)")
        print(f"  詞彙級最佳: {best_word['name']} ({best_word['score']:.0f}/60)")
        
        # 關鍵差異分析
        print(f"\n🔍 關鍵差異:")
        if best_segment['name'].startswith('ElevenLabs') and best_word['name'].startswith('ElevenLabs'):
            print(f"  同一服務 (ElevenLabs) 比較:")
            print(f"    段落級: 最長 {best_segment['max_length']} 字符, 問題段落 {best_segment['long_segments_count']} 個")
            print(f"    詞彙級: 最長 {best_word['max_length']} 字符, 問題段落 {best_word['long_segments_count']} 個")
            
            improvement = best_segment['max_length'] - best_word['max_length']
            print(f"    詞彙級改善: 最長段落減少 {improvement} 字符")
            
            if improvement > 0:
                print(f"    ✅ 詞彙級明顯優於段落級")
            else:
                print(f"    ⚠️ 段落級表現相當")
    
    # 針對用戶需求的建議
    print(f"\n💡 針對您需求的建議:")
    print(f"  您的原始問題: Whisper-1 段落過長 (19字符)")
    
    if segment_level:
        segment_max = segment_level[0]['max_length']
        print(f"  段落級結果: 最長 {segment_max} 字符 ({'問題更嚴重' if segment_max > 19 else '有所改善'})")
    
    if word_level:
        word_max = min(a['max_length'] for a in word_level)
        print(f"  詞彙級結果: 最長 {word_max} 字符 ({'完美解決' if word_max <= 18 else '大幅改善'})")
    
    print(f"\n🎯 最終推薦:")
    if word_level:
        best_word = max(word_level, key=lambda x: x['score'])
        print(f"  🏆 推薦方案: {best_word['name']}")
        print(f"  📁 文件位置: {best_word['filepath']}")
        print(f"  ✅ 評分: {best_word['score']:.0f}/60")
        print(f"  ✅ 最長段落: {best_word['max_length']} 字符")
        print(f"  ✅ 問題段落: {best_word['long_segments_count']} 個")
    
    print(f"\n📁 所有測試文件位置:")
    for analysis in analyses:
        print(f"  - {analysis['filepath']} ({analysis['name']})")

def main():
    """主函數"""
    print("🔍 段落級 vs 詞彙級最終比較分析")
    print("使用實際成功生成的文件進行比較")
    print("=" * 80)
    
    # 檢查文件存在性
    test_files = [
        "elevenlabs_segment_real.srt",
        "elevenlabs_precise_18chars.srt",
        "assemblyai_precise_18chars.srt",
        "final_groq_word_level.srt"
    ]
    
    existing_files = [f for f in test_files if os.path.exists(f)]
    print(f"📋 可用文件: {len(existing_files)}/{len(test_files)}")
    
    if len(existing_files) < 2:
        print("❌ 可用文件太少，無法進行有效比較")
        return
    
    # 執行詳細比較
    analyses = create_detailed_comparison()
    
    if analyses:
        # 生成最終報告
        generate_final_report(analyses)
        
        print(f"\n✅ 段落級 vs 詞彙級比較分析完成！")
        print(f"📊 成功分析了 {len(analyses)} 個文件")
    else:
        print(f"❌ 分析失敗")

if __name__ == "__main__":
    main()
