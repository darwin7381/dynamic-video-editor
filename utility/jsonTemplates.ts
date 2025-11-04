/**
 * JSON 模板生成器
 */

import { CreatomateAsset } from './creatomateAssets';

/**
 * 生成素材展示 JSON 模板
 */
export function generateAssetTemplate(asset: CreatomateAsset): string {
  const template = {
    output_format: "mp4",
    width: 1920,
    height: 1080,
    fill_color: "#000000",
    elements: [
      {
        type: asset.type === 'gif' ? 'image' : asset.type,
        source: asset.url,
        ...(asset.type === 'image' || asset.type === 'gif' ? { fit: "cover" } : {}),
        time: "0 s",
        duration: asset.duration || "4 s"
      },
      {
        type: "text",
        name: "title",
        text: asset.name,
        font_family: "Noto Sans TC",
        font_size: "6 vh",
        font_weight: "700",
        fill_color: "#FFFFFF",
        x_alignment: "50%",
        y_alignment: "50%",
        y: "20%",
        width: "80%",
        background_color: "rgba(0,0,0,0.7)",
        time: "0.5 s",
        duration: "3 s"
      }
    ]
  };
  
  return JSON.stringify(template, null, 2);
}

