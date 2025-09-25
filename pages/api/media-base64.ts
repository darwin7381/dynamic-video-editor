import { NextApiRequest, NextApiResponse } from 'next';

/**
 * 媒體 Base64 轉換 API - 將外部圖片轉換為 base64 data URL
 * 這可能是繞過 Creatomate Preview SDK 限制的另一種方法
 */

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // 處理 CORS 預檢請求
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Origin, Referer');
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
      usage: '/api/media-base64?url=https://example.com/image.jpg'
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

  // 只允許 HTTPS 協議
  if (targetUrl.protocol !== 'https:') {
    return res.status(400).json({ 
      error: 'Only HTTPS URLs are allowed',
      provided: targetUrl.protocol
    });
  }

  try {
    console.log(`[Base64 轉換] 正在處理: ${url}`);
    
    // 發送請求到目標 URL
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Creatomate-Base64-Converter/1.0',
        'Accept': 'image/*',
      },
      signal: AbortSignal.timeout(30000),
    });

    if (!response.ok) {
      console.error(`[Base64 轉換] HTTP 錯誤: ${response.status} ${response.statusText}`);
      return res.status(response.status).json({ 
        error: `Failed to fetch media: ${response.status} ${response.statusText}`,
        url: url
      });
    }

    // 檢查檔案大小限制（10MB for base64）
    const contentLength = response.headers.get('content-length');
    if (contentLength && parseInt(contentLength) > 10 * 1024 * 1024) {
      return res.status(413).json({ 
        error: 'File too large for base64 conversion (max 10MB)',
        size: `${Math.round(parseInt(contentLength) / 1024 / 1024)}MB`
      });
    }

    // 獲取內容類型
    const contentType = response.headers.get('content-type') || 'image/jpeg';
    
    // 獲取媒體數據
    const buffer = await response.arrayBuffer();
    
    // 轉換為 base64
    const base64 = Buffer.from(buffer).toString('base64');
    const dataUrl = `data:${contentType};base64,${base64}`;
    
    console.log(`[Base64 轉換] 成功轉換: ${url} (${contentType}, ${buffer.byteLength} bytes)`);

    // 返回 JSON 響應包含 base64 data URL
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Cache-Control', 'public, max-age=3600'); // 快取 1 小時
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    res.json({
      success: true,
      dataUrl: dataUrl,
      originalUrl: url,
      contentType: contentType,
      size: buffer.byteLength
    });

  } catch (error) {
    console.error('[Base64 轉換] 錯誤:', error);
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        return res.status(408).json({ 
          error: 'Request timeout (30s)',
          url: url
        });
      }
      
      return res.status(500).json({ 
        error: 'Failed to convert to base64',
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
