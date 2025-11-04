import { useRef, useState, useCallback } from 'react';
import { Preview, PreviewState } from '@creatomate/preview';
import { cacheExternalAssets, replaceGifUrlsInJson } from '../utility/cacheAssetHelper';
import { UrlStatus } from '../utility/urlHighlight';

/**
 * usePreviewManager Hook
 * 
 * 管理 Creatomate Preview SDK 的所有邏輯：
 * - Preview 實例初始化
 * - JSON 處理和快取
 * - 狀態管理
 * - 錯誤處理
 */

interface UsePreviewManagerOptions {
  jsonInput: string;
  onTimelineElementsParsed: (elements: any[]) => void;
  parseTimelineElements: (source: any) => any[];
  onTimeChange: (time: number) => void;
}

interface UsePreviewManagerReturn {
  previewRef: React.MutableRefObject<Preview | undefined>;
  previewContainerRef: React.MutableRefObject<HTMLDivElement | null>;
  previewReady: boolean;
  isLoading: boolean;
  error: string | null;
  currentState: PreviewState | undefined;
  processedSource: any;
  urlMapping: Map<string, string>;
  urlStatus: Map<string, UrlStatus>;
  setError: (error: string | null) => void;
  setUrlStatus: React.Dispatch<React.SetStateAction<Map<string, UrlStatus>>>;
  setUpPreview: (htmlElement: HTMLDivElement) => void;
  createVideo: () => Promise<void>;
}

export function usePreviewManager({
  jsonInput,
  onTimelineElementsParsed,
  parseTimelineElements,
  onTimeChange,
}: UsePreviewManagerOptions): UsePreviewManagerReturn {
  const previewRef = useRef<Preview>();
  const previewContainerRef = useRef<HTMLDivElement | null>(null);
  
  const [previewReady, setPreviewReady] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentState, setCurrentState] = useState<PreviewState>();
  
  // 中間處理層
  const [processedSource, setProcessedSource] = useState<any>(null);
  const [urlMapping, setUrlMapping] = useState<Map<string, string>>(new Map());
  const [urlStatus, setUrlStatus] = useState<Map<string, UrlStatus>>(new Map());

  // 設置預覽
  const setUpPreview = useCallback((htmlElement: HTMLDivElement) => {
    if (previewRef.current) {
      previewRef.current.dispose();
      previewRef.current = undefined;
    }

    if (!process.env.NEXT_PUBLIC_CREATOMATE_PUBLIC_TOKEN) {
      setError('請設置 NEXT_PUBLIC_CREATOMATE_PUBLIC_TOKEN 環境變數');
      return;
    }

    try {
      console.log('初始化預覽...');
      const preview = new Preview(htmlElement, 'player', process.env.NEXT_PUBLIC_CREATOMATE_PUBLIC_TOKEN);

      preview.onReady = async () => {
        console.log('SDK準備就緒，開始初始化...');
        try {
          setIsLoading(true);
          
          // 設定影片快取規則
          console.log('🔧 設定影片快取規則...');
          try {
            await preview.setCacheBypassRules([/.*/]);
            console.log('✅ 影片快取規則設定完成');
          } catch (cacheRuleError) {
            console.warn('⚠️ 快取規則設定失敗:', cacheRuleError);
          }
          
          // 載入 template（如果有）
          if (process.env.NEXT_PUBLIC_TEMPLATE_ID) {
            console.log('先載入基礎模板...');
            try {
              await preview.loadTemplate(process.env.NEXT_PUBLIC_TEMPLATE_ID);
              console.log('基礎模板載入完成');
            } catch (templateError) {
              console.warn('基礎模板載入失敗，繼續使用 JSON 直接輸入:', templateError);
            }
          }
          
          // 解析 JSON
          const source = JSON.parse(jsonInput);
          console.log('原始JSON source:', source);
          
          // 快取外部素材
          console.log('🔧 [初始化] 開始快取外部素材...');
          const cacheResult = await cacheExternalAssets(
            preview, 
            source,
            (url, status) => {
              setUrlStatus(prev => new Map(prev).set(url, status));
            }
          );
          console.log(`✅ [初始化] 快取完成 - 成功: ${cacheResult.success.length}, 失敗: ${cacheResult.failed.length}`);
          
          // 處理 JSON
          let processedSrc = source;
          if (cacheResult.urlMapping.size > 0) {
            console.log('🔧 [初始化] 應用 URL 映射...');
            processedSrc = replaceGifUrlsInJson(source, cacheResult.urlMapping);
            setUrlMapping(cacheResult.urlMapping);
          }
          setProcessedSource(processedSrc);
          
          // 轉換為 snake_case
          const convertToSnakeCase = (obj: any): any => {
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
          };
          
          const convertedSource = convertToSnakeCase(processedSrc);
          console.log('[中間層] 處理後的 JSON:', convertedSource);
          
          await preview.setSource(convertedSource);
          console.log('✅ JSON設置完成');
          
          // 解析時間軸元素
          const elements = parseTimelineElements(source);
          onTimelineElementsParsed(elements);
          
          setPreviewReady(true);
          setError(null);
          setIsLoading(false);
        } catch (err) {
          console.error('初始化失敗:', err);
          setError(`初始化失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
          setIsLoading(false);
        }
      };

      preview.onLoad = () => {
        console.log('開始載入...');
        setIsLoading(true);
      };

      preview.onLoadComplete = () => {
        console.log('載入完成');
        setIsLoading(false);
      };

      preview.onStateChange = (state) => {
        console.log('狀態變更:', state);
        setCurrentState(state);
      };
      
      preview.onTimeChange = onTimeChange;

      previewRef.current = preview;
    } catch (err) {
      console.error('預覽初始化失敗:', err);
      setError(`預覽初始化失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
    }
  }, [jsonInput, onTimeChange, parseTimelineElements, onTimelineElementsParsed]);

  // 創建視頻
  const createVideo = useCallback(async () => {
    if (!previewRef.current) return;

    try {
      setIsLoading(true);
      const source = previewRef.current.getSource();
      
      const response = await fetch('/api/videos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ source }),
      });

      if (!response.ok) {
        throw new Error(`渲染失敗: ${response.status}`);
      }

      const result = await response.json();
      if (result.status === 'succeeded') {
        window.open(result.url, '_blank');
      } else {
        setError(`渲染失敗: ${result.errorMessage || '未知錯誤'}`);
      }
    } catch (err) {
      setError(`創建視頻失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    previewRef,
    previewContainerRef,
    previewReady,
    isLoading,
    error,
    currentState,
    processedSource,
    urlMapping,
    urlStatus,
    setError,
    setUrlStatus,
    setUpPreview,
    createVideo,
  };
}

