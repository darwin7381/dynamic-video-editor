/**
 * Creatomate 官方素材庫
 * 這些是經過驗證可以在 Preview SDK 中正常使用的素材
 */

export interface CreatomateAsset {
  id: string;
  name: string;
  description: string;
  url: string;
  type: 'image' | 'video' | 'audio' | 'gif';
  category: string;
  size?: string;
  duration?: string;
  resolution?: string;
}

export const CREATOMATE_ASSETS: CreatomateAsset[] = [
  // 圖片素材 - 基於官方 GitHub 範例
  {
    id: 'img-1',
    name: '示範圖片 1',
    description: '官方範例圖片 - 經過驗證可用',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/image1.jpg',
    type: 'image',
    category: '官方範例',
    resolution: '1920x1080'
  },
  {
    id: 'img-2',
    name: '示範圖片 2',
    description: '官方範例圖片 - 經過驗證可用',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/image2.jpg',
    type: 'image',
    category: '官方範例',
    resolution: '1920x1080'
  },
  {
    id: 'img-3',
    name: '示範圖片 3',
    description: '官方範例圖片 - 經過驗證可用',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/image3.jpg',
    type: 'image',
    category: '官方範例',
    resolution: '1920x1080'
  },
  {
    id: 'img-samuel',
    name: 'Samuel Ferrara 攝影',
    description: '城市夜景攝影作品 - Unsplash',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/samuel-ferrara-1527pjeb6jg-unsplash.jpg',
    type: 'image',
    category: '攝影作品',
    resolution: '1920x1280'
  },
  {
    id: 'img-harshil',
    name: 'Harshil Gudka 攝影',
    description: '山景攝影作品 - Unsplash',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/harshil-gudka-77zGnfU_SFU-unsplash.jpg',
    type: 'image',
    category: '攝影作品',
    resolution: '1920x1280'
  },

  // 影片素材 - 基於官方 GitHub 範例
  {
    id: 'video-1',
    name: '示範影片 1',
    description: '官方範例影片 - 經過驗證可用',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/video1.mp4',
    type: 'video',
    category: '官方範例',
    duration: '15s',
    resolution: '1920x1080'
  },
  {
    id: 'video-4',
    name: '示範影片 4',
    description: '官方範例影片 - 用於音訊測試',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/video4.mp4',
    type: 'video',
    category: '官方範例',
    duration: '10s',
    resolution: '1920x1080'
  },

  // 音訊素材 - 基於官方 GitHub 範例
  {
    id: 'music-1',
    name: '背景音樂 1',
    description: '官方範例音樂 - 經過驗證可用',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/music1.mp3',
    type: 'audio',
    category: '背景音樂',
    duration: '30s',
    size: '1.5MB'
  },

  // 從我們現有程式碼中找到的有效素材
  {
    id: 'img-existing-1',
    name: '現有範例圖片',
    description: '程式碼中已使用的有效圖片',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/image1.jpg',
    type: 'image',
    category: '已驗證',
    resolution: '1920x1080'
  },
  {
    id: 'img-existing-2',
    name: 'Samuel Ferrara 作品',
    description: '程式碼中已使用的攝影作品',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/samuel-ferrara-1527pjeb6jg-unsplash.jpg',
    type: 'image',
    category: '已驗證',
    resolution: '1920x1280'
  },

  // 測試用素材 - 這些需要驗證
  {
    id: 'test-video-demo',
    name: '測試影片',
    description: '用於測試的基本影片',
    url: 'https://creatomate-static.s3.amazonaws.com/demo/video1.mp4',
    type: 'video',
    category: '測試素材',
    duration: '15s',
    resolution: '1920x1080'
  }
];

/**
 * 根據類型獲取素材
 */
export function getAssetsByType(type: CreatomateAsset['type']): CreatomateAsset[] {
  return CREATOMATE_ASSETS.filter(asset => asset.type === type);
}

/**
 * 根據分類獲取素材
 */
export function getAssetsByCategory(category: string): CreatomateAsset[] {
  return CREATOMATE_ASSETS.filter(asset => asset.category === category);
}

/**
 * 獲取所有分類
 */
export function getAllCategories(): string[] {
  const categories = CREATOMATE_ASSETS.map(asset => asset.category);
  return Array.from(new Set(categories));
}

/**
 * 獲取所有類型
 */
export function getAllTypes(): CreatomateAsset['type'][] {
  return ['image', 'video', 'audio', 'gif'];
}

/**
 * 根據 ID 獲取素材
 */
export function getAssetById(id: string): CreatomateAsset | undefined {
  return CREATOMATE_ASSETS.find(asset => asset.id === id);
}

/**
 * 搜尋素材
 */
export function searchAssets(query: string): CreatomateAsset[] {
  const lowercaseQuery = query.toLowerCase();
  return CREATOMATE_ASSETS.filter(asset => 
    asset.name.toLowerCase().includes(lowercaseQuery) ||
    asset.description.toLowerCase().includes(lowercaseQuery) ||
    asset.category.toLowerCase().includes(lowercaseQuery)
  );
}

/**
 * 類型對應的圖示
 */
export const TYPE_ICONS = {
  image: '🖼️',
  video: '🎬',
  audio: '🎵',
  gif: '🎭'
} as const;

/**
 * 類型對應的顏色
 */
export const TYPE_COLORS = {
  image: '#2196f3',
  video: '#9c27b0',
  audio: '#4caf50',
  gif: '#ff9800'
} as const;
