#!/usr/bin/env python3
"""
完整的段落級 vs 詞彙級比較分析
包含 ElevenLabs, AssemblyAI, Groq 三個服務
"""

import os
import json

def parse_srt_file(filepath):
    """解析 SRT 文件並返回段落信息"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
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

def analyze_segments(segments, name, service, level_type):
    """分析段落特性"""
    if not segments:
        return None
    
    lengths = [seg['length'] for seg in segments]
    long_segments = [seg for seg in segments if seg['length'] > 25]
    very_long_segments = [seg for seg in segments if seg['length'] > 35]
    
    # 評分邏輯：基礎60分，每個長段落扣5分，每個超長段落扣額外5分
    score = 60 - (len(long_segments) * 5) - (len(very_long_segments) * 5)
    
    analysis = {
        'name': name,
        'service': service,
        'level_type': level_type,
        'total_segments': len(segments),
        'avg_length': sum(lengths) / len(lengths),
        'max_length': max(lengths),
        'min_length': min(lengths),
        'long_segments_count': len(long_segments),
        'very_long_segments_count': len(very_long_segments),
        'score': max(0, score),
        'long_segments': long_segments,
        'very_long_segments': very_long_segments,
        'all_segments': segments
    }
    
    return analysis

def create_complete_comparison():
    """創建完整的三服務比較"""
    print("🎯 完整段落級 vs 詞彙級比較分析")
    print("=" * 80)
    
    # 定義所有要比較的文件
    files_to_compare = [
        # 段落級文件
        ("elevenlabs_segment_real.srt", "ElevenLabs 段落級", "ElevenLabs", "segment"),
        ("assemblyai_segment_real.srt", "AssemblyAI 段落級", "AssemblyAI", "segment"),
        
        # 詞彙級文件
        ("elevenlabs_precise_18chars.srt", "ElevenLabs 詞彙級", "ElevenLabs", "word"),
        ("assemblyai_precise_18chars.srt", "AssemblyAI 詞彙級", "AssemblyAI", "word"),
        ("final_groq_word_level.srt", "Groq 詞彙級", "Groq", "word")
    ]
    
    analyses = []
    
    print("📋 解析所有文件...")
    for filepath, name, service, level_type in files_to_compare:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✅ 解析 {name}: {filepath} ({file_size} bytes)")
            segments = parse_srt_file(filepath)
            analysis = analyze_segments(segments, name, service, level_type)
            if analysis:
                analysis['filepath'] = filepath
                analyses.append(analysis)
        else:
            print(f"  ❌ 文件不存在: {filepath}")
    
    if not analyses:
        print("❌ 沒有可分析的文件")
        return None
    
    # 顯示完整比較表格
    print(f"\n📊 完整比較結果:")
    print(f"{'服務':<12} {'類型':<6} {'段落數':<8} {'平均長度':<8} {'最長':<6} {'問題段落':<8} {'評分':<6}")
    print("-" * 80)
    
    for analysis in analyses:
        print(f"{analysis['service']:<12} {analysis['level_type']:<6} {analysis['total_segments']:<8} "
              f"{analysis['avg_length']:<8.1f} {analysis['max_length']:<6} "
              f"{analysis['long_segments_count']:<8} {analysis['score']:<6.0f}")
    
    # 按服務分組比較
    print(f"\n🔍 按服務分組比較:")
    services = list(set(a['service'] for a in analyses))
    
    for service in services:
        service_analyses = [a for a in analyses if a['service'] == service]
        if len(service_analyses) >= 2:  # 有段落級和詞彙級
            print(f"\n  📈 {service} 比較:")
            
            segment_analysis = next((a for a in service_analyses if a['level_type'] == 'segment'), None)
            word_analysis = next((a for a in service_analyses if a['level_type'] == 'word'), None)
            
            if segment_analysis and word_analysis:
                print(f"    段落級: 最長 {segment_analysis['max_length']} 字符, 問題段落 {segment_analysis['long_segments_count']} 個, 評分 {segment_analysis['score']:.0f}/60")
                print(f"    詞彙級: 最長 {word_analysis['max_length']} 字符, 問題段落 {word_analysis['long_segments_count']} 個, 評分 {word_analysis['score']:.0f}/60")
                
                improvement = segment_analysis['max_length'] - word_analysis['max_length']
                score_improvement = word_analysis['score'] - segment_analysis['score']
                
                print(f"    改善: 最長段落減少 {improvement} 字符, 評分提升 {score_improvement:.0f} 分")
                
                if improvement > 0 and score_improvement > 0:
                    print(f"    ✅ 詞彙級明顯優於段落級")
                elif improvement > 0:
                    print(f"    ✅ 詞彙級段落控制更好")
                else:
                    print(f"    ⚠️ 差異不明顯")
    
    # 同類型排名
    print(f"\n🏆 同類型服務排名:")
    
    # 段落級排名
    segment_analyses = [a for a in analyses if a['level_type'] == 'segment']
    if segment_analyses:
        print(f"\n  段落級排名:")
        segment_analyses.sort(key=lambda x: (-x['score'], x['max_length']))
        for i, analysis in enumerate(segment_analyses, 1):
            print(f"    {i}. {analysis['name']}: {analysis['score']:.0f}/60 (最長 {analysis['max_length']} 字符)")
    
    # 詞彙級排名
    word_analyses = [a for a in analyses if a['level_type'] == 'word']
    if word_analyses:
        print(f"\n  詞彙級排名:")
        word_analyses.sort(key=lambda x: (-x['score'], x['max_length']))
        for i, analysis in enumerate(word_analyses, 1):
            print(f"    {i}. {analysis['name']}: {analysis['score']:.0f}/60 (最長 {analysis['max_length']} 字符)")
    
    return analyses

def show_problem_samples(analyses):
    """顯示問題段落樣本"""
    print(f"\n📝 問題段落樣本 (>25字符):")
    
    for analysis in analyses:
        if analysis['long_segments']:
            print(f"\n  {analysis['name']} 問題段落:")
            for i, seg in enumerate(analysis['long_segments'][:3], 1):  # 只顯示前3個
                print(f"    {i}. {seg['text']} ({seg['length']} 字符)")
        else:
            print(f"\n  {analysis['name']}: ✅ 無問題段落")

def generate_final_comprehensive_report(analyses):
    """生成最終綜合報告"""
    print(f"\n🏆 最終綜合報告")
    print("=" * 80)
    
    # 統計成功測試
    segment_count = len([a for a in analyses if a['level_type'] == 'segment'])
    word_count = len([a for a in analyses if a['level_type'] == 'word'])
    
    print(f"📊 測試成功統計:")
    print(f"  段落級測試: {segment_count} 個服務成功")
    print(f"  詞彙級測試: {word_count} 個服務成功")
    print(f"  總計: {len(analyses)} 個測試結果")
    
    # 找出最佳方案
    if analyses:
        best_overall = max(analyses, key=lambda x: x['score'])
        best_segment = max([a for a in analyses if a['level_type'] == 'segment'], key=lambda x: x['score'], default=None)
        best_word = max([a for a in analyses if a['level_type'] == 'word'], key=lambda x: x['score'], default=None)
        
        print(f"\n🥇 最佳方案:")
        print(f"  整體最佳: {best_overall['name']} ({best_overall['score']:.0f}/60)")
        if best_segment:
            print(f"  段落級最佳: {best_segment['name']} ({best_segment['score']:.0f}/60)")
        if best_word:
            print(f"  詞彙級最佳: {best_word['name']} ({best_word['score']:.0f}/60)")
    
    # 針對用戶原始問題的分析
    print(f"\n💡 針對用戶原始問題的解決方案:")
    print(f"  原始問題: Whisper-1 段落過長 (19字符)")
    
    # 段落級表現
    segment_analyses = [a for a in analyses if a['level_type'] == 'segment']
    if segment_analyses:
        avg_segment_max = sum(a['max_length'] for a in segment_analyses) / len(segment_analyses)
        print(f"  段落級平均最長: {avg_segment_max:.1f} 字符 ({'問題更嚴重' if avg_segment_max > 19 else '有改善'})")
    
    # 詞彙級表現
    word_analyses = [a for a in analyses if a['level_type'] == 'word']
    if word_analyses:
        avg_word_max = sum(a['max_length'] for a in word_analyses) / len(word_analyses)
        print(f"  詞彙級平均最長: {avg_word_max:.1f} 字符 ({'完美解決' if avg_word_max <= 18 else '大幅改善'})")
    
    # 最終建議
    print(f"\n🎯 最終建議:")
    if best_word:
        print(f"  🏆 推薦方案: {best_word['name']}")
        print(f"  📁 文件位置: {best_word['filepath']}")
        print(f"  ✅ 評分: {best_word['score']:.0f}/60")
        print(f"  ✅ 最長段落: {best_word['max_length']} 字符")
        print(f"  ✅ 問題段落: {best_word['long_segments_count']} 個")
        
        if best_word['score'] >= 60:
            print(f"  🎉 完美解決您的段落過長問題！")
    
    # 文件位置總結
    print(f"\n📁 所有測試結果文件位置:")
    for analysis in analyses:
        print(f"  - {analysis['filepath']} ({analysis['name']})")
    
    print(f"\n📋 結果數據文件:")
    result_files = [
        "elevenlabs_segment_real_result.json",
        "assemblyai_segment_real_result.json"
    ]
    for filepath in result_files:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  - {filepath} ({file_size} bytes)")

def main():
    """主函數"""
    print("🔍 完整段落級 vs 詞彙級比較分析")
    print("包含 ElevenLabs, AssemblyAI, Groq 三個服務")
    print("=" * 80)
    
    # 檢查所有必要文件
    required_files = [
        "elevenlabs_segment_real.srt",
        "assemblyai_segment_real.srt",
        "elevenlabs_precise_18chars.srt",
        "assemblyai_precise_18chars.srt",
        "final_groq_word_level.srt"
    ]
    
    existing_files = [f for f in required_files if os.path.exists(f)]
    print(f"📋 可用文件: {len(existing_files)}/{len(required_files)}")
    
    if len(existing_files) < 3:
        print("⚠️ 可用文件較少，但仍可進行比較")
    
    # 執行完整比較
    analyses = create_complete_comparison()
    
    if analyses:
        # 顯示問題段落樣本
        show_problem_samples(analyses)
        
        # 生成最終報告
        generate_final_comprehensive_report(analyses)
        
        print(f"\n✅ 完整段落級 vs 詞彙級比較分析完成！")
        print(f"📊 成功分析了 {len(analyses)} 個測試結果")
    else:
        print(f"❌ 分析失敗")
    
    return analyses

if __name__ == "__main__":
    main()
