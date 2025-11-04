/**
 * 元素檢測器
 * 
 * 檢測 JSON 編輯器中光標位置對應的時間軸元素
 * 支援：
 * - 精確的元素邊界檢測
 * - 多種匹配策略
 * - 嵌套結構支援
 */

import { parseTime } from './jsonHelpers';
import { TimelineElement } from './timelineParser';

/**
 * 遞歸查找光標所在的元素路徑
 * 支援嵌套 composition 結構
 */
function findElementPathAtCursor(
  jsonText: string,
  cursorPosition: number,
  elements: any[],
  currentPath: string = ''
): string | null {
  let currentPos = jsonText.indexOf('"elements"');
  if (currentPos === -1) return null;
  
  const arrayStart = jsonText.indexOf('[', currentPos);
  if (arrayStart === -1) return null;
  
  // 遍歷每個元素
  let depth = 0;
  let inString = false;
  let escapeNext = false;
  let elementIndex = 0;
  let elementStart = -1;
  
  for (let i = arrayStart; i < jsonText.length; i++) {
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
        depth++;
        if (depth === 1) {
          elementStart = i;
        }
      } else if (char === '}') {
        depth--;
        if (depth === 0 && elementStart !== -1) {
          const elementEnd = i;
          
          // 檢查光標是否在這個元素內
          if (cursorPosition >= elementStart && cursorPosition <= elementEnd) {
            const elementPath = currentPath ? `${currentPath}.${elementIndex}` : `${elementIndex}`;
            const element = elements[elementIndex];
            
            // 如果是 composition，遞歸檢查子元素
            if (element && element.type === 'composition' && element.elements) {
              const elementText = jsonText.substring(elementStart, elementEnd + 1);
              const childPath = findElementPathAtCursor(
                elementText,
                cursorPosition - elementStart,
                element.elements,
                elementPath
              );
              
              if (childPath) {
                return childPath;  // 找到子元素，返回子元素的 path
              }
            }
            
            // 返回當前元素的 path
            return elementPath;
          }
          
          elementIndex++;
          elementStart = -1;
        }
      }
    }
  }
  
  return null;
}

/**
 * 檢測當前編輯的元素（支援嵌套結構）
 * 
 * @param cursorPosition 光標在 JSON 字符串中的位置
 * @param jsonText 完整的 JSON 字符串
 * @param timelineElements 時間軸元素陣列
 * @returns 對應的時間軸元素索引，未找到則返回 -1
 */
export function detectCurrentElement(
  cursorPosition: number, 
  jsonText: string, 
  timelineElements: TimelineElement[]
): number {
  try {
    const source = JSON.parse(jsonText);
    if (!source.elements || !Array.isArray(source.elements)) return -1;
    if (!timelineElements || timelineElements.length === 0) return -1;

    // 🔧 使用新的遞歸查找函數找到光標所在元素的 path
    const elementPath = findElementPathAtCursor(jsonText, cursorPosition, source.elements);
    
    if (!elementPath) {
      console.log('⚠️ 未找到光標所在的元素 path');
      return -1;
    }
    
    console.log(`🔍 光標位置 ${cursorPosition} 對應的 path: ${elementPath}`);
    
    // 在時間軸中查找匹配的元素
    const timelineIndex = timelineElements.findIndex(el => el.path === elementPath);
    
    if (timelineIndex !== -1) {
      console.log(`✅ 匹配成功: path=${elementPath} → 時間軸索引=${timelineIndex}, 元素="${timelineElements[timelineIndex].name}"`);
      return timelineIndex;
    } else {
      console.log(`❌ 在時間軸中找不到 path: ${elementPath}`);
      console.log(`可用的 paths:`, timelineElements.map(el => el.path).join(', '));
      return -1;
    }
  } catch (err) {
    console.error('檢測當前元素失敗:', err);
    return -1;
  }
}

