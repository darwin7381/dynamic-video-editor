// 從 ElevenLabs 結果提取 words
const elevenLabsResult = $input.item.json;
const words = elevenLabsResult.words || [];

// 參數設定
const MAX_CHARS = 18;
const MAX_DURATION = 5.0;
const INCLUDE_SPEAKERS = true;

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

function generateSRT(words, maxChars, maxDuration) {
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
    const currentDuration = currentSegment.length > 0 ? wordEnd - segmentStart : 0;
    
    const shouldBreak = (
      (INCLUDE_SPEAKERS && speaker && speaker !== currentSpeaker) ||
      (potentialText.length > maxChars && currentSegment.length > 0) ||
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

const srtContent = generateSRT(words, MAX_CHARS, MAX_DURATION);
const wordCount = words.filter(w => w.type === 'word').length;
const speakers = [...new Set(words.filter(w => w.speaker_id).map(w => w.speaker_id))];
const segments = srtContent.split('\n\n').filter(s => s.trim()).length;

return {
  json: {
    srt: srtContent,
    transcription: elevenLabsResult.text,
    language: elevenLabsResult.language_code,
    word_count: wordCount,
    segment_count: segments,
    speakers_detected: speakers.length,
    speakers: speakers
  }
};




