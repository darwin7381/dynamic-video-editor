/**
 * URL 高亮工具（使用 background-image 漸變）
 * 直接在 textarea 上添加背景，不需要額外層
 */

export type UrlStatus = 'processing' | 'success' | 'error';

/**
 * 當前元素範圍
 */
export interface CurrentElementRange {
  start: number;
  end: number;
}

/**
 * 生成高亮 HTML（用於 overlay div）
 * 支援兩種高亮：
 * 1. URL 狀態高亮（背景色）
 * 2. 當前編輯元素高亮（左側藍色邊框 + 淡藍背景）
 */
/**
 * 生成多個元素的整區高亮（獨立層）
 * 正確處理多個範圍，避免重複文字
 */
export function generateMultipleElementHighlights(
  text: string,
  elementRanges: CurrentElementRange[]
): string {
  if (elementRanges.length === 0) {
    return escapeHtml(text);
  }
  
  // 按位置排序
  const sortedRanges = [...elementRanges].sort((a, b) => a.start - b.start);
  
  let result = '';
  let lastIndex = 0;
  
  sortedRanges.forEach((range, index) => {
    // 找到元素前的縮排
    let indentStart = range.start;
    while (indentStart > lastIndex && text[indentStart - 1] !== '\n') {
      if (text[indentStart - 1] !== ' ' && text[indentStart - 1] !== '\t') {
        break;
      }
      indentStart--;
    }
    
    // 範圍前的普通文字
    if (indentStart > lastIndex) {
      result += escapeHtml(text.substring(lastIndex, indentStart));
    }
    
    // 高亮區域
    const indent = text.substring(indentStart, range.start);
    const element = text.substring(range.start, range.end);
    
    // 🔧 檢查元素後是否有換行符
    let afterElement = '';
    if (range.end < text.length && text[range.end] === ',') {
      afterElement = ',';  // 包含逗號
      lastIndex = range.end + 1;
    } else {
      lastIndex = range.end;
    }
    
    // 🔧 檢查逗號後是否有換行
    if (lastIndex < text.length && text[lastIndex] === '\n') {
      afterElement += '\n';  // 包含換行，避免 div 後多一個空行
      lastIndex++;
    }
    
    result += `<div class="element-block-highlight">${escapeHtml(indent + element + afterElement)}</div>`;
  });
  
  // 剩餘文字
  if (lastIndex < text.length) {
    result += escapeHtml(text.substring(lastIndex));
  }
  
  return result;
}

/**
 * 向後相容：單個元素高亮
 */
export function generateElementHighlight(
  text: string,
  elementRange: CurrentElementRange
): string {
  return generateMultipleElementHighlights(text, [elementRange]);
}

/**
 * 生成 URL 狀態高亮（獨立層，只處理 URL）
 */
export function generateHighlightedText(
  text: string,
  urlStatusMap: Map<string, UrlStatus>
): string {
  return processSegment(text, urlStatusMap, false);
}

/**
 * 處理文字片段，添加 URL 狀態高亮
 */
function processSegment(
  text: string,
  urlStatusMap: Map<string, UrlStatus>,
  isInCurrentElement: boolean
): string {
  if (urlStatusMap.size === 0) {
    return escapeHtml(text);
  }

  // 找到所有 URL 位置
  const urlPositions: Array<{ start: number; end: number; status: UrlStatus }> = [];
  
  urlStatusMap.forEach((status, url) => {
    let index = 0;
    while ((index = text.indexOf(url, index)) !== -1) {
      urlPositions.push({
        start: index,
        end: index + url.length,
        status
      });
      index += url.length;
    }
  });

  if (urlPositions.length === 0) {
    return escapeHtml(text);
  }

  // 排序
  urlPositions.sort((a, b) => a.start - b.start);

  // 生成 HTML
  let result = '';
  let lastIndex = 0;

  urlPositions.forEach(pos => {
    // 普通文字
    if (pos.start > lastIndex) {
      result += escapeHtml(text.substring(lastIndex, pos.start));
    }

    // URL 高亮
    const bgColor = 
      pos.status === 'processing' ? 'rgba(255, 193, 7, 0.35)' :
      pos.status === 'success' ? 'rgba(76, 175, 80, 0.35)' :
      'rgba(244, 67, 54, 0.35)';
    
    result += `<span style="background-color: ${bgColor};">${escapeHtml(text.substring(pos.start, pos.end))}</span>`;
    lastIndex = pos.end;
  });

  // 剩餘文字
  if (lastIndex < text.length) {
    result += escapeHtml(text.substring(lastIndex));
  }

  return result;
}

/**
 * HTML 跳脫
 */
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
    // 🔧 不用 &nbsp;，保留正常空格，讓長 URL 可以自動換行
    // .replace(/ /g, '&nbsp;')  ← 移除這行
    .replace(/\n/g, '<br/>');
}

/**
 * 取得狀態對應的顏色
 */
export function getStatusColor(status: UrlStatus): string {
  switch (status) {
    case 'processing':
      return 'rgba(255, 193, 7, 0.3)';  // 黃色
    case 'success':
      return 'rgba(76, 175, 80, 0.3)';  // 綠色
    case 'error':
      return 'rgba(244, 67, 54, 0.3)';  // 紅色
    default:
      return 'transparent';
  }
}

/**
 * 取得狀態對應的文字說明
 */
export function getStatusText(status: UrlStatus): string {
  switch (status) {
    case 'processing':
      return '處理中...';
    case 'success':
      return '✓ 成功';
    case 'error':
      return '✗ 失敗';
    default:
      return '';
  }
}

/**
 * 根據 path 在 JSON 中找到元素位置（支援嵌套）
 * @param jsonText JSON 文字
 * @param path 路徑，如 "0"（第0個元素）或 "8.0"（第8個元素的第0個子元素）
 */
export function findElementRangeByPath(jsonText: string, path: string): CurrentElementRange | null {
  try {
    const pathParts = path.split('.').map(p => parseInt(p));
    
    // 找到 elements 陣列
    let searchStart = 0;
    let arrayKey = '"elements"';
    
    // 逐層深入
    for (let depth = 0; depth < pathParts.length; depth++) {
      const targetIndex = pathParts[depth];
      
      const elementsPos = jsonText.indexOf(arrayKey, searchStart);
      if (elementsPos === -1) return null;
      
      const arrayStart = jsonText.indexOf('[', elementsPos);
      if (arrayStart === -1) return null;
      
      // 找到第 targetIndex 個元素
      let currentIndex = 0;
      let braceDepth = 0;
      let inString = false;
      let escapeNext = false;
      let elementStart = -1;
      
      for (let i = arrayStart + 1; i < jsonText.length; i++) {
        const char = jsonText[i];
        
        if (escapeNext) {
          escapeNext = false;
          continue;
        }
        
        if (char === '\\') {
          escapeNext = true;
          continue;
        }
        
        if (char === '"') {
          inString = !inString;
          continue;
        }
        
        if (!inString) {
          if (char === '{') {
            if (braceDepth === 0) elementStart = i;
            braceDepth++;
          } else if (char === '}') {
            braceDepth--;
            
            if (braceDepth === 0 && elementStart !== -1) {
              if (currentIndex === targetIndex) {
                // 找到目標元素
                if (depth === pathParts.length - 1) {
                  // 最後一層，返回範圍
                  return { start: elementStart, end: i + 1 };
                } else {
                  // 還要繼續深入，更新 searchStart
                  searchStart = elementStart;
                  break;
                }
              }
              currentIndex++;
              elementStart = -1;
            }
          }
        }
      }
    }
    
    return null;
  } catch (error) {
    console.error('[findElementRangeByPath] 錯誤:', error);
    return null;
  }
}

/**
 * 在 JSON 文字中找到第 N 個元素的位置範圍（向後相容）
 */
export function findElementRange(jsonText: string, elementIndex: number): CurrentElementRange | null {
  try {
    // 找到 elements 陣列的開始
    const elementsStart = jsonText.indexOf('"elements"');
    if (elementsStart === -1) return null;
    
    const arrayStart = jsonText.indexOf('[', elementsStart);
    if (arrayStart === -1) return null;

    // 解析元素邊界
    let currentIndex = 0;
    let braceDepth = 0;
    let inString = false;
    let escapeNext = false;
    let elementStartPos = -1;
    
    for (let i = arrayStart + 1; i < jsonText.length; i++) {
      const char = jsonText[i];
      
      if (escapeNext) {
        escapeNext = false;
        continue;
      }
      
      if (char === '\\') {
        escapeNext = true;
        continue;
      }
      
      if (char === '"' && !escapeNext) {
        inString = !inString;
        continue;
      }
      
      if (!inString) {
        if (char === '{') {
          if (braceDepth === 0) {
            elementStartPos = i;
          }
          braceDepth++;
        } else if (char === '}') {
          braceDepth--;
          
          if (braceDepth === 0 && elementStartPos !== -1) {
            // 找到一個完整元素
            if (currentIndex === elementIndex) {
              return {
                start: elementStartPos,
                end: i + 1
              };
            }
            currentIndex++;
            elementStartPos = -1;
          }
        }
      }
    }
    
    return null;
  } catch (error) {
    console.error('[findElementRange] 錯誤:', error);
    return null;
  }
}


