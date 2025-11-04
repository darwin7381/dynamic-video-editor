import React from 'react';
import { PreviewState } from '@creatomate/preview';
import {
  TimelinePanel,
  TimelinePanelTitle,
  AutoJumpHint,
  TimelineElementsContainer,
  TimelineElement,
  ActiveIndicator,
  ElementTime,
  ElementInfo,
  ElementType,
  ElementText,
  TypeBadge,
  CurrentTimeInfo,
} from './JsonTestStyles';

export interface TimelineElementData {
  id: string;
  time: number;
  duration: number;
  type: string;
  name: string;
  text: string;
  source: string;
  path: string;
}

interface TimelinePanelComponentProps {
  timelineElements: TimelineElementData[];
  currentState?: PreviewState;
  activeElementIndices: number[];
  currentEditingElement: number;
  onSeekToTime: (time: number, index: number, path: string) => void;
}

export const TimelinePanelComponent: React.FC<TimelinePanelComponentProps> = ({
  timelineElements,
  currentState,
  activeElementIndices,
  currentEditingElement,
  onSeekToTime,
}) => {
  if (!timelineElements || timelineElements.length === 0) {
    return null;
  }

  return (
    <TimelinePanel>
      <TimelinePanelTitle>
        時間軸控制 
        <AutoJumpHint>💡 編輯JSON時會自動跳轉</AutoJumpHint>
      </TimelinePanelTitle>
      
      <TimelineElementsContainer>
        {timelineElements.map((element, index) => (
          <TimelineElement
            key={element.id}
            $isActive={activeElementIndices.includes(index)}
            $isClicked={index === currentEditingElement}
            onClick={() => onSeekToTime(element.time, index, element.path)}
          >
            <ActiveIndicator>
              {index === currentEditingElement ? '●' : ''}
            </ActiveIndicator>
            <ElementTime>{element.time}s</ElementTime>
            <ElementInfo>
              <ElementType>{element.name}</ElementType>
              <ElementText>{element.text}</ElementText>
            </ElementInfo>
            <TypeBadge $type={element.type}>{element.type}</TypeBadge>
          </TimelineElement>
        ))}
      </TimelineElementsContainer>
      
      {currentState && (
        <CurrentTimeInfo>
          視頻尺寸: {currentState.width} x {currentState.height}
          {currentState.duration && ` | 時長: ${currentState.duration.toFixed(1)}s`}
        </CurrentTimeInfo>
      )}
    </TimelinePanel>
  );
};

