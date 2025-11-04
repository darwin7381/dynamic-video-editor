import React from 'react';
import { CreatomateAsset, getAllTypes, TYPE_ICONS, TYPE_COLORS } from '../../utility/creatomateAssets';
import {
  ModalOverlay,
  AssetsModalContent,
  ModalHeader,
  ModalTitle,
  CloseModalButton,
  AssetsModalBody,
  AssetsDescription,
  TypeFilter,
  FilterButton,
  AssetsList,
  AssetItem,
  AssetInfo,
  AssetHeader,
  AssetTypeIcon,
  AssetName,
  AssetCategory,
  AssetDescription,
  AssetDetails,
  AssetDetail,
  AssetUrl,
  AssetActions,
  CopyAssetButton,
  LoadAssetButton,
  NoAssetsMessage,
} from './JsonTestStyles';

interface AssetsModalComponentProps {
  show: boolean;
  selectedType: 'all' | CreatomateAsset['type'];
  filteredAssets: CreatomateAsset[];
  onClose: () => void;
  onTypeChange: (type: 'all' | CreatomateAsset['type']) => void;
  onCopyAsset: (asset: CreatomateAsset) => void;
  onLoadAsset: (asset: CreatomateAsset) => void;
}

export const AssetsModalComponent: React.FC<AssetsModalComponentProps> = ({
  show,
  selectedType,
  filteredAssets,
  onClose,
  onTypeChange,
  onCopyAsset,
  onLoadAsset,
}) => {
  if (!show) {
    return null;
  }

  return (
    <ModalOverlay onClick={onClose}>
      <AssetsModalContent onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>📁 Creatomate 官方素材庫</ModalTitle>
          <CloseModalButton onClick={onClose}>×</CloseModalButton>
        </ModalHeader>
        
        <AssetsModalBody>
          <AssetsDescription>
            以下是經過驗證可以在 Creatomate Preview SDK 中正常使用的官方素材。
            點擊「載入」可以自動生成包含該素材的 JSON 模板。
          </AssetsDescription>
          
          {/* 類型篩選器 */}
          <TypeFilter>
            <FilterButton 
              $active={selectedType === 'all'}
              onClick={() => onTypeChange('all')}
            >
              🎯 全部
            </FilterButton>
            {getAllTypes().map(type => (
              <FilterButton
                key={type}
                $active={selectedType === type}
                onClick={() => onTypeChange(type)}
                style={{ color: TYPE_COLORS[type] }}
              >
                {TYPE_ICONS[type]} {type.toUpperCase()}
              </FilterButton>
            ))}
          </TypeFilter>
          
          {/* 素材列表 */}
          <AssetsList>
            {filteredAssets.map(asset => (
              <AssetItem key={asset.id}>
                <AssetInfo>
                  <AssetHeader>
                    <AssetTypeIcon style={{ color: TYPE_COLORS[asset.type] }}>
                      {TYPE_ICONS[asset.type]}
                    </AssetTypeIcon>
                    <AssetName>{asset.name}</AssetName>
                    <AssetCategory>{asset.category}</AssetCategory>
                  </AssetHeader>
                  <AssetDescription>{asset.description}</AssetDescription>
                  <AssetDetails>
                    {asset.resolution && <AssetDetail>📐 {asset.resolution}</AssetDetail>}
                    {asset.duration && <AssetDetail>⏱️ {asset.duration}</AssetDetail>}
                    {asset.size && <AssetDetail>💾 {asset.size}</AssetDetail>}
                  </AssetDetails>
                  <AssetUrl>{asset.url}</AssetUrl>
                </AssetInfo>
                <AssetActions>
                  <CopyAssetButton
                    onClick={() => onCopyAsset(asset)}
                    title="複製 URL 到剪貼簿"
                  >
                    📋 複製
                  </CopyAssetButton>
                  <LoadAssetButton
                    onClick={() => onLoadAsset(asset)}
                    title="載入此素材到 JSON 編輯器"
                  >
                    📥 載入
                  </LoadAssetButton>
                </AssetActions>
              </AssetItem>
            ))}
          </AssetsList>
          
          {filteredAssets.length === 0 && (
            <NoAssetsMessage>
              沒有找到 {selectedType === 'all' ? '' : selectedType.toUpperCase()} 類型的素材
            </NoAssetsMessage>
          )}
        </AssetsModalBody>
      </AssetsModalContent>
    </ModalOverlay>
  );
};

