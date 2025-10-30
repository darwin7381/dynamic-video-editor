import { NextApiRequest, NextApiResponse } from 'next';

/**
 * GIF 轉 MP4 API
 * 
 * 問題：Creatomate Preview SDK 中，type="video" 的 GIF 會顯示黑畫面
 * 解決：將 GIF 轉換為 MP4，讓 Preview 能正常播放
 * 
 * 使用方式：
 * const mp4Url = `/api/gif-to-video?url=${encodeURIComponent(gifUrl)}`;
 * await preview.cacheAsset(mp4Url, mp4Blob);
 */

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { url } = req.query;

  if (!url || typeof url !== 'string') {
    return res.status(400).json({ 
      error: 'Missing URL parameter',
      usage: '/api/gif-to-video?url=https://example.com/animation.gif'
    });
  }

  try {
    console.log(`[GIF轉換] 開始處理: ${url}`);
    
    // 下載 GIF
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch GIF: ${response.status}`);
    }

    const gifBuffer = await response.arrayBuffer();
    console.log(`[GIF轉換] GIF 下載完成: ${gifBuffer.byteLength} bytes`);

    // 🔧 暫時方案：直接返回 GIF（讓 cacheAsset 處理）
    // TODO: 如果需要真正轉換，需要使用 FFmpeg
    
    res.setHeader('Content-Type', 'image/gif');
    res.setHeader('Cache-Control', 'public, max-age=86400');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.send(Buffer.from(gifBuffer));

    console.log(`[GIF轉換] 返回 GIF（暫未轉換）`);

  } catch (error) {
    console.error('[GIF轉換] 錯誤:', error);
    return res.status(500).json({ 
      error: 'Failed to process GIF',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

export const config = {
  api: {
    responseLimit: '50mb',
  },
};

