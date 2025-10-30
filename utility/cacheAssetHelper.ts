/**
 * cacheAsset 輔助函數
 * 用於提取 JSON 中的所有媒體 URL 並預先快取到 Preview SDK
 */

import { Preview } from '@creatomate/preview';

/**
 * 提取 JSON 中所有的媒體 URL
 * 遞迴搜尋所有 source 屬性
 */
export function extractMediaUrls(obj: any, urls: Set<string> = new Set()): string[] {
  if (typeof obj !== 'object' || obj === null) {
    return Array.from(urls);
  }

  if (Array.isArray(obj)) {
    obj.forEach(item => extractMediaUrls(item, urls));
    return Array.from(urls);
  }

  for (const [key, value] of Object.entries(obj)) {
    if (key === 'source' && typeof value === 'string') {
      // 找到 source 屬性
      if (isExternalUrl(value)) {
        urls.add(value);
      }
    } else if (typeof value === 'object') {
      // 遞迴處理嵌套物件
      extractMediaUrls(value, urls);
    }
  }

  return Array.from(urls);
}

/**
 * 檢查 URL 是否為外部 URL（需要快取）
 */
export function isExternalUrl(url: string): boolean {
  // 不處理空字串或相對路徑
  if (!url || !url.startsWith('http://') && !url.startsWith('https://')) {
    return false;
  }

  try {
    const urlObj = new URL(url);
    
    // Creatomate 官方資源不需要快取（已經可以直接載入）
    const allowedDomains = [
      'creatomate-static.s3.amazonaws.com',
      'creatomate.com',
      'static.creatomate.com',
    ];

    return !allowedDomains.some(domain => urlObj.hostname === domain);
  } catch (error) {
    return false;
  }
}

/**
 * URL 映射表（原始 URL → 處理後的 URL）
 */
const globalUrlMapping = new Map<string, string>();

/**
 * 獲取當前網域的絕對 URL
 */
function getAbsoluteProxyUrl(originalUrl: string): string {
  // 使用絕對 URL（避免跨域 iframe 的相對路徑問題）
  const baseUrl = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000';
  return `${baseUrl}/api/media-proxy?url=${encodeURIComponent(originalUrl)}`;
}

/**
 * 快取所有外部素材到 Preview SDK
 * 
 * @param preview Preview SDK 實例
 * @param json JSON 物件
 * @returns 成功快取的 URL 列表和 URL 映射（用於替換 JSON）
 */
export async function cacheExternalAssets(
  preview: Preview,
  json: any
): Promise<{ 
  success: string[]; 
  failed: Array<{ url: string; error: string }>;
  urlMapping: Map<string, string>;
}> {
  const urls = extractMediaUrls(json);
  const success: string[] = [];
  const failed: Array<{ url: string; error: string }> = [];
  const urlMapping = new Map<string, string>();

  if (urls.length === 0) {
    console.log(`[cacheAsset] 沒有外部素材需要快取`);
    return { success, failed, urlMapping };
  }

  console.log(`[cacheAsset] 發現 ${urls.length} 個外部素材需要快取:`, urls);

  for (const url of urls) {
    try {
      console.log(`[cacheAsset] 開始下載: ${url}`);
      
      // 🔧 策略：優先嘗試直接下載，失敗則使用代理
      let blob: Blob;
      
      try {
        // 嘗試 1：直接下載（如果素材有 CORS）
        console.log(`[cacheAsset] 嘗試直接下載...`);
        const directResponse = await fetch(url, {
          mode: 'cors',
          credentials: 'omit',
        });
        
        if (!directResponse.ok) {
          throw new Error(`HTTP ${directResponse.status}`);
        }
        
        blob = await directResponse.blob();
        console.log(`[cacheAsset] ✅ 直接下載成功`);
        
      } catch (directError) {
        // 嘗試 2：使用代理下載（繞過 CORS）
        console.log(`[cacheAsset] 直接下載失敗，改用代理...`);
        console.log(`[cacheAsset] 直接下載錯誤:`, directError);
        
        const proxyUrl = `/api/media-proxy?url=${encodeURIComponent(url)}`;
        console.log(`[cacheAsset] 代理 URL: ${proxyUrl}`);
        
        const proxyResponse = await fetch(proxyUrl);
        console.log(`[cacheAsset] 代理回應狀態: ${proxyResponse.status} ${proxyResponse.statusText}`);
        
        if (!proxyResponse.ok) {
          const errorText = await proxyResponse.text();
          console.error(`[cacheAsset] 代理錯誤內容:`, errorText);
          throw new Error(`代理失敗: HTTP ${proxyResponse.status} - ${errorText}`);
        }
        
        // 取得 Blob 並確保有正確的 MIME type
        const arrayBuffer = await proxyResponse.arrayBuffer();
        let contentType = proxyResponse.headers.get('content-type') || 'application/octet-stream';
        
        // 🔧 如果代理已經偽裝 GIF 為 video/mp4，保持這個 type
        blob = new Blob([arrayBuffer], { type: contentType });
        
        console.log(`[cacheAsset] ✅ 代理下載成功 (${blob.size} bytes, type: ${blob.type})`);
      }

      console.log(`[cacheAsset] 下載完成: ${url} (${blob.size} bytes, ${blob.type})`);

      // 🔧 關鍵策略：如果是透過代理下載的，用代理的絕對 URL 快取
      // 這樣 iframe 驗證 URL 時會成功（代理 URL 真的存在）
      let cacheUrl = url;
      
      if (url.toLowerCase().includes('2050today.org') || 
          (!url.includes('creatomate') && !url.includes('blocktempo.ai'))) {
        // 無 CORS 的外部素材 → 使用代理 URL
        cacheUrl = getAbsoluteProxyUrl(url);
        urlMapping.set(url, cacheUrl);
        globalUrlMapping.set(url, cacheUrl);
        console.log(`[cacheAsset] 🔧 使用代理 URL: ${url} → ${cacheUrl}`);
      }

      // 快取到 Preview SDK
      await preview.cacheAsset(cacheUrl, blob);
      console.log(`[cacheAsset] ✅ 快取成功: ${cacheUrl}`);
      
      success.push(url);
      
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      console.error(`[cacheAsset] ❌ 完全失敗: ${url}`);
      console.error(`[cacheAsset] 錯誤:`, error);
      
      failed.push({ url, error: errorMsg });
      
      // ⚠️ 重要：即使快取失敗也不拋出錯誤
      // 讓 Preview SDK 嘗試直接載入（可能成功，如果素材有 CORS）
    }
  }

  console.log(`[cacheAsset] 完成 - 成功: ${success.length}, 失敗: ${failed.length}`);
  
  if (failed.length > 0) {
    console.warn(`[cacheAsset] ⚠️ 有 ${failed.length} 個素材快取失敗，Preview SDK 會嘗試直接載入這些 URL`);
  }
  
  if (urlMapping.size > 0) {
    console.log(`[cacheAsset] 📝 URL 映射記錄:`, Array.from(urlMapping.entries()));
  }
  
  return { success, failed, urlMapping };
}

/**
 * 替換 JSON 中的 GIF URL 為映射後的假 URL
 */
export function replaceGifUrlsInJson(json: any, urlMapping: Map<string, string>): any {
  if (typeof json !== 'object' || json === null) {
    return json;
  }

  if (Array.isArray(json)) {
    return json.map(item => replaceGifUrlsInJson(item, urlMapping));
  }

  const result: any = {};
  
  for (const [key, value] of Object.entries(json)) {
    if (key === 'source' && typeof value === 'string') {
      // 檢查是否需要替換
      const mappedUrl = urlMapping.get(value);
      if (mappedUrl) {
        console.log(`[URL替換] ${value} → ${mappedUrl}`);
        result[key] = mappedUrl;
      } else {
        result[key] = value;
      }
    } else if (typeof value === 'object') {
      result[key] = replaceGifUrlsInJson(value, urlMapping);
    } else {
      result[key] = value;
    }
  }

  return result;
}

/**
 * 檢測媒體類型
 */
export function getMediaType(url: string): 'image' | 'video' | 'audio' | 'unknown' {
  const extension = url.split('.').pop()?.toLowerCase().split('?')[0];
  
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
  const videoExts = ['mp4', 'webm', 'avi', 'mov', 'mkv'];
  const audioExts = ['mp3', 'wav', 'aac', 'ogg', 'flac'];

  if (imageExts.includes(extension || '')) return 'image';
  if (videoExts.includes(extension || '')) return 'video';
  if (audioExts.includes(extension || '')) return 'audio';
  
  return 'unknown';
}

