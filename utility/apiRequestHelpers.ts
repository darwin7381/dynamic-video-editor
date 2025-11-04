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

