import { useState, useCallback } from 'react';
import { Preview } from '@creatomate/preview';
import { findElementRange, findElementRangeByPath, CurrentElementRange } from '../utility/urlHighlight';

/**
 * useTimeline Hook
 * 
 * 管理時間軸相關的所有邏輯：
 * - 時間軸元素管理
 * - 活躍元素追蹤
 * - 時間跳轉
 * - JSON 高亮同步
 */

interface TimelineElement {
  id: string;
  time: number;
  duration: number;
  type: string;
  name: string;
  text: string;
  source: string;
  path: string;
}

interface UseTimelineOptions {
  jsonInput: string;
  previewRef: React.MutableRefObject<Preview | undefined>;
  previewReady: boolean;
}

interface UseTimelineReturn {
  timelineElements: TimelineElement[];
  activeElementIndices: number[];
  currentEditingElement: number;
  autoHighlightRanges: CurrentElementRange[];
  clickedHighlightRange: CurrentElementRange | null;
  setTimelineElements: React.Dispatch<React.SetStateAction<TimelineElement[]>>;
  setCurrentEditingElement: React.Dispatch<React.SetStateAction<number>>;
  handleTimeChange: (time: number) => void;
  seekToTime: (time: number, elementIndex?: number, elementPath?: string) => Promise<void>;
}

export function useTimeline({
  jsonInput,
  previewRef,
  previewReady,
}: UseTimelineOptions): UseTimelineReturn {
  const [timelineElements, setTimelineElements] = useState<TimelineElement[]>([]);
  const [activeElementIndices, setActiveElementIndices] = useState<number[]>([]);
  const [currentEditingElement, setCurrentEditingElement] = useState<number>(-1);
  const [autoHighlightRanges, setAutoHighlightRanges] = useState<CurrentElementRange[]>([]);
  const [clickedHighlightRange, setClickedHighlightRange] = useState<CurrentElementRange | null>(null);

  // 處理時間變化
  const handleTimeChange = useCallback((time: number) => {
    if (!timelineElements || timelineElements.length === 0) return;
    
    // 找到所有活躍元素
    const activeElements = timelineElements
      .map((el, index) => ({ el, index }))
      .filter(({ el }) => {
        const inTimeRange = time >= el.time && time < (el.time + el.duration);
        const isNotComposition = el.type !== 'composition';
        return inTimeRange && isNotComposition;
      });
    
    if (activeElements.length > 0) {
      const ranges: CurrentElementRange[] = [];
      
      activeElements.forEach(({ el, index }) => {
        const range = el.path 
          ? findElementRangeByPath(jsonInput, el.path)
          : findElementRange(jsonInput, index);
        
        if (range) {
          ranges.push(range);
        }
      });
      
      setAutoHighlightRanges(ranges);
      const indices = activeElements.map(a => a.index);
      setActiveElementIndices(indices);
    } else {
      setAutoHighlightRanges([]);
      setActiveElementIndices([]);
    }
  }, [timelineElements, jsonInput]);

  // 跳轉到特定時間
  const seekToTime = useCallback(async (time: number, elementIndex?: number, elementPath?: string) => {
    if (!previewRef.current || !previewReady) return;
    
    try {
      await previewRef.current.setTime(time);
      console.log(`跳轉到時間: ${time}秒`);
      
      // 更新高亮狀態
      if (elementIndex !== undefined && elementIndex !== currentEditingElement) {
        setCurrentEditingElement(elementIndex);
        console.log(`🎯 同步更新高亮元素索引: ${elementIndex}, path: ${elementPath}`);
        
        const range = elementPath 
          ? findElementRangeByPath(jsonInput, elementPath)
          : findElementRange(jsonInput, elementIndex);
        
        if (range) {
          setClickedHighlightRange(range);
          console.log(`🎨 點擊高亮: ${range.start}-${range.end}, path: ${elementPath}`);
        }
      }
    } catch (err) {
      console.error('跳轉時間失敗:', err);
    }
  }, [previewReady, currentEditingElement, jsonInput, previewRef]);

  return {
    timelineElements,
    activeElementIndices,
    currentEditingElement,
    autoHighlightRanges,
    clickedHighlightRange,
    setTimelineElements,
    setCurrentEditingElement,
    handleTimeChange,
    seekToTime,
  };
}

