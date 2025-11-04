import React from 'react';
import {
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalTitle,
  CloseModalButton,
  ModalBody,
  ModalDescription,
  ImportTextarea,
  ModalFooter,
  CancelButton,
  ImportButton,
} from './JsonTestStyles';

interface ImportModalComponentProps {
  show: boolean;
  jsonInput: string;
  onClose: () => void;
  onImport: () => void;
  onInputChange: (value: string) => void;
}

export const ImportModalComponent: React.FC<ImportModalComponentProps> = ({
  show,
  jsonInput,
  onClose,
  onImport,
  onInputChange,
}) => {
  if (!show) {
    return null;
  }

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>匯入 JSON 請求</ModalTitle>
          <CloseModalButton onClick={onClose}>×</CloseModalButton>
        </ModalHeader>
        
        <ModalBody>
          <ModalDescription>
            請貼入完整的 API 請求格式 JSON（包含 source 和 output_format）
          </ModalDescription>
          <ImportTextarea
            value={jsonInput}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder={`請貼入如下格式的 JSON：
{
  "source": {
    "outputFormat": "mp4",
    "width": 1920,
    "height": 1080,
    "elements": [...]
  },
  "output_format": "mp4"
}`}
          />
        </ModalBody>
        
        <ModalFooter>
          <CancelButton onClick={onClose}>
            取消
          </CancelButton>
          <ImportButton onClick={onImport}>
            匯入
          </ImportButton>
        </ModalFooter>
      </ModalContent>
    </ModalOverlay>
  );
};

