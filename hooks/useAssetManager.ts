/**
 * Asset Manager Hook
 * 管理素材庫相關的所有邏輯
 */

import { useState } from 'react';
import { CreatomateAsset, CREATOMATE_ASSETS, getAssetsByType } from '../utility/creatomateAssets';
import { generateAssetTemplate } from '../utility/jsonTemplates';

interface UseAssetManagerOptions {
  setJsonInput: (json: string) => void;
  setError: (error: string | null) => void;
  error: string | null;
}

export function useAssetManager({
  setJsonInput,
  setError,
  error,
}: UseAssetManagerOptions) {
  const [showAssetsModal, setShowAssetsModal] = useState(false);
  const [selectedAssetType, setSelectedAssetType] = useState<'all' | CreatomateAsset['type']>('all');
  
  // 獲取篩選後的素材列表
  const filteredAssets = selectedAssetType === 'all' 
    ? CREATOMATE_ASSETS 
    : getAssetsByType(selectedAssetType);
  
  // 複製素材 URL 到剪貼簿
  const copyAssetUrl = async (asset: CreatomateAsset) => {
    try {
      await navigator.clipboard.writeText(asset.url);
      setError(null);
      const originalError = error;
      setError(`✅ 已複製：${asset.name}`);
      setTimeout(() => setError(originalError), 2000);
    } catch (err) {
      setError('複製失敗，請手動複製');
    }
  };
  
  // 載入素材到 JSON 編輯器
  const loadAssetToJson = (asset: CreatomateAsset) => {
    const assetJson = generateAssetTemplate(asset);
    setJsonInput(assetJson);
    setShowAssetsModal(false);
  };
  
  return {
    showAssetsModal,
    setShowAssetsModal,
    selectedAssetType,
    setSelectedAssetType,
    filteredAssets,
    copyAssetUrl,
    loadAssetToJson,
  };
}

