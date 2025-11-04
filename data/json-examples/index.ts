/**
 * JSON 示例索引
 * 
 * 這個檔案管理所有的 JSON 示例，每個示例都是一個獨立的檔案。
 * 使用時只需要 import 這個檔案，就可以取得所有示例。
 */

import welcomeExample from './01-welcome-example.json';
import imageSlideshowExample from './02-image-slideshow.json';
import professionalVideoExample from './03-professional-video.json';

export interface JsonExample {
  name: string;
  description: string;
  json: string;
}

export const JSON_EXAMPLES: JsonExample[] = [
  {
    name: '載入示例',
    description: '展示基本的視頻 + 字幕功能',
    json: JSON.stringify(welcomeExample, null, 2),
  },
  {
    name: '從文件載入',
    description: '圖片輪播與文字說明',
    json: JSON.stringify(imageSlideshowExample, null, 2),
  },
  {
    name: '載入新的JSON',
    description: '專業視頻編輯工具展示',
    json: JSON.stringify(professionalVideoExample, null, 2),
  },
];

export default JSON_EXAMPLES;

