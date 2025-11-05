import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { JsonExample } from '../../data/json-examples';

interface ExampleDropdownProps {
  examples: JsonExample[];
  onSelectExample: (json: string) => void;
}

export const ExampleDropdown: React.FC<ExampleDropdownProps> = ({
  examples,
  onSelectExample,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // 除錯：列出收到的示例
  useEffect(() => {
    console.log('ExampleDropdown 收到的示例數量:', examples.length);
    console.log('示例列表:', examples.map(e => e.name));
  }, [examples]);

  // 點擊外部關閉下拉選單
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleSelectExample = (json: string) => {
    onSelectExample(json);
    setIsOpen(false);
  };

  return (
    <DropdownContainer ref={dropdownRef}>
      <DropdownButton onClick={() => setIsOpen(!isOpen)}>
        載入更多案例 {isOpen ? '▲' : '▼'}
      </DropdownButton>
      
      {isOpen && (
        <DropdownMenu>
          {examples.map((example, index) => (
            <DropdownItem
              key={index}
              onClick={() => handleSelectExample(example.json)}
            >
              {example.name}
            </DropdownItem>
          ))}
        </DropdownMenu>
      )}
    </DropdownContainer>
  );
};

const DropdownContainer = styled.div`
  position: relative;
  display: inline-block;
`;

const DropdownButton = styled.button`
  padding: 8px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
  
  &:hover {
    background: #1976d2;
  }
`;

const DropdownMenu = styled.div`
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  min-width: 280px;
  max-width: 400px;
  max-height: 60vh;
  overflow-y: auto;
  z-index: 1000;
  
  /* 滾動條美化 */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: #555;
  }
`;

const DropdownItem = styled.div`
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  font-family: 'Monaco', 'Menlo', monospace;
  white-space: nowrap;
  transition: background-color 0.1s;
  
  &:hover {
    background: #1976d2;
    color: white;
  }
  
  &:active {
    background: #1565c0;
  }
`;

