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
    name: string;
    text: string;
    source: string;
    path: string;
  }>>([]);
  const [currentEditingElement, setCurrentEditingElement] = useState<number>(-1);
  const previewRef = useRef<Preview>();
  const previewContainerRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const cursorTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // 解析時間軸元素（支援composition嵌套結構）
  const parseTimelineElements = useCallback((source: any) => {
    try {
      if (!source.elements || !Array.isArray(source.elements)) {
        console.log('⚠️ 無效的elements陣列:', source.elements);
        return [];
      }

      // 解析時間字符串轉為秒數
      const parseTime = (timeStr: any): number => {
        if (typeof timeStr === 'number') return timeStr;
        if (timeStr === 'end') return 0; // 特殊值，需要後續處理
        const match = String(timeStr || '0').match(/(\d+(\.\d+)?)\s*s?/);
        return match ? parseFloat(match[1]) : 0;
      };

      // 計算元素的估計持續時間
      const estimateDuration = (element: any): number => {
        if (element.duration !== undefined) {
          return parseTime(element.duration);
        }
        
        // 根據元素類型估算默認持續時間
        switch (element.type) {
          case 'video':
          case 'audio':
            return 8; // 視頻/音頻默認8秒
          case 'image':
            return 3; // 圖片默認3秒
          case 'text':
            return 4; // 文字默認4秒
          case 'composition':
            return 6; // 組合默認6秒
          case 'shape':
            return 5; // 形狀默認5秒
          default:
            return 3; // 其他默認3秒
        }
      };

            // 遞歸解析元素（處理composition嵌套和自動時間軸）
      const parseElementsRecursively = (
        elements: any[], 
        parentTime: number = 0, 
        parentPath: string = ''
      ): any[] => {
        const results: any[] = [];

        // 按track分組元素
        const trackGroups: { [track: number]: any[] } = {};
        elements.forEach((element, index) => {
          const track = element.track || 1;
          if (!trackGroups[track]) trackGroups[track] = [];
          trackGroups[track].push({ ...element, originalIndex: index });
        });

        // 為每個track計算自動時間軸
        Object.keys(trackGroups).forEach(trackStr => {
          const track = parseInt(trackStr);
          const trackElements = trackGroups[track];
          let currentTrackTime = 0; // 當前track的時間軸位置

          console.log(`🎬 處理Track ${track}: ${trackElements.length} 個元素`);

          trackElements.forEach((element: any, trackIndex: number) => {
            const elementPath = parentPath ? `${parentPath}.${element.originalIndex}` : `${element.originalIndex}`;
            
            // 決定元素的開始時間
            let elementTime: number;
            if (element.time !== undefined) {
              // 有明確時間，使用指定時間
              elementTime = parseTime(element.time);
              currentTrackTime = Math.max(currentTrackTime, elementTime);
            } else {
              // 沒有明確時間，使用當前track時間
              elementTime = currentTrackTime;
            }

            // 如果是composition類型，先處理子元素以計算準確的持續時間
            let compositionChildElements: any[] = [];
            if (element.type === 'composition' && element.elements && Array.isArray(element.elements)) {
              // 為了計算持續時間，先遞歸解析子元素（使用臨時時間偏移0）
              compositionChildElements = parseElementsRecursively(
                element.elements, 
                0, // 臨時使用0來計算相對時間
                elementPath
              );
            }

            // 計算持續時間，對於composition使用子元素的實際時間軸
            let elementDuration: number;
            if (element.type === 'composition' && compositionChildElements.length > 0 && !element.duration) {
              // 基於解析後的子元素計算composition的實際持續時間
              const maxChildEndTime = Math.max(...compositionChildElements.map(child => 
                child.time + child.duration
              ));
              elementDuration = maxChildEndTime > 0 ? maxChildEndTime : estimateDuration(element);
              console.log(`📏 Composition ${element.name} 實際持續時間: ${elementDuration.toFixed(1)}s (基於子元素計算)`);
            } else {
              elementDuration = estimateDuration(element);
            }

            // 處理transition重疊效果
            if (element.transition && trackIndex > 0) {
              const transitionDuration = parseTime(element.transition.duration || '1');
              // transition會讓當前元素提前開始，與前一個元素重疊
              elementTime = Math.max(0, elementTime - transitionDuration);
              console.log(`🔄 處理transition: ${element.name || element.type}, 提前 ${transitionDuration}s 開始`);
            }

            const absoluteTime = parentTime + elementTime;

            // 創建當前元素的基本信息
            const baseElement = {
              id: element.id || `element-${elementPath}`,
              time: absoluteTime,
              duration: elementDuration,
              type: element.type || 'unknown',
              name: element.name || `${element.type} ${element.originalIndex + 1}`,
              text: element.text || (element.source ? element.source.split('/').pop()?.replace(/\?.*$/, '') : '') || '',
              source: element.source || '',
              path: elementPath,
              track: track
            };

            results.push(baseElement);

            // 更新track時間軸位置（考慮實際結束時間）
            const elementEndTime = elementTime + elementDuration;
            currentTrackTime = Math.max(currentTrackTime, elementEndTime);
            
            console.log(`⏰ 元素時間計算: ${baseElement.name} - 開始:${elementTime.toFixed(1)}s, 持續:${elementDuration.toFixed(1)}s, 絕對時間:${absoluteTime.toFixed(1)}s`);

            // 添加composition的子元素（使用正確的時間偏移）
            if (compositionChildElements.length > 0) {
              console.log(`📁 添加composition子元素: ${element.name || `composition-${element.originalIndex}`}, 時間偏移: ${absoluteTime}s`);
              const adjustedChildElements = compositionChildElements.map(child => ({
                ...child,
                time: child.time + absoluteTime // 調整為正確的絕對時間
              }));
              results.push(...adjustedChildElements);
            }
          });
        });

        return results;
      };

      // 開始遞歸解析
      const allElements = parseElementsRecursively(source.elements);
      
      // 按時間排序並過濾重複
      const sortedElements = allElements
        .sort((a: any, b: any) => {
          // 首先按時間排序
          if (a.time !== b.time) return a.time - b.time;
          // 時間相同時，按路徑深度排序（父元素在前）
          return a.path.split('.').length - b.path.split('.').length;
        });

             console.log(`✅ 解析完成 ${sortedElements.length} 個時間軸元素 (包含嵌套)`);
       
       // 打印時間軸總覽
       console.log('📊 時間軸總覽:');
       sortedElements.slice(0, 10).forEach((el, i) => {
         const endTime = el.time + el.duration;
         console.log(`  ${i}: ${el.time.toFixed(1)}s-${endTime.toFixed(1)}s | ${el.type.toUpperCase()} | ${el.name}`);
       });
       
       if (sortedElements.length > 10) {
         console.log(`  ... 還有 ${sortedElements.length - 10} 個元素`);
       }
       
       const totalDuration = Math.max(...sortedElements.map(el => el.time + el.duration));
       console.log(`🎬 總視頻時長: ${totalDuration.toFixed(1)}秒`);
      
      return sortedElements;
    } catch (err) {
      console.error('解析時間軸元素失敗:', err);
      return [];
    }
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
          
          // 檢查並轉換駝峰命名為蛇形命名（Creatomate Preview SDK 需要）
          const convertToSnakeCase = (obj: any): any => {
            if (Array.isArray(obj)) {
              return obj.map(item => convertToSnakeCase(item));
            } else if (obj !== null && typeof obj === 'object') {
              const newObj: any = {};
              for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                  // 轉換 camelCase 為 snake_case
                  const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
                  newObj[snakeKey] = convertToSnakeCase(obj[key]);
                }
              }
              return newObj;
            }
            return obj;
          };
          
          // 轉換格式以供 Preview SDK 使用
          const convertedSource = convertToSnakeCase(source);
          console.log('轉換後的JSON source:', convertedSource);
          
          await preview.setSource(convertedSource);
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
      
      // 轉換駝峰命名為蛇形命名（Creatomate Preview SDK 需要）
      const convertToSnakeCase = (obj: any): any => {
        if (Array.isArray(obj)) {
          return obj.map(item => convertToSnakeCase(item));
        } else if (obj !== null && typeof obj === 'object') {
          const newObj: any = {};
          for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
              // 轉換 camelCase 為 snake_case
              const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
              newObj[snakeKey] = convertToSnakeCase(obj[key]);
            }
          }
          return newObj;
        }
        return obj;
      };
      
      const convertedSource = convertToSnakeCase(source);
      console.log('開始載入到預覽...', convertedSource);
      await previewRef.current.setSource(convertedSource);
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
          setError(null); // 清除之前的錯誤
          const source = JSON.parse(jsonInput);
          
          // 先解析時間軸元素，避免狀態不同步
          const elements = parseTimelineElements(source);
          setTimelineElements(elements);
          
          // 轉換駝峰命名為蛇形命名（Creatomate Preview SDK 需要）
          const convertToSnakeCase = (obj: any): any => {
            if (Array.isArray(obj)) {
              return obj.map(item => convertToSnakeCase(item));
            } else if (obj !== null && typeof obj === 'object') {
              const newObj: any = {};
              for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                  // 轉換 camelCase 為 snake_case
                  const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
                  newObj[snakeKey] = convertToSnakeCase(obj[key]);
                }
              }
              return newObj;
            }
            return obj;
          };
          
          // 然後更新預覽源
          const convertedSource = convertToSnakeCase(source);
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
  }, [jsonInput, parseTimelineElements]); // 只依賴jsonInput變化

  // 跳轉到特定時間
  const seekToTime = useCallback(async (time: number, elementIndex?: number) => {
    if (!previewRef.current || !previewReady) return;
    
    try {
      await previewRef.current.setTime(time);
      console.log(`跳轉到時間: ${time}秒`);
      
      // 如果提供了元素索引，同步更新高亮狀態
      if (elementIndex !== undefined && elementIndex !== currentEditingElement) {
        setCurrentEditingElement(elementIndex);
        console.log(`🎯 同步更新高亮元素索引: ${elementIndex}`);
      }
    } catch (err) {
      console.error('跳轉時間失敗:', err);
    }
  }, [previewReady, currentEditingElement]);

  // 檢測當前編輯的元素（按時間軸順序修正版本）
  const detectCurrentElement = useCallback((cursorPosition: number, jsonText: string, timelineElements: Array<any>) => {
    try {
      const source = JSON.parse(jsonText);
      if (!source.elements || !Array.isArray(source.elements)) return -1;
      if (!timelineElements || timelineElements.length === 0) return -1;

      // 找到elements陣列在JSON中的起始位置
      const elementsStart = jsonText.indexOf('"elements"');
      if (elementsStart === -1) return -1;
      
      const arrayStart = jsonText.indexOf('[', elementsStart);
      if (arrayStart === -1) return -1;

      // 如果光標在elements陣列之前，返回-1
      if (cursorPosition < arrayStart) return -1;

      // 解析每個元素的邊界並獲取JSON中的原始索引
      let currentPos = arrayStart + 1;
      let braceDepth = 0;
      let inString = false;
      let escapeNext = false;
      let jsonElementIndex = 0;
      let elementStartPos = currentPos;

      // 跳過空白字符找到第一個元素
      while (currentPos < jsonText.length && /\s/.test(jsonText[currentPos])) {
        currentPos++;
      }
      elementStartPos = currentPos;

      for (let i = currentPos; i < jsonText.length; i++) {
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
            braceDepth++;
          } else if (char === '}') {
            braceDepth--;
            
            // 當前元素結束
            if (braceDepth === 0) {
              // 檢查光標是否在當前元素範圍內
              if (cursorPosition >= elementStartPos && cursorPosition <= i) {
                // 找到光標所在的JSON元素，現在需要找到它在時間軸中的對應索引
                const jsonElement = source.elements[jsonElementIndex];
                if (jsonElement) {
                  // 解析時間字符串轉為秒數（與parseTimelineElements相同邏輯）
                  const parseTime = (timeStr: string): number => {
                    if (typeof timeStr === 'number') return timeStr;
                    const match = String(timeStr).match(/(\d+(\.\d+)?)\s*s?/);
                    return match ? parseFloat(match[1]) : 0;
                  };

                  const elementTime = parseTime(jsonElement.time || jsonElement.start_time || '0');
                  const elementType = jsonElement.type || 'unknown';
                  const elementName = jsonElement.name || `${elementType} ${jsonElementIndex + 1}`;
                  const elementSource = jsonElement.source || '';

                                      console.log(`🔍 JSON元素匹配: 索引=${jsonElementIndex}, 類型=${elementType}, 名稱="${elementName}", 時間=${elementTime}s, source=${elementSource}`);

                  // 開始詳細匹配流程
                  console.log(`🔍 開始詳細匹配流程:`);
                  console.log(`   JSON元素: 索引=${jsonElementIndex}, 類型=${elementType}, 時間=${elementTime}s`);
                  console.log(`   元素詳情: name="${elementName}", source="${elementSource}"`);
                  console.log(`   可用時間軸元素: ${timelineElements.length}個`);

                  // 在時間軸元素中找到匹配的索引
                  const timelineIndex = timelineElements.findIndex((timelineElement, index) => {
                    const typeMatch = timelineElement.type === elementType;
                    
                    // 策略1: 對於有source的元素，優先使用source匹配
                    if (elementSource && timelineElement.source) {
                      const sourceMatch = timelineElement.source === elementSource;
                      console.log(`  策略1-source匹配: ${sourceMatch} (${elementSource} vs ${timelineElement.source})`);
                      if (typeMatch && sourceMatch) {
                        return true;
                      }
                    }
                    
                                        // 策略2: 對於有明確時間和名稱的元素，使用時間+名稱匹配
                    const elementTimeMatch = Math.abs(timelineElement.time - elementTime) < 0.01;
                    if (elementTimeMatch && typeMatch && (elementTime > 0 || jsonElement.time !== undefined)) {
                      const nameMatch = timelineElement.name === elementName;
                      console.log(`  策略2-時間+名稱匹配: ${nameMatch} (時間:${elementTimeMatch}, 名稱:"${timelineElement.name}" vs "${elementName}")`);
                      if (nameMatch) {
                        return true;
                      }
                    }
                    
                    // 策略3: 對於簡單序列（沒有明確time的元素），使用JSON順序匹配
                    if (elementTime === 0 && !jsonElement.time) {
                      // 找到相同類型的第 jsonElementIndex 個元素
                      const sameTypeElements = timelineElements.filter(el => el.type === elementType);
                      const isCorrectIndex = sameTypeElements[jsonElementIndex] === timelineElement;
                      console.log(`  策略3-順序匹配: ${isCorrectIndex} (第${jsonElementIndex}個${elementType}元素，共${sameTypeElements.length}個)`);
                      if (isCorrectIndex) {
                        return true;
                      }
                    }
                    
                    // 策略4: 原始索引匹配（處理 originalIndex 差異）
                    if (typeMatch && timelineElement.path) {
                      const pathParts = timelineElement.path.split('.');
                      const elementOriginalIndex = parseInt(pathParts[pathParts.length - 1]);
                      const indexMatch = elementOriginalIndex === jsonElementIndex;
                      console.log(`  策略4-原始索引匹配: ${indexMatch} (path:${timelineElement.path}, 原始索引:${elementOriginalIndex} vs JSON索引:${jsonElementIndex})`);
                      if (indexMatch) {
                        return true;
                      }
                    }
                    
                    return false;
                  });

                  if (timelineIndex !== -1) {
                    console.log(`✅ 匹配成功: JSON索引=${jsonElementIndex} → 時間軸索引=${timelineIndex}, 元素="${timelineElements[timelineIndex].name}"`);
                    return timelineIndex;
                  } else {
                    console.log(`❌ 精確匹配失敗: JSON索引=${jsonElementIndex}, 嘗試降級策略`);
                    console.log(`   JSON元素詳情: type=${elementType}, time=${elementTime}, name="${elementName}", hasSource=${!!elementSource}`);
                    
                    // 降級匹配：僅針對非常特殊的簡單情況
                    const isVerySimpleCase = (
                      elementTime === 0 && 
                      !jsonElement.time && 
                      !jsonElement.name && 
                      elementSource && 
                      elementType === 'video'
                    );
                    
                    if (isVerySimpleCase && jsonElementIndex < timelineElements.length) {
                      const fallbackElement = timelineElements[jsonElementIndex];
                      if (fallbackElement.type === elementType) {
                        console.log(`🔄 簡單視頻序列降級匹配: 索引${jsonElementIndex} → "${fallbackElement.name}"`);
                        return jsonElementIndex;
                      }
                    }
                    
                    console.log(`❌ 所有匹配策略失敗`);
                    return -1;
                  }
                }
                return -1;
              }
              
              // 準備檢測下一個元素
              jsonElementIndex++;
              
              // 跳過逗號和空白，找到下一個元素開始位置
              let nextPos = i + 1;
              while (nextPos < jsonText.length && /[\s,]/.test(jsonText[nextPos])) {
                nextPos++;
              }
              
              if (nextPos < jsonText.length && jsonText[nextPos] === ']') {
                // 到達陣列結尾
                break;
              }
              
              elementStartPos = nextPos;
            }
          } else if (char === ']' && braceDepth === 0) {
            // 到達elements陣列結尾
            break;
          }
        }
      }

      return -1;
      
    } catch (err) {
      console.error('檢測當前元素失敗:', err);
      return -1;
    }
  }, []);

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
            seekToTime(element.time, elementIndex);
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

  // 複製 API 請求格式 - 完全按照用戶提供的範例格式
  const copyApiRequest = async () => {
    try {
      // 解析當前的 JSON 輸入
      const inputSource = JSON.parse(jsonInput);
      
      // 完全按照你的範例格式包裝成 API 請求格式
      // 你的範例: {"source": {"outputFormat": "mp4", ...}, "output_format": "mp4"}
      const apiRequest = {
        source: inputSource,  // 直接使用輸入的 JSON 作為 source
        output_format: inputSource.output_format || "mp4"
      };
      
      // 轉換為 JSON 字符串
      const apiRequestString = JSON.stringify(apiRequest, null, 2);
      
      // 複製到剪貼板
      await navigator.clipboard.writeText(apiRequestString);
      
      // 顯示成功消息
      console.log('API 請求已複製到剪貼板');
      
      // 視覺反饋
      const button = document.querySelector('[data-copy-api-button]') as HTMLButtonElement;
      if (button) {
        const originalText = button.textContent;
        button.textContent = '已複製！';
        button.style.background = '#45a049';
        setTimeout(() => {
          button.textContent = originalText;
          button.style.background = '#4caf50';
        }, 2000);
      }
      
    } catch (err) {
      console.error('複製 API 請求失敗:', err);
      if (err instanceof SyntaxError) {
        setError('JSON 格式錯誤，無法複製 API 請求');
      } else {
        setError('複製失敗，請重試');
      }
    }
  };

  const examples = [
    {
      name: '載入示例',
      json: `{
  "outputFormat": "mp4",
  "width": 1920,
  "height": 1080,
  "fillColor": "#262626",
  "elements": [
    {
      "type": "video",
      "source": "https://creatomate.com/files/assets/c16f42db-7b5b-4ab7-9625-bc869fae623d.mp4",
      "fit": "cover"
    },
    {
      "type": "text",
      "name": "subtitle",
      "text": "歡迎使用 Creatomate 視頻編輯器",
      "font_family": "Noto Sans TC",
      "font_size": "5.5 vmin",
      "font_size_minimum": "5 vmin",
      "line_height": "126%",
      "font_weight": "700",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "70.3388%",
      "width": "83.1194%",
      "background_color": "rgba(19,19,19,0.7)",
      "time": "0 s",
      "duration": "3 s"
    },
    {
      "type": "text",
      "name": "subtitle",
      "text": "這是一個功能強大的工具",
      "font_family": "Noto Sans TC",
      "font_size": "5.5 vmin",
      "font_size_minimum": "5 vmin",
      "line_height": "126%",
      "font_weight": "700",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "70.3388%",
      "width": "83.1194%",
      "background_color": "rgba(19,19,19,0.7)",
      "time": "3 s",
      "duration": "3 s"
    },
    {
      "type": "text",
      "name": "subtitle",
      "text": "支援即時預覽和編輯",
      "font_family": "Noto Sans TC",
      "font_size": "5.5 vmin",
      "font_size_minimum": "5 vmin",
      "line_height": "126%",
      "font_weight": "700",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "70.3388%",
      "width": "83.1194%",
      "background_color": "rgba(19,19,19,0.7)",
      "time": "6 s",
      "duration": "3 s"
    },
    {
      "type": "text",
      "name": "subtitle",
      "text": "讓創作變得更簡單",
      "font_family": "Noto Sans TC",
      "font_size": "5.5 vmin",
      "font_size_minimum": "5 vmin",
      "line_height": "126%",
      "font_weight": "700",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "70.3388%",
      "width": "83.1194%",
      "background_color": "rgba(19,19,19,0.7)",
      "time": "9 s",
      "duration": "3 s"
    },
    {
      "type": "text",
      "name": "subtitle",
      "text": "開始你的創作之旅吧！",
      "font_family": "Noto Sans TC",
      "font_size": "5.5 vmin",
      "font_size_minimum": "5 vmin",
      "line_height": "126%",
      "font_weight": "700",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "70.3388%",
      "width": "83.1194%",
      "background_color": "rgba(19,19,19,0.7)",
      "time": "12 s",
      "duration": "3 s"
    }
  ]
}`
    },
    {
      name: '從文件載入',
      json: `{
  "outputFormat": "mp4",
  "width": 1920,
  "height": 1080,
  "fillColor": "#000000",
  "elements": [
    {
      "type": "image",
      "source": "https://creatomate-static.s3.amazonaws.com/demo/image1.jpg",
      "fit": "cover",
      "time": "0 s",
      "duration": "4 s"
    },
    {
      "type": "text",
      "name": "title",
      "text": "圖片展示範例",
      "font_family": "Noto Sans TC",
      "font_size": "6 vh",
      "font_weight": "700",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "20%",
      "width": "80%",
      "background_color": "rgba(0,0,0,0.7)",
      "time": "0.5 s",
      "duration": "3 s"
    },
    {
      "type": "image",
      "source": "https://creatomate-static.s3.amazonaws.com/demo/harshil-gudka-77zGnfU_SFU-unsplash.jpg",
      "fit": "cover",
      "time": "4 s",
      "duration": "4 s"
    },
    {
      "type": "text",
      "name": "subtitle",
      "text": "第二張圖片",
      "font_family": "Noto Sans TC",
      "font_size": "6 vh",
      "font_weight": "700",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "20%",
      "width": "80%",
      "background_color": "rgba(0,0,0,0.7)",
      "time": "4.5 s",
      "duration": "3 s"
    },
    {
      "type": "image",
      "source": "https://creatomate-static.s3.amazonaws.com/demo/samuel-ferrara-1527pjeb6jg-unsplash.jpg",
      "fit": "cover",
      "time": "8 s",
      "duration": "4 s"
    },
    {
      "type": "text",
      "name": "ending",
      "text": "感謝觀看",
      "font_family": "Noto Sans TC",
      "font_size": "6 vh",
      "font_weight": "700",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "50%",
      "width": "80%",
      "background_color": "rgba(0,0,0,0.7)",
      "time": "8.5 s",
      "duration": "3 s"
    }
  ]
}`
    },
    {
      name: '載入新的JSON',
      json: `{
  "outputFormat": "mp4",
  "width": 1920,
  "height": 1080,
  "fillColor": "#1a1a1a",
  "elements": [
    {
      "type": "video",
      "source": "https://creatomate-static.s3.amazonaws.com/demo/video1.mp4",
      "fit": "cover",
      "time": "0 s",
      "duration": "10 s"
    },
    {
      "type": "text",
      "name": "main-title",
      "text": "專業視頻編輯工具",
      "font_family": "Noto Sans TC",
      "font_size": "8 vh",
      "font_weight": "900",
      "fill_color": "#FFD700",
      "x_alignment": "50%",
      "y": "25%",
      "width": "90%",
      "time": "1 s",
      "duration": "4 s"
    },
    {
      "type": "text",
      "name": "subtitle",
      "text": "讓創作變得更簡單、更專業",
      "font_family": "Noto Sans TC",
      "font_size": "5 vh",
      "font_weight": "600",
      "fill_color": "#FFFFFF",
      "x_alignment": "50%",
      "y": "40%",
      "width": "90%",
      "background_color": "rgba(0,0,0,0.7)",
      "time": "3 s",
      "duration": "4 s"
    },
    {
      "type": "text",
      "name": "feature1",
      "text": "✓ 即時預覽功能",
      "font_family": "Noto Sans TC",
      "font_size": "4 vh",
      "font_weight": "500",
      "fill_color": "#4CAF50",
      "x_alignment": "50%",
      "y": "60%",
      "width": "80%",
      "time": "5 s",
      "duration": "3 s"
    },
    {
      "type": "text",
      "name": "feature2",
      "text": "✓ 豐富的動畫效果",
      "font_family": "Noto Sans TC",
      "font_size": "4 vh",
      "font_weight": "500",
      "fill_color": "#2196F3",
      "x_alignment": "50%",
      "y": "70%",
      "width": "80%",
      "time": "6 s",
      "duration": "3 s"
    },
    {
      "type": "text",
      "name": "cta",
      "text": "立即開始創作！",
      "font_family": "Noto Sans TC",
      "font_size": "6 vh",
      "font_weight": "800",
      "fill_color": "#FF4444",
      "x_alignment": "50%",
      "y": "85%",
      "width": "80%",
      "time": "7.5 s",
      "duration": "2.5 s"
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
              <CopyApiButton
                data-copy-api-button
                onClick={copyApiRequest}
              >
                複製 api 請求
              </CopyApiButton>
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
                      onClick={() => seekToTime(element.time, index)}
                    >
                      <ElementTime>{element.time}s</ElementTime>
                      <ElementInfo>
                        <ElementType>{element.name}</ElementType>
                        <ElementText>{element.text}</ElementText>
                      </ElementInfo>
                      <TypeBadge $type={element.type}>{element.type}</TypeBadge>
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

const CopyApiButton = styled.button`
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
  font-size: 14px;
  color: #333;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const ElementText = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-style: italic;
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

const TypeBadge = styled.div<{ $type: string }>`
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
  margin-left: auto;
  margin-right: 35px; /* 為 ActiveIndicator 留出空間 */
  align-self: center;
`; 