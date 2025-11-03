/**
 * URL 高亮工具（使用 background-image 漸變）
 * 直接在 textarea 上添加背景，不需要額外層
 */

export type UrlStatus = 'processing' | 'success' | 'error';

/**
 * 生成高亮 HTML（用於 overlay div）
 */
export function generateHighlightedText(
  text: string,
  urlStatusMap: Map<string, UrlStatus>
): string {
  if (urlStatusMap.size === 0) {
    return escapeHtml(text);
  }

  // 收集所有需要高亮的區域
  const highlights: Array<{ start: number; end: number; status: UrlStatus }> = [];
  
  urlStatusMap.forEach((status, url) => {
    let index = 0;
    while ((index = text.indexOf(url, index)) !== -1) {
      highlights.push({
        start: index,
        end: index + url.length,
        status
      });
      index += url.length;
    }
  });

  // 按位置排序
  highlights.sort((a, b) => a.start - b.start);

  // 生成 HTML
  let result = '';
  let lastIndex = 0;

  highlights.forEach(hl => {
    // 添加普通文字
    if (hl.start > lastIndex) {
      result += escapeHtml(text.substring(lastIndex, hl.start));
    }

    // 添加高亮文字
    const color = 
      hl.status === 'processing' ? 'rgba(255, 193, 7, 0.3)' :
      hl.status === 'success' ? 'rgba(76, 175, 80, 0.3)' :
      'rgba(244, 67, 54, 0.3)';
    
    result += `<span style="background-color: ${color};">${escapeHtml(text.substring(hl.start, hl.end))}</span>`;
    lastIndex = hl.end;
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
    .replace(/ /g, '&nbsp;')
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


