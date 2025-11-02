import { NextApiRequest, NextApiResponse} from 'next';

/**
 * GIF 轉 MP4 API（使用 CloudConvert）
 * 
 * CloudConvert: https://cloudconvert.com/
 * 免費額度: 25 次/天
 * 速度: 2-5 秒
 * 支援: GIF → MP4 ✅
 */

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { gifUrl } = req.body;

  if (!gifUrl) {
    return res.status(400).json({ error: 'Missing gifUrl parameter' });
  }

  try {
    console.log(`[GIF轉換] 開始轉換: ${gifUrl}`);
    
    const CLOUDCONVERT_API_KEY = process.env.CLOUDCONVERT_API_KEY;
    
    if (!CLOUDCONVERT_API_KEY) {
      throw new Error('CLOUDCONVERT_API_KEY 環境變數未設定');
    }

    // CloudConvert API 使用 Job-based 流程
    // 步驟 1: 創建 Job
    const jobResponse = await fetch('https://api.cloudconvert.com/v2/jobs', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${CLOUDCONVERT_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tasks: {
          'import-gif': {
            operation: 'import/url',
            url: gifUrl
          },
          'convert-to-mp4': {
            operation: 'convert',
            input: 'import-gif',
            input_format: 'gif',
            output_format: 'mp4'
          },
          'export-mp4': {
            operation: 'export/url',
            input: 'convert-to-mp4'
          }
        }
      })
    });

    if (!jobResponse.ok) {
      const errorText = await jobResponse.text();
      throw new Error(`CloudConvert Job 創建失敗: ${jobResponse.status} - ${errorText}`);
    }

    const job = await jobResponse.json();
    const jobId = job.data.id;
    
    console.log(`[GIF轉換] Job 已創建: ${jobId}`);

    // 步驟 2: 等待轉換完成
    let completed = false;
    let attempts = 0;
    const maxAttempts = 30; // 最多等待 30 秒
    
    while (!completed && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const statusResponse = await fetch(`https://api.cloudconvert.com/v2/jobs/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${CLOUDCONVERT_API_KEY}`
        }
      });
      
      const statusData = await statusResponse.json();
      const status = statusData.data.status;
      
      console.log(`[GIF轉換] 狀態: ${status} (${attempts + 1}/${maxAttempts})`);
      
      if (status === 'finished') {
        completed = true;
        
        // 取得轉換後的檔案 URL（CloudConvert 提供的臨時 URL）
        const exportTask = statusData.data.tasks.find((t: any) => t.operation === 'export/url');
        const mp4Url = exportTask.result.files[0].url;
        
        console.log(`[GIF轉換] ✅ 轉換完成`);
        console.log(`[GIF轉換] MP4 URL: ${mp4Url}`);

        // 🔧 關鍵：返回 URL，不是檔案內容！
        // 這個 URL 可以直接被 Creatomate iframe 訪問
        res.setHeader('Content-Type', 'application/json');
        res.json({ 
          success: true,
          mp4Url: mp4Url,  // CloudConvert 的臨時 URL（24小時有效）
          originalGifUrl: gifUrl
        });
        return;
        
      } else if (status === 'error') {
        throw new Error(`轉換失敗: ${JSON.stringify(statusData.data)}`);
      }
      
      attempts++;
    }
    
    if (!completed) {
      throw new Error('轉換超時');
    }

  } catch (error) {
    console.error('[GIF轉換] 錯誤:', error);
    return res.status(500).json({ 
      error: 'GIF 轉換失敗',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

export const config = {
  api: {
    responseLimit: '50mb',
  },
};

