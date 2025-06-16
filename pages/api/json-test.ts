import { NextApiRequest, NextApiResponse } from 'next';
import { Client } from 'creatomate';

const client = new Client(process.env.CREATOMATE_API_KEY!);

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  return new Promise<void>((resolve) => {
    if (req.method === 'POST') {
      // 檢查 API 密鑰
      if (!process.env.CREATOMATE_API_KEY) {
        res.status(401).json({ 
          error: '未設置 CREATOMATE_API_KEY 環境變數',
          message: '請在 .env.local 文件中設置 CREATOMATE_API_KEY' 
        });
        resolve();
        return;
      }

      try {
        // 驗證請求體
        if (!req.body || !req.body.source) {
          res.status(400).json({ 
            error: '缺少必要參數',
            message: '請提供有效的 JSON 源' 
          });
          resolve();
          return;
        }

        const { source, action = 'preview' } = req.body;

        // 驗證 JSON 格式
        if (typeof source !== 'object') {
          res.status(400).json({ 
            error: 'JSON 格式錯誤',
            message: '源必須是有效的 JSON 物件' 
          });
          resolve();
          return;
        }

        // 基本的 JSON 結構驗證
        if (!source.output_format) {
          res.status(400).json({ 
            error: 'JSON 結構錯誤',
            message: '缺少必要字段：output_format' 
          });
          resolve();
          return;
        }

        if (action === 'preview') {
          // 對於預覽，我們只返回驗證後的源
          res.status(200).json({
            success: true,
            message: 'JSON 驗證成功',
            source: source,
            action: 'preview'
          });
          resolve();
        } else if (action === 'render') {
          // 對於渲染，調用 Creatomate API
          const renderOptions = {
            source: source,
          };

          client
            .render(renderOptions)
            .then((renders) => {
              res.status(200).json({
                success: true,
                message: '視頻渲染成功',
                render: renders[0],
                action: 'render'
              });
              resolve();
            })
            .catch((error) => {
              console.error('Creatomate API 錯誤:', error);
              res.status(500).json({ 
                error: '渲染失敗',
                message: error.message || '未知錯誤',
                details: error
              });
              resolve();
            });
        } else {
          res.status(400).json({ 
            error: '無效操作',
            message: 'action 必須是 "preview" 或 "render"' 
          });
          resolve();
        }

      } catch (error) {
        console.error('API 處理錯誤:', error);
        res.status(500).json({ 
          error: '服務器錯誤',
          message: error instanceof Error ? error.message : '未知錯誤' 
        });
        resolve();
      }

    } else if (req.method === 'GET') {
      // 返回API狀態和示例
      res.status(200).json({
        status: 'active',
        message: 'JSON 測試 API 正常運行',
        endpoints: {
          preview: 'POST /api/json-test { "source": {...}, "action": "preview" }',
          render: 'POST /api/json-test { "source": {...}, "action": "render" }'
        },
        example: {
          output_format: "mp4",
          duration: "3 s",
          width: 1920,
          height: 1080,
          elements: [
            {
              type: "text",
              track: 1,
              time: "0 s",
              duration: "1 s",
              fill_color: "#ffffff",
              text: "Hello World",
              font_family: "Open Sans"
            }
          ]
        }
      });
      resolve();

    } else {
      res.status(405).json({ 
        error: '方法不允許',
        message: '只支持 GET 和 POST 請求' 
      });
      resolve();
    }
  });
} 