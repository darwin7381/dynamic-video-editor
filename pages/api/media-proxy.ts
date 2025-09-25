import { NextApiRequest, NextApiResponse } from 'next';

/**
 * 媒體代理 API - 解決 Creatomate Preview SDK 外部圖片限制問題
 * 
 * 工作原理：
 * 1. Creatomate iframe 看到的是相對路徑 /api/media-proxy?url=...
 * 2. 此 API 代理去抓取真正的外部媒體資源
 * 3. 直接返回媒體數據給 Creatomate，繞過安全檢查
 * 
 * 支援的媒體類型：
 * - 圖片：JPG, PNG, WebP, SVG, GIF
 * - 影片：MP4, WebM, AVI, MOV
 * - 音訊：MP3, WAV, AAC, OGG
 */

// 支援的媒體類型對應表
const MEDIA_TYPES = {
  // 圖片
  'image/jpeg': ['jpg', 'jpeg'],
  'image/png': ['png'],
  'image/webp': ['webp'],
  'image/svg+xml': ['svg'],
  'image/gif': ['gif'],
  
  // 影片
  'video/mp4': ['mp4'],
  'video/webm': ['webm'],
  'video/avi': ['avi'],
  'video/quicktime': ['mov'],
  
  // 音訊
  'audio/mpeg': ['mp3'],
  'audio/wav': ['wav'],
  'audio/aac': ['aac'],
  'audio/ogg': ['ogg'],
};

// 從 URL 推測內容類型
function guessContentType(url: string): string {
  const extension = url.split('.').pop()?.toLowerCase();
  
  for (const [contentType, extensions] of Object.entries(MEDIA_TYPES)) {
    if (extensions.includes(extension || '')) {
      return contentType;
    }
  }
  
  return 'application/octet-stream';
}

// 設置快取策略
function getCacheControl(contentType: string): string {
  if (contentType.startsWith('video/')) {
    return 'public, max-age=3600'; // 影片快取 1 小時
  } else if (contentType.startsWith('audio/')) {
    return 'public, max-age=7200'; // 音訊快取 2 小時
  } else {
    return 'public, max-age=86400'; // 圖片快取 24 小時
  }
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // 處理 CORS 預檢請求
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Origin, Referer');
    res.setHeader('Access-Control-Max-Age', '86400');
    return res.status(200).end();
  }

  // 只允許 GET 請求
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { url } = req.query;

  // 檢查 URL 參數
  if (!url || typeof url !== 'string') {
    return res.status(400).json({ 
      error: 'Missing or invalid URL parameter',
      usage: '/api/media-proxy?url=https://example.com/image.jpg'
    });
  }

  // 驗證 URL 格式
  let targetUrl: URL;
  try {
    targetUrl = new URL(url);
  } catch (error) {
    return res.status(400).json({ 
      error: 'Invalid URL format',
      provided: url
    });
  }

  // 只允許 HTTPS 協議（安全考量）
  if (targetUrl.protocol !== 'https:') {
    return res.status(400).json({ 
      error: 'Only HTTPS URLs are allowed',
      provided: targetUrl.protocol
    });
  }

  try {
    console.log(`[媒體代理] 正在代理: ${url}`);
    
    // 發送請求到目標 URL
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Creatomate-Media-Proxy/1.0',
        'Accept': '*/*',
      },
      // 設置 30 秒超時
      signal: AbortSignal.timeout(30000),
    });

    // 檢查響應狀態
    if (!response.ok) {
      console.error(`[媒體代理] HTTP 錯誤: ${response.status} ${response.statusText}`);
      return res.status(response.status).json({ 
        error: `Failed to fetch media: ${response.status} ${response.statusText}`,
        url: url
      });
    }

    // 獲取內容類型
    const contentType = response.headers.get('content-type') || guessContentType(url);
    const contentLength = response.headers.get('content-length');

    // 檢查檔案大小限制（50MB）
    if (contentLength && parseInt(contentLength) > 50 * 1024 * 1024) {
      return res.status(413).json({ 
        error: 'File too large (max 50MB)',
        size: `${Math.round(parseInt(contentLength) / 1024 / 1024)}MB`
      });
    }

    // 獲取媒體數據
    const buffer = await response.arrayBuffer();
    
    console.log(`[媒體代理] 成功代理: ${url} (${contentType}, ${buffer.byteLength} bytes)`);

    // 設置響應標頭 - 模擬 Creatomate 官方資源
    res.setHeader('Content-Type', contentType);
    res.setHeader('Cache-Control', getCacheControl(contentType));
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization, Cache-Control');
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Cross-Origin-Resource-Policy', 'cross-origin');
    res.setHeader('Cross-Origin-Embedder-Policy', 'unsafe-none');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    
    // 如果有內容長度，設置它
    if (contentLength) {
      res.setHeader('Content-Length', contentLength);
    }

    // 返回媒體數據
    res.send(Buffer.from(buffer));

  } catch (error) {
    console.error('[媒體代理] 錯誤:', error);
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        return res.status(408).json({ 
          error: 'Request timeout (30s)',
          url: url
        });
      }
      
      return res.status(500).json({ 
        error: 'Failed to fetch media',
        message: error.message,
        url: url
      });
    }

    return res.status(500).json({ 
      error: 'Unknown error occurred',
      url: url
    });
  }
}

// 配置 API 路由
export const config = {
  api: {
    // 允許較大的響應體（50MB）
    responseLimit: '50mb',
  },
};
