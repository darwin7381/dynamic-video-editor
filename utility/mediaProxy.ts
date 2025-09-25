/**
 * 媒體代理工具函數
 * 用於將外部媒體 URL 轉換為代理 URL，繞過 Creatomate Preview SDK 的安全限制
 */

/**
 * 將外部媒體 URL 轉換為代理 URL
 * 
 * @param externalUrl 外部媒體資源的 URL
 * @returns 代理後的相對路徑 URL
 * 
 * @example
 * ```typescript
 * const proxyUrl = createMediaProxyUrl('https://example.com/image.jpg');
 * // 返回: '/api/media-proxy?url=https%3A//example.com/image.jpg'
 * ```
 */
export function createMediaProxyUrl(externalUrl: string): string {
  // 驗證 URL 格式
  try {
    new URL(externalUrl);
  } catch (error) {
    throw new Error(`Invalid URL format: ${externalUrl}`);
  }

  // 編碼 URL 參數
  const encodedUrl = encodeURIComponent(externalUrl);
  
  // 返回代理 URL
  return `/api/media-proxy?url=${encodedUrl}`;
}

/**
 * 檢查 URL 是否需要代理
 * 
 * @param url 要檢查的 URL
 * @returns 如果需要代理返回 true，否則返回 false
 */
export function needsProxy(url: string): boolean {
  // 如果已經是代理 URL，不需要再次代理
  if (url.startsWith('/api/media-proxy')) {
    return false;
  }

  // 如果是相對路徑，不需要代理
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return false;
  }

  try {
    const urlObj = new URL(url);
    
    // Creatomate 官方資源不需要代理
    const allowedDomains = [
      'creatomate-static.s3.amazonaws.com',
      'creatomate.com',
      'static.creatomate.com',
    ];

    return !allowedDomains.some(domain => urlObj.hostname === domain);
  } catch (error) {
    // 如果 URL 格式錯誤，假設需要代理
    return true;
  }
}

/**
 * 智能媒體 URL 處理
 * 自動判斷是否需要代理，並返回適當的 URL
 * 
 * @param url 原始 URL
 * @returns 處理後的 URL（可能是代理 URL 或原始 URL）
 */
export function processMediaUrl(url: string): string {
  if (needsProxy(url)) {
    return createMediaProxyUrl(url);
  }
  return url;
}

/**
 * 批量處理媒體 URL
 * 
 * @param urls URL 陣列
 * @returns 處理後的 URL 陣列
 */
export function processMediaUrls(urls: string[]): string[] {
  return urls.map(processMediaUrl);
}

/**
 * 處理 JSON 物件中的媒體 URL
 * 遞迴搜尋並轉換所有的 source 屬性
 * 
 * @param obj 要處理的 JSON 物件
 * @returns 處理後的 JSON 物件
 */
export function processMediaUrlsInJson(obj: any): any {
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(processMediaUrlsInJson);
  }

  const result: any = {};
  
  for (const [key, value] of Object.entries(obj)) {
    if (key === 'source' && typeof value === 'string') {
      // 處理 source 屬性
      result[key] = processMediaUrl(value);
    } else if (typeof value === 'object') {
      // 遞迴處理嵌套物件
      result[key] = processMediaUrlsInJson(value);
    } else {
      // 保持其他屬性不變
      result[key] = value;
    }
  }

  return result;
}

/**
 * 媒體類型檢測
 * 
 * @param url 媒體 URL
 * @returns 媒體類型 ('image' | 'video' | 'audio' | 'unknown')
 */
export function detectMediaType(url: string): 'image' | 'video' | 'audio' | 'unknown' {
  const extension = url.split('.').pop()?.toLowerCase();
  
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
  const videoExts = ['mp4', 'webm', 'avi', 'mov', 'mkv'];
  const audioExts = ['mp3', 'wav', 'aac', 'ogg', 'flac'];

  if (imageExts.includes(extension || '')) return 'image';
  if (videoExts.includes(extension || '')) return 'video';
  if (audioExts.includes(extension || '')) return 'audio';
  
  return 'unknown';
}

/**
 * 生成測試用的媒體 URL 範例
 */
export const EXAMPLE_MEDIA_URLS = {
  images: [
    'https://picsum.photos/800/600',
    'https://via.placeholder.com/400x300.jpg',
    'https://httpbin.org/image/jpeg',
  ],
  videos: [
    'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
  ],
  gifs: [
    'https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif',
  ],
} as const;
