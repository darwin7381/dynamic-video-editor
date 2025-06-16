import React, { useRef, useState, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import styled from 'styled-components';
import { Preview, PreviewState } from '@creatomate/preview';

const JSONTest: React.FC = () => {
  const [jsonInput, setJsonInput] = useState(`{
  "output_format": "mp4",
  "width": 1280,
  "height": 720,
  "duration": "6s",
  "elements": [
    {
      "type": "text",
      "text": "第一段文字",
      "font_family": "Arial",
      "font_size": "48px",
      "fill_color": "#ffffff",
      "x": "50%",
      "y": "40%",
      "x_alignment": "50%",
      "y_alignment": "50%",
      "time": "0s",
      "duration": "2s"
    },
    {
      "type": "text",
      "text": "第二段文字",
      "font_family": "Arial",
      "font_size": "48px",
      "fill_color": "#ffff00",
      "x": "50%",
      "y": "60%",
      "x_alignment": "50%",
      "y_alignment": "50%",
      "time": "2s",
      "duration": "2s"
    },
    {
      "type": "text",
      "text": "第三段文字",
      "font_family": "Arial",
      "font_size": "48px",
      "fill_color": "#ff6600",
      "x": "50%",
      "y": "50%",
      "x_alignment": "50%",
      "y_alignment": "50%",
      "time": "4s",
      "duration": "2s"
    }
  ]
}`);

  const [previewReady, setPreviewReady] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentState, setCurrentState] = useState<PreviewState>();
  const [timelineElements, setTimelineElements] = useState<Array<{
    id: string;
    time: number;
    duration: number;
    type: string;
    text?: string;
  }>>([]);
  const [currentEditingElement, setCurrentEditingElement] = useState<number>(-1);
  const previewRef = useRef<Preview>();
  const previewContainerRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 解析時間軸元素
  const parseTimelineElements = useCallback((source: any) => {
    if (!source.elements || !Array.isArray(source.elements)) return [];

    const elements = source.elements
      .map((element: any, index: number) => {
        const timeStr = element.time || element.start_time || '0s';
        const durationStr = element.duration || '3s';
        
        // 解析時間字符串轉為秒數
        const parseTime = (timeStr: string): number => {
          if (typeof timeStr === 'number') return timeStr;
          const match = String(timeStr).match(/(\d+(\.\d+)?)\s*s?/);
          return match ? parseFloat(match[1]) : 0;
        };

        const time = parseTime(timeStr);
        const duration = parseTime(durationStr);

        return {
          id: `element-${index}`,
          time,
          duration,
          type: element.type || 'unknown',
          text: element.text || element.source?.split('/').pop() || `${element.type} ${index + 1}`
        };
      })
      .sort((a: any, b: any) => a.time - b.time); // 按時間排序

    return elements;
  }, []);

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
          
          // 檢查是否有template ID環境變數，如果有就先載入template作為基礎
          if (process.env.NEXT_PUBLIC_TEMPLATE_ID) {
            console.log('先載入基礎模板...');
            await preview.loadTemplate(process.env.NEXT_PUBLIC_TEMPLATE_ID);
            console.log('基礎模板載入完成');
          }
          
          // 然後設置我們的JSON
          const source = JSON.parse(jsonInput);
          console.log('設置JSON source:', source);
          await preview.setSource(source);
          console.log('JSON設置完成');
          
          // 解析時間軸元素
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



      previewRef.current = preview;
    } catch (err) {
      console.error('預覽初始化失敗:', err);
      setError(`預覽初始化失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
    }
  }, [jsonInput]);

  // 加載 JSON
  const loadJSON = useCallback(async () => {
    if (!previewRef.current || !previewReady) {
      setError('預覽未準備就緒');
      return;
    }

    try {
      setError(null);
      setIsLoading(true);
      
      console.log('開始解析JSON...', jsonInput.substring(0, 200));
      
      const source = JSON.parse(jsonInput);
      console.log('JSON解析成功:', source);
      
      // 基本驗證
      if (!source.output_format) {
        throw new Error('缺少必要字段：output_format');
      }
      
      if (!source.elements || !Array.isArray(source.elements)) {
        throw new Error('缺少或無效的 elements 陣列');
      }
      
      console.log('開始載入到預覽...');
      await previewRef.current.setSource(source);
      console.log('預覽載入成功');
      
    } catch (err) {
      console.error('載入失敗:', err);
      if (err instanceof SyntaxError) {
        setError(`JSON 語法錯誤: ${err.message}`);
      } else {
        setError(`載入失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
      }
    } finally {
      setIsLoading(false);
    }
  }, [jsonInput, previewReady]);

  // JSON改變時的即時更新（手動觸發）
  React.useEffect(() => {
    // 只在預覽準備好且不是初始載入時更新
    if (previewReady && previewRef.current) {
      const timeoutId = setTimeout(async () => {
        try {
          const source = JSON.parse(jsonInput);
          await previewRef.current!.setSource(source);
          
          // 解析並設置時間軸元素
          const elements = parseTimelineElements(source);
          setTimelineElements(elements);
        } catch (err) {
          console.error('JSON更新失敗:', err);
          setError(`JSON更新失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
        }
      }, 500); // 防抖
      return () => clearTimeout(timeoutId);
    }
  }, [jsonInput, parseTimelineElements]); // 只依賴jsonInput變化

  // 跳轉到特定時間
  const seekToTime = useCallback(async (time: number) => {
    if (!previewRef.current || !previewReady) return;
    
    try {
      await previewRef.current.setTime(time);
      console.log(`跳轉到時間: ${time}秒`);
    } catch (err) {
      console.error('跳轉時間失敗:', err);
    }
  }, [previewReady]);

  // 檢測當前編輯的元素
  const detectCurrentElement = useCallback((cursorPosition: number, jsonText: string) => {
    try {
      const source = JSON.parse(jsonText);
      if (!source.elements || !Array.isArray(source.elements)) return -1;

      // 找到每個元素在JSON字符串中的位置範圍
      const elementsText = jsonText.substring(
        jsonText.indexOf(`"elements"`),
        jsonText.lastIndexOf(']') + 1
      );
      
      let elementStartIndex = jsonText.indexOf(`"elements"`) + jsonText.substring(jsonText.indexOf(`"elements"`)).indexOf('[') + 1;
      let braceCount = 0;
      let currentElementIndex = 0;
      let inString = false;
      let escapeNext = false;

      for (let i = elementStartIndex; i < jsonText.length && i < cursorPosition; i++) {
        const char = jsonText[i];
        
        if (escapeNext) {
          escapeNext = false;
          continue;
        }
        
        if (char === '\\') {
          escapeNext = true;
          continue;
        }
        
        if (char === '"') {
          inString = !inString;
          continue;
        }
        
        if (!inString) {
          if (char === '{') {
            braceCount++;
          } else if (char === '}') {
            braceCount--;
            if (braceCount === 0) {
              // 完成一個元素
              currentElementIndex++;
            }
          }
        }
      }

      // 確保索引有效
      if (currentElementIndex >= 0 && currentElementIndex < source.elements.length) {
        return currentElementIndex;
      }
      
      return -1;
    } catch (err) {
      return -1;
    }
  }, []);

  // 處理光標位置變化（帶防抖）
  const handleCursorChange = useCallback(() => {
    if (!textareaRef.current || !previewReady) return;
    
    // 防抖處理
    setTimeout(() => {
      if (!textareaRef.current) return;
      
      const cursorPosition = textareaRef.current.selectionStart;
      const elementIndex = detectCurrentElement(cursorPosition, jsonInput);
      
      if (elementIndex !== -1 && elementIndex !== currentEditingElement) {
        setCurrentEditingElement(elementIndex);
        
        // 自動跳轉到該元素的時間
        if (timelineElements[elementIndex]) {
          const element = timelineElements[elementIndex];
          console.log(`🎯 自動跳轉到元素 ${elementIndex}: ${element.text} (${element.time}s)`);
          seekToTime(element.time);
        }
      }
    }, 300); // 300ms 防抖
  }, [jsonInput, currentEditingElement, timelineElements, detectCurrentElement, seekToTime, previewReady]);

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

  const examples = [
    {
      name: '載入示例',
      json: `{
  "output_format": "mp4",
  "duration": "3 s",
  "width": 1920,
  "height": 1080,
  "elements": [
    {
      "type": "text",
      "track": 1,
      "time": "0 s",
      "duration": "1 s",
      "fill_color": "#ffffff",
      "text": "This text is only visible for one second",
      "font_family": "Open Sans"
    }
  ]
}`
    },
    {
      name: '從文件載入',
      json: `{
  "output_format": "mp4",
  "width": 1280,
  "height": 720,
  "elements": [
    {
      "type": "image",
      "track": 1,
      "duration": "3 s",
      "source": "https://creatomate-static.s3.amazonaws.com/demo/image1.jpg"
    },
    {
      "type": "text",
      "text": "Hello World",
      "font_family": "Arial",
      "font_size": "5 vh",
      "fill_color": "#ffffff",
      "x": "50%",
      "y": "50%",
      "x_alignment": "50%",
      "y_alignment": "50%"
    }
  ]
}`
    },
    {
      name: '載入新的JSON',
      json: `{
  "output_format": "mp4",
  "width": 1920,
  "height": 1080,
  "duration": "5 s",
  "elements": [
    {
      "type": "video",
      "track": 1,
      "source": "https://creatomate-static.s3.amazonaws.com/demo/video1.mp4"
    },
    {
      "type": "text",
      "text": "視頻疊加層",
      "font_family": "Arial",
      "font_size": "8 vh",
      "fill_color": "#ff0000",
      "x": "50%",
      "y": "20%",
      "x_alignment": "50%",
      "y_alignment": "50%"
    }
  ]
}`
    }
  ];

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
            </ButtonGroup>
            
            <JSONTextarea
              ref={textareaRef}
              value={jsonInput}
              onChange={(e) => setJsonInput(e.target.value)}
              onClick={handleCursorChange}
              onKeyUp={handleCursorChange}
              onFocus={handleCursorChange}
              onSelect={handleCursorChange}
              placeholder="在此輸入你的 JSON..."
            />
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
            {previewReady && timelineElements.length > 0 && (
              <TimelinePanel>
                <TimelinePanelTitle>
                  時間軸控制 
                  <AutoJumpHint>💡 編輯JSON時會自動跳轉</AutoJumpHint>
                </TimelinePanelTitle>
                <TimelineElementsContainer>
                  {timelineElements.map((element, index) => (
                    <TimelineElement
                      key={element.id}
                      $isActive={index === currentEditingElement}
                      onClick={() => seekToTime(element.time)}
                    >
                      <ElementTime>{element.time}s</ElementTime>
                      <ElementInfo>
                        <ElementType>{element.type}</ElementType>
                        <ElementText>{element.text}</ElementText>
                      </ElementInfo>
                      {index === currentEditingElement && <ActiveIndicator>●</ActiveIndicator>}
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
            )}
          </RightPanel>
        </MainContent>
      </Container>
    </div>
  );
};

export default JSONTest;

const Container = styled.div`
  min-height: 100vh;
  background: #f5f5f5;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
`;

const BackLink = styled.div`
  a {
    color: #2196f3;
    text-decoration: none;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const Title = styled.h1`
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

const CreateButton = styled.button`
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

const MainContent = styled.div`
  display: flex;
  height: calc(100vh - 80px);
`;

const LeftPanel = styled.div`
  flex: 1;
  padding: 20px;
  background: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
`;

const RightPanel = styled.div`
  flex: 1;
  padding: 20px;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
`;

const SectionTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
`;

const ExampleButton = styled.button`
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

const JSONTextarea = styled.textarea`
  flex: 1;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  outline: none;
  
  &:focus {
    border-color: #2196f3;
  }
`;

const PreviewContainer = styled.div`
  flex: 1;
  background: #000;
  border-radius: 8px;
  position: relative;
  min-height: 400px;
`;

const ErrorMessage = styled.div`
  color: #f44336;
  background: #ffebee;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
`;

const LoadingIndicator = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-size: 18px;
  font-weight: 600;
`;

const TimelinePanel = styled.div`
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
`;

const TimelinePanelTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: #333;
`;

const TimelineElementsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
`;

const TimelineElement = styled.div<{ $isActive?: boolean }>`
  display: flex;
  align-items: center;
  padding: 10px;
  background: ${props => props.$isActive ? '#e3f2fd' : '#f8f9fa'};
  border: ${props => props.$isActive ? '2px solid #2196f3' : '1px solid transparent'};
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  
  &:hover {
    background: ${props => props.$isActive ? '#bbdefb' : '#e9ecef'};
  }
`;

const ElementTime = styled.div`
  min-width: 50px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #2196f3;
`;

const ElementInfo = styled.div`
  margin-left: 15px;
  display: flex;
  flex-direction: column;
  flex: 1;
`;

const ElementType = styled.div`
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  font-weight: 500;
`;

const ElementText = styled.div`
  font-size: 14px;
  color: #333;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const CurrentTimeInfo = styled.div`
  font-size: 14px;
  color: #666;
  text-align: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
`;

const ActiveIndicator = styled.div`
  position: absolute;
  right: 10px;
  color: #2196f3;
  font-size: 16px;
  font-weight: bold;
  animation: pulse 1.5s infinite;
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const AutoJumpHint = styled.span`
  font-size: 12px;
  color: #666;
  font-weight: normal;
  margin-left: 10px;
`; 