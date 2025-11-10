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

interface ElementsImportModalComponentProps {
  show: boolean;
  elementsInput: string;
  onClose: () => void;
  onImport: () => void;
  onInputChange: (value: string) => void;
}

export const ElementsImportModalComponent: React.FC<ElementsImportModalComponentProps> = ({
  show,
  elementsInput,
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
          <ModalTitle>匯入 Elements</ModalTitle>
          <CloseModalButton onClick={onClose}>×</CloseModalButton>
        </ModalHeader>
        
        <ModalBody>
          <ModalDescription>
            支援四種格式：<br/>
            1. 帶有 "elements": [...] 的完整物件<br/>
            2. 直接的 [...] 陣列<br/>
            3. 直接的 "elements": [...] 字串<br/>
            4. 多個元素物件(用逗號分隔)
          </ModalDescription>
          <ImportTextarea
            value={elementsInput}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder={`請貼入以下任一格式：

格式1 - 完整物件:
{ "elements": [{ "type": "text", ... }] }

格式2 - 直接陣列:
[{ "type": "text", ... }]

格式3 - elements 字串:
"elements": [{ "type": "text", ... }]

格式4 - 多個元素:
{ "type": "text", ... },
{ "type": "image", ... }`}
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

