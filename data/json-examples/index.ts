/**
 * JSON 示例索引
 * 
 * 自動載入所有 .json 檔案
 */

import defaultSimpleExample from './00-default-simple.json';

export interface JsonExample {
  name: string;
  fileName: string;
  json: string;
}

/**
 * 默認的初始 JSON
 */
export const DEFAULT_JSON = JSON.stringify(defaultSimpleExample, null, 2);

/**
 * 自動載入所有 JSON 示例檔案
 */
// @ts-ignore - webpack require.context
const context = require.context('./', false, /\.json$/);

export const JSON_EXAMPLES: JsonExample[] = context
  .keys()
  .filter((key: string) => {
    // 只保留以 ./ 開頭的（排除絕對路徑）
    if (!key.startsWith('./')) {
      console.log(`⏭️ 跳過絕對路徑: ${key}`);
      return false;
    }
    
    // 排除 00-default-simple.json
    if (key === './00-default-simple.json') {
      console.log(`⏭️ 跳過默認示例: ${key}`);
      return false;
    }
    
    return true;
  })
  .map((key: string): JsonExample => {
    const fileName = key.replace('./', '');
    const jsonData = context(key);
    const name = fileName.replace('.json', '');
    
    console.log(`✅ 載入示例: ${name}`);
    
    return {
      name,
      fileName,
      json: JSON.stringify(jsonData, null, 2),
    };
  })
  .sort((a: JsonExample, b: JsonExample) => a.fileName.localeCompare(b.fileName));

console.log(`📊 總共 ${JSON_EXAMPLES.length} 個示例:`, JSON_EXAMPLES.map(e => e.name));

export default JSON_EXAMPLES;
