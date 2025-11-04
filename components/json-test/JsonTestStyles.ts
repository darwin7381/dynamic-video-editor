import styled from 'styled-components';

export const Container = styled.div`
  min-height: 100vh;
  background: #f5f5f5;
`;

export const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
`;

export const BackLink = styled.div`
  a {
    color: #2196f3;
    text-decoration: none;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

export const Title = styled.h1`
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

export const CreateButton = styled.button`
  padding: 12px 24px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  
  &:hover:not(:disabled) {
    background: #45a049;
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

export const MainContent = styled.div`
  display: flex;
  height: calc(100vh - 80px);
`;

export const LeftPanel = styled.div`
  flex: 1;
  padding: 20px;
  background: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
`;

export const RightPanel = styled.div`
  flex: 1;
  padding: 20px;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
`;

export const SectionTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
`;

export const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
`;

export const ExampleButton = styled.button`
  padding: 8px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: #1976d2;
  }
`;

export const CopyApiButton = styled.button`
  padding: 8px 16px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: #45a049;
  }
  
  &:active {
    background: #3d8b40;
  }
`;

export const ImportApiButton = styled.button`
  padding: 8px 16px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: #45a049;
  }
  
  &:active {
    background: #3d8b40;
  }
`;

export const TestImageButton = styled.button`
  padding: 8px 16px;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
  
  &:hover:not(:disabled) {
    background: #f57c00;
  }
  
  &:active:not(:disabled) {
    background: #ef6c00;
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

export const TestBase64Button = styled.button`
  padding: 8px 16px;
  background: #9c27b0;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
  
  &:hover:not(:disabled) {
    background: #7b1fa2;
  }
  
  &:active:not(:disabled) {
    background: #6a1b9a;
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

export const AssetsButton = styled.button`
  padding: 8px 16px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: #45a049;
  }
  
  &:active {
    background: #3d8b40;
  }
`;

export const EditorContainer = styled.div`
  position: relative;
  flex: 1;
  display: flex;
`;

export const JSONTextarea = styled.textarea`
  flex: 1;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  outline: none;
  background: transparent;  /* 讓高亮層可見 */
  position: relative;
  z-index: 2;  /* 在高亮層上方 */
  color: #333;
  
  &:focus {
    border-color: #2196f3;
  }
`;

/* 通用 Overlay 樣式 */
const baseOverlayStyle = `
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 15px;
  pointer-events: none;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: hidden;
  color: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
`;

/* 層1: 自動播放高亮（淡藍，無邊線）*/
export const AutoHighlightOverlay = styled.div.attrs({ 'data-overlay': true })`
  ${baseOverlayStyle}
  z-index: 1;
  
  .element-block-highlight {
    display: block;
    background-color: rgba(33, 150, 243, 0.08);  /* 淡藍背景（被動）*/
    /* 無左側邊線 */
  }
`;

/* 層2: 點擊選中高亮（淡藍，有粗邊線）*/
export const ClickedHighlightOverlay = styled.div.attrs({ 'data-overlay': true })`
  ${baseOverlayStyle}
  z-index: 2;
  
  .element-block-highlight {
    display: block;
    background-color: rgba(33, 150, 243, 0.08);  /* 淡藍背景（與被動相同）*/
    border-left: 4px solid #2196f3;  /* 藍色粗線（主動標記）*/
  }
`;

/* 層3: URL 狀態高亮 */
export const UrlHighlightOverlay = styled.div.attrs({ 'data-overlay': true })`
  ${baseOverlayStyle}
  z-index: 3;
`;

export const PreviewContainer = styled.div`
  flex: 1;
  background: #000;
  border-radius: 8px;
  position: relative;
  min-height: 400px;
`;

export const ErrorMessage = styled.div`
  color: #f44336;
  background: #ffebee;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
`;

export const LoadingIndicator = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-size: 18px;
  font-weight: 600;
`;

export const TimelinePanel = styled.div`
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
`;

export const TimelinePanelTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: #333;
`;

export const TimelineElementsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
`;

export const TimelineElement = styled.div<{ $isActive?: boolean; $isClicked?: boolean }>`
  display: flex;
  align-items: center;
  padding: 10px;
  
  /* 背景：播放中的元素顯示淡綠 */
  background: ${props => props.$isActive ? 'rgba(76, 175, 80, 0.12)' : '#f8f9fa'};
  
  /* 外框：點擊選中的元素顯示藍色粗框 */
  border: ${props => 
    props.$isClicked ? '2px solid #2196f3' :  /* 點擊：藍色粗框 */
    '1px solid transparent'  /* 其他：無框 */
  };
  
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  
  &:hover {
    background: ${props => 
      props.$isClicked ? '#bbdefb' :  /* 點擊的：hover 深藍 */
      props.$isActive ? 'rgba(76, 175, 80, 0.18)' :  /* 活躍的：hover 深綠 */
      '#e9ecef'  /* 其他：淺灰 */
    };
  }
`;

export const ElementTime = styled.div`
  min-width: 50px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #2196f3;
  margin-right: 8px;  /* 時間右側間距 */
  flex-shrink: 0;
`;

export const ElementInfo = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;  /* 允許文字截斷 */
`;

export const ElementType = styled.div`
  font-size: 14px;
  color: #333;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

export const ElementText = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-style: italic;
`;

export const CurrentTimeInfo = styled.div`
  font-size: 14px;
  color: #666;
  text-align: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
`;

export const ActiveIndicator = styled.div`
  width: 20px;  /* 固定寬度，確保對齊 */
  color: #2196f3;
  font-size: 16px;
  font-weight: bold;
  text-align: center;
  animation: pulse 1.5s infinite;
  flex-shrink: 0;
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

export const AutoJumpHint = styled.span`
  font-size: 12px;
  color: #666;
  font-weight: normal;
  margin-left: 10px;
`;

export const TypeBadge = styled.div<{ $type: string }>`
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  white-space: nowrap;
  background: ${props => {
    switch (props.$type) {
      case 'video': return '#ff6b6b';
      case 'audio': return '#4ecdc4';
      case 'text': return '#45b7d1';
      case 'image': return '#f9ca24';
      case 'composition': return '#6c5ce7';
      case 'shape': return '#a29bfe';
      default: return '#74b9ff';
    }
  }};
  color: white;
  margin-left: auto;  /* 推到最右邊 */
  margin-right: 10px;
  align-self: center;
`;

/* Modal 樣式 */
export const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

export const ModalContent = styled.div`
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
`;

export const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
`;

export const ModalTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

export const CloseModalButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: #333;
  }
`;

export const ModalBody = styled.div`
  padding: 24px;
  flex: 1;
  overflow-y: auto;
`;

export const ModalDescription = styled.p`
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
  line-height: 1.5;
`;

export const ImportTextarea = styled.textarea`
  width: 100%;
  height: 300px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  resize: vertical;
  outline: none;
  
  &:focus {
    border-color: #4caf50;
  }
`;

export const ModalFooter = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
`;

export const CancelButton = styled.button`
  padding: 10px 20px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: #e0e0e0;
  }
`;

export const ImportButton = styled.button`
  padding: 10px 20px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  
  &:hover {
    background: #45a049;
  }
`;

// 素材彈窗樣式
export const AssetsModalContent = styled(ModalContent)`
  width: 90vw;
  max-width: 1000px;
  height: 80vh;
  max-height: 600px;
`;

export const AssetsModalBody = styled.div`
  padding: 20px;
  height: calc(100% - 60px);
  overflow-y: auto;
`;

export const AssetsDescription = styled.p`
  color: #666;
  margin: 0 0 20px 0;
  line-height: 1.5;
  font-size: 14px;
`;

export const TypeFilter = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
`;

export const FilterButton = styled.button<{ $active: boolean }>`
  padding: 6px 12px;
  border: 1px solid ${props => props.$active ? '#2196f3' : '#ddd'};
  background: ${props => props.$active ? '#2196f3' : 'white'};
  color: ${props => props.$active ? 'white' : '#333'};
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #2196f3;
    background: ${props => props.$active ? '#1976d2' : '#f0f8ff'};
  }
`;

export const AssetsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

export const AssetItem = styled.div`
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f0f0f0;
    border-color: #2196f3;
  }
`;

export const AssetInfo = styled.div`
  flex: 1;
  margin-right: 16px;
`;

export const AssetHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
`;

export const AssetTypeIcon = styled.span`
  font-size: 16px;
`;

export const AssetName = styled.h4`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
`;

export const AssetCategory = styled.span`
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
`;

export const AssetDescription = styled.p`
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
`;

export const AssetDetails = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
`;

export const AssetDetail = styled.span`
  font-size: 12px;
  color: #888;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
`;

export const AssetUrl = styled.div`
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 11px;
  color: #888;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  word-break: break-all;
  border: 1px solid #e0e0e0;
`;

export const AssetActions = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const CopyAssetButton = styled.button`
  padding: 6px 12px;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
  
  &:hover {
    background: #f57c00;
  }
`;

export const LoadAssetButton = styled.button`
  padding: 6px 12px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
  
  &:hover {
    background: #45a049;
  }
`;

export const NoAssetsMessage = styled.div`
  text-align: center;
  color: #888;
  font-style: italic;
  padding: 40px 20px;
`;

