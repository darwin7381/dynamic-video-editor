import React, { useRef, useState, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Preview, PreviewState } from '@creatomate/preview';
import { cacheExternalAssets, replaceGifUrlsInJson } from '../../utility/cacheAssetHelper';
import { generateHighlightedText, generateMultipleElementHighlights, findElementRange, findElementRangeByPath, UrlStatus, CurrentElementRange } from '../../utility/urlHighlight';
import { convertToSnakeCase, parseTime, estimateDuration } from '../../utility/jsonHelpers';
import { parseTimelineElements, TimelineElement } from '../../utility/timelineParser';
import { detectCurrentElement } from '../../utility/elementDetector';
import { generateAssetTemplate } from '../../utility/jsonTemplates';
import { convertToApiRequest, extractFromApiRequest, showCopyFeedback } from '../../utility/apiRequestHelpers';
import { CREATOMATE_ASSETS, getAssetsByType, getAllTypes, TYPE_ICONS, TYPE_COLORS, CreatomateAsset } from '../../utility/creatomateAssets';
import { TimelinePanelComponent } from '../../components/json-test/TimelinePanelComponent';
import { ImportModalComponent } from '../../components/json-test/ImportModalComponent';
import { AssetsModalComponent } from '../../components/json-test/AssetsModalComponent';
import { JSON_EXAMPLES, DEFAULT_JSON } from '../../data/json-examples';
import { usePreviewManager } from '../../hooks/usePreviewManager';
import { useTimeline } from '../../hooks/useTimeline';
import { useJsonProcessor } from '../../hooks/useJsonProcessor';
import { useAssetManager } from '../../hooks/useAssetManager';
import { useImportExport } from '../../hooks/useImportExport';
import {
  Container,
  Header,
  BackLink,
  Title,
  CreateButton,
  MainContent,
  LeftPanel,
  RightPanel,
  SectionTitle,
  ButtonGroup,
  ExampleButton,
  CopyApiButton,
  ImportApiButton,
  TestImageButton,
  TestBase64Button,
  AssetsButton,
  EditorContainer,
  JSONTextarea,
  AutoHighlightOverlay,
  ClickedHighlightOverlay,
  UrlHighlightOverlay,
  PreviewContainer,
  ErrorMessage,
  LoadingIndicator,
  TimelinePanel,
  TimelinePanelTitle,
  TimelineElementsContainer,
  TimelineElement as TimelineElementStyled,
  ElementTime,
  ElementInfo,
  ElementType,
  ElementText,
  CurrentTimeInfo,
  ActiveIndicator,
  AutoJumpHint,
  TypeBadge,
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
  AssetsModalContent,
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
} from '../../components/json-test/JsonTestStyles';

const JSONTest: React.FC = () => {
  const [jsonInput, setJsonInput] = useState(DEFAULT_JSON);

  const [previewReady, setPreviewReady] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentState, setCurrentState] = useState<PreviewState>();
  
  // 🔧 中間處理層：分離使用者輸入與 SDK 實際使用的 JSON
  const [processedSource, setProcessedSource] = useState<any>(null);  // SDK 實際使用的
  const [urlMapping, setUrlMapping] = useState<Map<string, string>>(new Map());  // URL 映射記錄
  
  // 🎨 URL 狀態追蹤（用於視覺高亮）
  const [urlStatus, setUrlStatus] = useState<Map<string, UrlStatus>>(new Map());
  
  // 🎨 元素高亮範圍
  const [autoHighlightRanges, setAutoHighlightRanges] = useState<CurrentElementRange[]>([]);  // 自動播放（淺灰）
  const [clickedHighlightRange, setClickedHighlightRange] = useState<CurrentElementRange | null>(null);  // 點擊選中（淡藍）
  const [timelineElements, setTimelineElements] = useState<TimelineElement[]>([]);
  
  // 🔧 同步到 ref（讓 onTimeChange 能取得最新值）
  React.useEffect(() => {
    timelineElementsRef.current = timelineElements;
  }, [timelineElements]);
  
  React.useEffect(() => {
    jsonInputRef.current = jsonInput;
  }, [jsonInput]);
  const [currentEditingElement, setCurrentEditingElement] = useState<number>(-1);  // 點擊選中（單個）
  const [activeElementIndices, setActiveElementIndices] = useState<number[]>([]);  // 播放中的活躍元素（多個）
  const previewRef = useRef<Preview>();
  const previewContainerRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const cursorTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const timelineElementsRef = useRef<TimelineElement[]>([]);
  const jsonInputRef = useRef<string>('');

  // 🎯 使用 Asset Manager Hook
  const {
    showAssetsModal,
    setShowAssetsModal,
    selectedAssetType,
    setSelectedAssetType,
    filteredAssets,
    copyAssetUrl,
    loadAssetToJson,
  } = useAssetManager({ setJsonInput, setError, error });

  // 🎯 使用 Import/Export Hook
  const {
    showImportModal,
    setShowImportModal,
    importJsonInput,
    setImportJsonInput,
    copyApiRequest,
    openImportModal,
    handleImportApiRequest,
  } = useImportExport({ jsonInput, setJsonInput, setError });

  // 🔄 處理時間變化（獨立函數，可訪問最新 state）
  const handleTimeChange = useCallback((time: number) => {
    const elements = timelineElements;
    
    if (!elements || elements.length === 0) return;
    
    // 找到所有活躍元素（排除 composition，只要具體的媒體元素）
    const activeElements = elements
      .map((el, index) => ({ el, index }))
      .filter(({ el }) => {
        // 檢查時間範圍
        const inTimeRange = time >= el.time && time < (el.time + el.duration);
        // 排除 composition（只要子元素）
        const isNotComposition = el.type !== 'composition';
        
        return inTimeRange && isNotComposition;
      });
    
    if (activeElements.length > 0) {
      // 收集所有活躍元素的範圍（使用 path 精確定位）
      const ranges: CurrentElementRange[] = [];
      
      activeElements.forEach(({ el, index }) => {
        // 🔧 必須使用 path 來精確定位（因為有 composition 嵌套）
        if (el.path) {
          const range = findElementRangeByPath(jsonInput, el.path);
          
          if (range) {
            ranges.push(range);
          } else {
            console.warn(`⚠️ 找不到 path 範圍: ${el.path} (元素: ${el.name})`);
          }
        } else {
          console.warn(`⚠️ 元素缺少 path: ${el.name} (type: ${el.type})`);
        }
      });
      
      // 設定所有範圍為自動高亮
      setAutoHighlightRanges(ranges);
      
      // 🔧 設定所有活躍元素的索引（用於時間軸多選背景）
      const indices = activeElements.map(a => a.index);
      setActiveElementIndices(indices);
    } else {
      setAutoHighlightRanges([]);
      setActiveElementIndices([]);
    }
  }, [timelineElements, jsonInput]);
  
  // 🔧 當 handleTimeChange 更新時，重新綁定到 preview
  React.useEffect(() => {
    if (previewRef.current && previewReady) {
      previewRef.current.onTimeChange = handleTimeChange;
    }
  }, [handleTimeChange, previewReady]);

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
          
          // 🔧 設定影片快取規則（允許所有外部影片完整快取）
          console.log('🔧 設定影片快取規則...');
          try {
            await preview.setCacheBypassRules([/.*/]);  // 允許所有 URL
            console.log('✅ 影片快取規則設定完成');
          } catch (cacheRuleError) {
            console.warn('⚠️ 快取規則設定失敗:', cacheRuleError);
          }
          
          // 檢查是否有template ID環境變數，如果有就先載入template作為基礎
          if (process.env.NEXT_PUBLIC_TEMPLATE_ID) {
            console.log('先載入基礎模板...');
            try {
              await preview.loadTemplate(process.env.NEXT_PUBLIC_TEMPLATE_ID);
              console.log('基礎模板載入完成');
            } catch (templateError) {
              console.warn('基礎模板載入失敗，繼續使用 JSON 直接輸入:', templateError);
              // 不拋出錯誤，允許繼續進行 JSON 直接輸入
            }
          }
          
          // 然後設置我們的JSON
          const source = JSON.parse(jsonInput);
          console.log('原始JSON source:', source);
          
          // 🔧 使用 cacheAsset 預先快取所有外部素材
          console.log('🔧 [初始化] 開始快取外部素材...');
          const cacheResult = await cacheExternalAssets(
            preview, 
            source,
            (url, status) => {
              // 更新 URL 狀態（用於視覺高亮）
              setUrlStatus(prev => new Map(prev).set(url, status));
            }
          );
          console.log(`✅ [初始化] 快取完成 - 成功: ${cacheResult.success.length}, 失敗: ${cacheResult.failed.length}`);
          
          // 🔧 中間處理層：創建處理過的 JSON
          // 保持使用者輸入不變，但 SDK 使用處理過的版本
          let processedSource = source;
          
          // 如果有 URL 映射（GIF 替換等），應用映射
          if (cacheResult.urlMapping.size > 0) {
            console.log('🔧 [初始化] 應用 URL 映射...');
            processedSource = replaceGifUrlsInJson(source, cacheResult.urlMapping);
            setUrlMapping(cacheResult.urlMapping);  // 儲存映射記錄
          }
          
          // 儲存處理過的 JSON
          setProcessedSource(processedSource);
          
          // 轉換為 snake_case（SDK 需要）
          const convertedSource = convertToSnakeCase(processedSource);
          console.log('[中間層] 處理後的 JSON:', convertedSource);
          
          await preview.setSource(convertedSource);
          console.log('✅ JSON設置完成');
          
          // 解析時間軸元素（使用原始 source，顯示給使用者看）
          const elements = parseTimelineElements(source);
          setTimelineElements(elements);
          
          setPreviewReady(true);
          setError(null);
          setIsLoading(false);
        } catch (err) {
          console.error('初始化失敗:', err);
          console.error('錯誤類型:', typeof err);
          console.error('錯誤訊息:', err instanceof Error ? err.message : String(err));
          if (err instanceof Error && err.stack) {
            console.error('錯誤堆疊:', err.stack);
          }
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

      // 監聽狀態變更
      preview.onStateChange = (state) => {
        console.log('狀態變更:', state);
        setCurrentState(state);
        if (state) {
          console.log('預覽尺寸:', state.width, 'x', state.height);
          console.log('預覽持續時間:', state.duration);
        }
      };
      
      // 🔄 監聽時間變化（直接調用外部函數）
      preview.onTimeChange = handleTimeChange;



      previewRef.current = preview;
    } catch (err) {
      console.error('預覽初始化失敗:', err);
      setError(`預覽初始化失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
    }
  }, [jsonInput, handleTimeChange, parseTimelineElements]);

  // JSON改變時的即時更新（手動觸發）
  React.useEffect(() => {
    // 只在預覽準備好且不是初始載入時更新
    if (previewReady && previewRef.current) {
      const timeoutId = setTimeout(async () => {
        try {
          setError(null); // 清除之前的錯誤
          const source = JSON.parse(jsonInput);
          
          // 🔧 使用 cacheAsset 預先快取所有外部素材
          console.log('🔧 [即時更新] 開始快取外部素材...');
          const cacheResult = await cacheExternalAssets(
            previewRef.current!,
            source,
            (url, status) => {
              // 更新 URL 狀態
              setUrlStatus(prev => new Map(prev).set(url, status));
            }
          );
          console.log(`✅ [即時更新] 快取完成 - 成功: ${cacheResult.success.length}, 失敗: ${cacheResult.failed.length}`);
          
          // 🔧 中間處理層：創建處理過的 JSON
          let processedSource = source;
          
          if (cacheResult.urlMapping.size > 0) {
            console.log('🔧 [即時更新] 應用 URL 映射...');
            processedSource = replaceGifUrlsInJson(source, cacheResult.urlMapping);
            setUrlMapping(cacheResult.urlMapping);
          }
          
          setProcessedSource(processedSource);
          
          // 解析時間軸元素（使用原始 source）
          const elements = parseTimelineElements(source);
          setTimelineElements(elements);
          
          // 轉換為 snake_case（使用處理過的 source）
          const convertedSource = convertToSnakeCase(processedSource);
          console.log('[中間層] 即時更新 - 處理後的 JSON');
          
          await previewRef.current!.setSource(convertedSource);
          
          console.log('JSON更新成功，時間軸元素:', elements.length);
        } catch (err) {
          console.error('JSON更新失敗:', err);
          // 只有在真正的語法錯誤時才顯示錯誤，避免防抖期間的誤報
          if (err instanceof SyntaxError) {
            setError(`JSON語法錯誤: ${err.message}`);
          }
        }
      }, 800); // 增加防抖時間以處理長JSON
      return () => clearTimeout(timeoutId);
    }
  }, [jsonInput, parseTimelineElements, previewReady]); // 加入 previewReady 依賴

  // 跳轉到特定時間
  const seekToTime = useCallback(async (time: number, elementIndex?: number, elementPath?: string) => {
    if (!previewRef.current || !previewReady) return;
    
    try {
      await previewRef.current.setTime(time);
      console.log(`跳轉到時間: ${time}秒`);
      
      // 如果提供了元素資訊，同步更新高亮狀態
      if (elementIndex !== undefined && elementIndex !== currentEditingElement) {
        setCurrentEditingElement(elementIndex);
        console.log(`🎯 同步更新高亮元素索引: ${elementIndex}, path: ${elementPath}`);
        
        // 🎨 更新 JSON 中的元素高亮範圍（點擊 → 淡藍色）
        // ⚠️ 必須使用 path，因為有 composition 嵌套，index 會對不上
        if (elementPath) {
          const range = findElementRangeByPath(jsonInput, elementPath);
          
          if (range) {
            setClickedHighlightRange(range);
            console.log(`🎨 點擊高亮: ${range.start}-${range.end}, path: ${elementPath}`);
          } else {
            console.warn(`⚠️ 無法找到 path 的範圍: ${elementPath}`);
            setClickedHighlightRange(null);
          }
        } else {
          console.warn(`⚠️ 缺少 path，無法精確高亮`);
          setClickedHighlightRange(null);
        }
      }
    } catch (err) {
      console.error('跳轉時間失敗:', err);
    }
  }, [previewReady, currentEditingElement, jsonInput]);

  // 處理光標位置變化（帶防抖）
  const handleCursorChange = useCallback(() => {
    if (!textareaRef.current || !previewReady) return;
    
    // 清理之前的超時
    if (cursorTimeoutRef.current) {
      clearTimeout(cursorTimeoutRef.current);
    }
    
    // 防抖處理
    cursorTimeoutRef.current = setTimeout(() => {
      if (!textareaRef.current) return;
      
      const cursorPosition = textareaRef.current.selectionStart;
                        const elementIndex = detectCurrentElement(cursorPosition, jsonInput, timelineElements);
      
      console.log(`光標位置: ${cursorPosition}, 檢測元素索引: ${elementIndex}, 當前編輯元素: ${currentEditingElement}`);
      console.log(`時間軸元素總數: ${timelineElements?.length || 0}`);
      
      // 特殊調試：列出前3個時間軸元素
      if (timelineElements && timelineElements.length > 0) {
        console.log(`前3個時間軸元素:`, timelineElements.slice(0, 3).map((el, i) => 
          `${i}: ${el.name} (${el.type}, ${el.time}s, source: ${el.source})`
        ));
      }
      
      if (elementIndex !== -1 && elementIndex !== currentEditingElement) {
        setCurrentEditingElement(elementIndex);
        
        // 自動跳轉到該元素的時間
        if (timelineElements && timelineElements[elementIndex]) {
          const element = timelineElements[elementIndex];
          console.log(`🎯 準備跳轉: 索引=${elementIndex}, 元素="${element.name}", 時間=${element.time}s`);
          console.log(`🎯 目標時間詳情: 類型=${element.type}, 源=${element.source}`);
          
          // 添加額外的驗證，確保時間有效
          if (element.time >= 0) {
            console.log(`▶️ 執行跳轉到 ${element.time}s`);
            seekToTime(element.time, elementIndex, element.path);
          } else {
            console.log(`⚠️ 元素時間無效: ${element.time}, 跳過跳轉`);
          }
        } else {
          console.log(`⚠️ 時間軸元素不存在: 索引 ${elementIndex}, 總數: ${timelineElements?.length || 0}`);
          if (timelineElements && timelineElements.length > 0) {
            console.log(`可用元素:`, timelineElements.map((el, i) => `${i}: ${el.name} (${el.time}s)`));
          }
        }
      }
      
      cursorTimeoutRef.current = null;
    }, 200); // 減少防抖時間提高響應性
  }, [jsonInput, currentEditingElement, timelineElements, seekToTime, previewReady]);

  // 清理函數
  React.useEffect(() => {
    return () => {
      if (cursorTimeoutRef.current) {
        clearTimeout(cursorTimeoutRef.current);
      }
    };
  }, []);

  // 載入示例 JSON
  const loadExample = (exampleJson: string) => {
    setJsonInput(exampleJson);
  };

  // 創建視頻
  const createVideo = async () => {
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
  };

  // 使用 import 的示例
  const examples = JSON_EXAMPLES;

  return (
    <div>
      <Head>
        <title>JSON 直接導入編輯器</title>
        <link rel='icon' href='/favicon.ico' />
      </Head>

      <Container>
        <Header>
          <BackLink>
            <Link href="/tools">← 返回工具集</Link>
          </BackLink>
          <Title>JSON 直接導入編輯器</Title>
          <CreateButton onClick={createVideo} disabled={!previewReady || isLoading}>
            {isLoading ? '生成中...' : '創建視頻'}
          </CreateButton>
        </Header>

        <MainContent>
          <LeftPanel>
            <SectionTitle>JSON 腳本</SectionTitle>
            <ButtonGroup>
              {examples.map((example, index) => (
                <ExampleButton
                  key={index}
                  onClick={() => loadExample(example.json)}
                >
                  {example.name}
                </ExampleButton>
              ))}
              <CopyApiButton
                data-copy-api-button
                onClick={copyApiRequest}
              >
                複製 api 請求
              </CopyApiButton>
              <ImportApiButton
                onClick={openImportModal}
              >
                匯入 JSON 請求
              </ImportApiButton>
              
            </ButtonGroup>
            
            <EditorContainer>
              {/* 層1: 自動播放高亮（最底層，淺灰）- 多個元素 */}
              {autoHighlightRanges.length > 0 && (
                <AutoHighlightOverlay
                  dangerouslySetInnerHTML={{
                    __html: generateMultipleElementHighlights(jsonInput, autoHighlightRanges)
                  }}
                />
              )}
              
              {/* 層2: 點擊選中高亮（中下層，淡藍）- 單個元素 */}
              {clickedHighlightRange && (
                <ClickedHighlightOverlay
                  dangerouslySetInnerHTML={{
                    __html: generateMultipleElementHighlights(jsonInput, [clickedHighlightRange])
                  }}
                />
              )}
              
              {/* 層3: URL 狀態高亮（中上層，URL 顏色）*/}
              <UrlHighlightOverlay
                dangerouslySetInnerHTML={{
                  __html: generateHighlightedText(jsonInput, urlStatus)
                }}
              />
              
              {/* 層3: Textarea（最上層，透明背景）*/}
            <JSONTextarea
              ref={textareaRef}
              value={jsonInput}
              onChange={(e) => setJsonInput(e.target.value)}
              onClick={handleCursorChange}
              onKeyUp={handleCursorChange}
              onFocus={handleCursorChange}
              onSelect={handleCursorChange}
                onScroll={(e) => {
                  // 同步滾動到所有 overlay
                  const container = e.currentTarget.parentElement;
                  if (container) {
                    const overlays = container.querySelectorAll('[data-overlay]');
                    overlays.forEach(overlay => {
                      (overlay as HTMLElement).scrollTop = e.currentTarget.scrollTop;
                      (overlay as HTMLElement).scrollLeft = e.currentTarget.scrollLeft;
                    });
                  }
                }}
              placeholder="在此輸入你的 JSON..."
            />
            </EditorContainer>
          </LeftPanel>

          <RightPanel>
            <SectionTitle>視頻預覽</SectionTitle>
            
            {error && <ErrorMessage>{error}</ErrorMessage>}
            
            <PreviewContainer
              ref={(element) => {
                if (element && element !== previewContainerRef.current) {
                  console.log('預覽容器元素:', element);
                  previewContainerRef.current = element;
                  setUpPreview(element);
                }
              }}
            />
            
            {isLoading && <LoadingIndicator>載入中...</LoadingIndicator>}
            
            {/* 時間軸控制面板 */}
            {previewReady && (
              <TimelinePanelComponent
                timelineElements={timelineElements}
                currentState={currentState}
                activeElementIndices={activeElementIndices}
                currentEditingElement={currentEditingElement}
                onSeekToTime={seekToTime}
              />
            )}
          </RightPanel>
        </MainContent>

        {/* 素材列表彈窗 */}
        <AssetsModalComponent
          show={showAssetsModal}
          selectedType={selectedAssetType}
          filteredAssets={filteredAssets}
          onClose={() => setShowAssetsModal(false)}
          onTypeChange={setSelectedAssetType}
          onCopyAsset={copyAssetUrl}
          onLoadAsset={loadAssetToJson}
        />

        {/* 匯入 JSON 請求彈窗 */}
        <ImportModalComponent
          show={showImportModal}
          jsonInput={importJsonInput}
          onClose={() => setShowImportModal(false)}
          onImport={handleImportApiRequest}
          onInputChange={setImportJsonInput}
        />
      </Container>
    </div>
  );
};

export default JSONTest; 