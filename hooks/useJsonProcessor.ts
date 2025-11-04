import { useCallback, useEffect } from 'react';
import { Preview } from '@creatomate/preview';
import { cacheExternalAssets, replaceGifUrlsInJson } from '../utility/cacheAssetHelper';
import { UrlStatus } from '../utility/urlHighlight';

/**
 * useJsonProcessor Hook
 * 
 * 管理 JSON 處理相關的邏輯：
 * - JSON 即時更新
 * - 外部素材快取
 * - URL 映射處理
 * - snake_case 轉換
 */

interface UseJsonProcessorOptions {
  jsonInput: string;
  previewRef: React.MutableRefObject<Preview | undefined>;
  previewReady: boolean;
  parseTimelineElements: (source: any) => any[];
  onTimelineElementsParsed: (elements: any[]) => void;
  setProcessedSource: (source: any) => void;
  setUrlMapping: React.Dispatch<React.SetStateAction<Map<string, string>>>;
  setUrlStatus: React.Dispatch<React.SetStateAction<Map<string, UrlStatus>>>;
  setError: (error: string | null) => void;
}

export function useJsonProcessor({
  jsonInput,
  previewRef,
  previewReady,
  parseTimelineElements,
  onTimelineElementsParsed,
  setProcessedSource,
  setUrlMapping,
  setUrlStatus,
  setError,
}: UseJsonProcessorOptions) {
  // 轉換為 snake_case 的輔助函數
  const convertToSnakeCase = useCallback((obj: any): any => {
    if (Array.isArray(obj)) {
      return obj.map(item => convertToSnakeCase(item));
    } else if (obj !== null && typeof obj === 'object') {
      const newObj: any = {};
      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
          newObj[snakeKey] = convertToSnakeCase(obj[key]);
        }
      }
      return newObj;
    }
    return obj;
  }, []);

  // JSON 即時更新
  useEffect(() => {
    if (!previewReady || !previewRef.current) return;

    const timeoutId = setTimeout(async () => {
      try {
        setError(null);
        const source = JSON.parse(jsonInput);
        
        // 快取外部素材
        console.log('🔧 [即時更新] 開始快取外部素材...');
        const cacheResult = await cacheExternalAssets(
          previewRef.current!,
          source,
          (url, status) => {
            setUrlStatus(prev => new Map(prev).set(url, status));
          }
        );
        console.log(`✅ [即時更新] 快取完成 - 成功: ${cacheResult.success.length}, 失敗: ${cacheResult.failed.length}`);
        
        // 處理 JSON
        let processedSrc = source;
        if (cacheResult.urlMapping.size > 0) {
          console.log('🔧 [即時更新] 應用 URL 映射...');
          processedSrc = replaceGifUrlsInJson(source, cacheResult.urlMapping);
          setUrlMapping(cacheResult.urlMapping);
        }
        setProcessedSource(processedSrc);
        
        // 解析時間軸元素
        const elements = parseTimelineElements(source);
        onTimelineElementsParsed(elements);
        
        // 轉換並設置
        const convertedSource = convertToSnakeCase(processedSrc);
        console.log('[中間層] 即時更新 - 處理後的 JSON');
        
        await previewRef.current!.setSource(convertedSource);
        console.log('JSON更新成功，時間軸元素:', elements.length);
      } catch (err) {
        console.error('JSON更新失敗:', err);
        if (err instanceof SyntaxError) {
          setError(`JSON語法錯誤: ${err.message}`);
        }
      }
    }, 800); // 防抖

    return () => clearTimeout(timeoutId);
  }, [
    jsonInput, 
    previewReady, 
    previewRef,
    parseTimelineElements,
    onTimelineElementsParsed,
    setProcessedSource,
    setUrlMapping,
    setUrlStatus,
    setError,
    convertToSnakeCase,
  ]);
}

