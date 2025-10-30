// ========================================
// ElevenLabs 詞彙級 SRT 生成器（寬度修正版）
// 解決中英文混合、數字寬度問題
// ========================================

const elevenLabsResult = $input.item.json;
const words = elevenLabsResult.words || [];

// ========================================
// 參數設定（根據實際顯示寬度）
// ========================================
const MAX_WIDTH = 36;      // 最大顯示寬度（中文=2，英文=1）
const MAX_DURATION = 5.0;  // 每段最長時間（秒）
const INCLUDE_SPEAKERS = true;  // 是否包含說話者標識

// ========================================
// 計算實際顯示寬度
// ========================================
function calculateDisplayWidth(text) {
  let width = 0;
  for (let char of text) {
    const code = char.charCodeAt(0);
    // 中文字符、全形字符
    if ((code >= 0x4E00 && code <= 0x9FFF) ||   // CJK 統一表意文字
        (code >= 0x3400 && code <= 0x4DBF) ||   // CJK 擴展 A
        (code >= 0xF900 && code <= 0xFAFF) ||   // CJK 兼容表意文字
        (code >= 0x3000 && code <= 0x303F) ||   // CJK 符號和標點
        (code >= 0xFF00 && code <= 0xFFEF)) {   // 全形字符
      width += 2;  // 中文字符寬度為2
    } else {
      width += 1;  // 英文、數字、符號寬度為1
    }
  }
  return width;
}

// ========================================
// 格式化函數
// ========================================
function formatSRTTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const milliseconds = Math.floor((seconds % 1) * 1000);
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')},${milliseconds.toString().padStart(3, '0')}`;
}

function formatSRTSegment(index, startSec, endSec, text) {
  const startTime = formatSRTTime(startSec);
  const endTime = formatSRTTime(endSec);
  return `${index}\n${startTime} --> ${endTime}\n${text}\n\n`;
}

// ========================================
// SRT 生成函數（寬度修正版）
// ========================================
function generateSRT(words, maxWidth, maxDuration) {
  let srtContent = "";
  let segmentIndex = 1;
  let currentSegment = [];
  let currentText = "";
  let segmentStart = null;
  let currentSpeaker = null;
  
  for (const word of words) {
    if (word.type !== 'word') continue;
    
    const wordText = word.text;
    const wordStart = word.start;
    const wordEnd = word.end;
    const speaker = word.speaker_id || null;
    
    if (segmentStart === null) segmentStart = wordStart;
    if (currentSpeaker === null) currentSpeaker = speaker;
    
    const potentialText = currentText + wordText;
    const potentialWidth = calculateDisplayWidth(potentialText);  // 使用顯示寬度
    const currentDuration = currentSegment.length > 0 ? wordEnd - segmentStart : 0;
    
    const shouldBreak = (
      (INCLUDE_SPEAKERS && speaker && speaker !== currentSpeaker) ||
      (potentialWidth > maxWidth && currentSegment.length > 0) ||  // 改用寬度判斷
      (currentDuration > maxDuration && currentSegment.length > 0)
    );
    
    if (shouldBreak) {
      const segmentEnd = currentSegment[currentSegment.length - 1].end;
      let finalText = currentText;
      if (INCLUDE_SPEAKERS && currentSpeaker) {
        finalText = `[${currentSpeaker}] ${currentText}`;
      }
      srtContent += formatSRTSegment(segmentIndex, segmentStart, segmentEnd, finalText);
      
      segmentIndex++;
      currentSegment = [word];
      currentText = wordText;
      segmentStart = wordStart;
      currentSpeaker = speaker;
    } else {
      currentSegment.push(word);
      currentText = potentialText;
    }
  }
  
  if (currentSegment.length > 0) {
    const segmentEnd = currentSegment[currentSegment.length - 1].end;
    let finalText = currentText;
    if (INCLUDE_SPEAKERS && currentSpeaker) {
      finalText = `[${currentSpeaker}] ${currentText}`;
    }
    srtContent += formatSRTSegment(segmentIndex, segmentStart, segmentEnd, finalText);
  }
  
  return srtContent;
}

// ========================================
// 執行生成
// ========================================
const srtContent = generateSRT(words, MAX_WIDTH, MAX_DURATION);

// 統計資訊
const wordCount = words.filter(w => w.type === 'word').length;
const speakers = [...new Set(words.filter(w => w.speaker_id).map(w => w.speaker_id))];
const segments = srtContent.split('\n\n').filter(s => s.trim()).length;

// 計算平均段落寬度
const segmentWidths = [];
srtContent.split('\n\n').forEach(seg => {
  const lines = seg.split('\n');
  if (lines.length >= 3) {
    const text = lines.slice(2).join('');
    segmentWidths.push(calculateDisplayWidth(text));
  }
});
const avgWidth = segmentWidths.length > 0 
  ? segmentWidths.reduce((a, b) => a + b, 0) / segmentWidths.length 
  : 0;
const maxWidthFound = Math.max(...segmentWidths, 0);

// ========================================
// 輸出結果
// ========================================
return {
  json: {
    srt: srtContent,
    transcription: elevenLabsResult.text,
    language: elevenLabsResult.language_code,
    language_probability: elevenLabsResult.language_probability,
    word_count: wordCount,
    total_words: words.length,
    segment_count: segments,
    speakers_detected: speakers.length,
    speakers: speakers,
    settings: {
      max_width: MAX_WIDTH,
      max_duration: MAX_DURATION,
      include_speakers: INCLUDE_SPEAKERS
    },
    quality_metrics: {
      avg_segment_width: Math.round(avgWidth * 10) / 10,
      max_segment_width: maxWidthFound,
      segments_over_limit: segmentWidths.filter(w => w > MAX_WIDTH).length
    }
  }
};



