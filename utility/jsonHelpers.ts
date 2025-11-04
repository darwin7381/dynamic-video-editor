/**
 * JSON 處理輔助函數
 */

/**
 * 轉換駝峰命名為蛇形命名
 * 用於 Creatomate API 的格式轉換
 */
export function convertToSnakeCase(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(item => convertToSnakeCase(item));
  } else if (obj !== null && typeof obj === 'object') {
    const newObj: any = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
        newObj[snakeKey] = convertToSnakeCase(obj[key]);
      }
    }
    return newObj;
  }
  return obj;
}

/**
 * 解析時間字符串轉為秒數
 */
export function parseTime(timeStr: any): number {
  if (typeof timeStr === 'number') return timeStr;
  if (timeStr === 'end') return 0;
  const match = String(timeStr || '0').match(/(\d+(\.\d+)?)\s*s?/);
  return match ? parseFloat(match[1]) : 0;
}

/**
 * 計算元素的估計持續時間
 */
export function estimateDuration(element: any): number {
  if (element.duration !== undefined) {
    return parseTime(element.duration);
  }
  
  // 根據元素類型估算默認持續時間
  switch (element.type) {
    case 'video':
    case 'audio':
      return 8;
    case 'image':
      return 3;
    case 'text':
      return 4;
    case 'composition':
      return 6;
    case 'shape':
      return 5;
    default:
      return 3;
  }
}

