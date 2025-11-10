/**
 * API 請求處理工具
 */

/**
 * 將編輯器 JSON 轉換為 API 請求格式
 */
export function convertToApiRequest(sourceJson: any): string {
  const apiRequest = {
    source: sourceJson,
    output_format: sourceJson.output_format || "mp4"
  };
  return JSON.stringify(apiRequest, null, 2);
}

/**
 * 從 API 請求格式提取編輯器 JSON
 */
export function extractFromApiRequest(apiRequestJson: string): string {
  const apiRequest = JSON.parse(apiRequestJson);
  
  if (!apiRequest.source) {
    throw new Error('匯入失敗：JSON 格式不正確，缺少 source 字段');
  }
  
  return JSON.stringify(apiRequest.source, null, 2);
}

/**
 * 複製按鈕視覺反饋
 */
export function showCopyFeedback(buttonSelector: string) {
  const button = document.querySelector(buttonSelector) as HTMLButtonElement;
  if (button) {
    const originalText = button.textContent;
    button.textContent = '已複製！';
    button.style.background = '#45a049';
    setTimeout(() => {
      button.textContent = originalText;
      button.style.background = '#4caf50';
    }, 2000);
  }
}

/**
 * 從 Elements 格式提取並轉換為完整的編輯器 JSON
 * 支援四種格式:
 * 1. 帶有 "elements": [...] 的外層物件 { "elements": [...] }
 * 2. 直接的 [...] 陣列
 * 3. 直接的 "elements": [...] 字串(直接提取陣列部分)
 * 4. 多個元素物件(用逗號分隔,自動包裝為陣列)
 */
export function extractFromElementsInput(elementsInput: string): string {
  let input = elementsInput.trim();
  
  // 格式3: 檢查是否為直接的 "elements": [...] 格式
  // 直接提取陣列部分,不要包裝成物件
  if (input.startsWith('"elements"')) {
    // 找到冒號後的陣列部分
    const match = input.match(/^"elements"\s*:\s*(\[[\s\S]*\])$/);
    if (match) {
      input = match[1]; // 直接使用陣列部分
    } else {
      throw new Error('格式錯誤: "elements": [...] 格式不正確');
    }
  }
  
  // 格式4: 檢查是否為多個元素物件(用逗號分隔但沒有外層陣列括號)
  // 特徵: 開頭是 { 但不是陣列,且包含多個物件(有 },\s*{ 模式)
  const hasMultipleObjects = /\}\s*,\s*\{/.test(input);
  if (input.startsWith('{') && !input.startsWith('[') && hasMultipleObjects) {
    // 包裝成陣列
    input = `[${input}]`;
  }
  
  const parsed = JSON.parse(input);
  
  let elements: any[] = [];
  
  // 格式1: 包含 "elements" 的物件
  if (parsed && typeof parsed === 'object' && 'elements' in parsed && Array.isArray(parsed.elements)) {
    elements = parsed.elements;
  }
  // 格式2: 直接是陣列
  else if (Array.isArray(parsed)) {
    elements = parsed;
  }
  // 單一元素物件(fallback)
  else if (parsed && typeof parsed === 'object') {
    elements = [parsed];
  }
  else {
    throw new Error('匯入失敗：無法識別的 Elements 格式');
  }
  
  // 構建完整的 Creatomate JSON 格式
  const fullJson = {
    outputFormat: "mp4",
    width: 1280,
    height: 1280,
    elements: elements
  };
  
  return JSON.stringify(fullJson, null, 2);
}

