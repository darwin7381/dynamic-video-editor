/**
 * 時間軸解析器
 * 
 * 解析 Creatomate JSON 並生成時間軸元素列表
 * 支援：
 * - composition 嵌套結構
 * - 多軌道（track）系統
 * - 自動時間軸計算
 * - transition 重疊效果
 */

import { parseTime, estimateDuration } from './jsonHelpers';

export interface TimelineElement {
  id: string;
  time: number;
  duration: number;
  type: string;
  name: string;
  text: string;
  source: string;
  path: string;
  track?: number;
}

/**
 * 解析時間軸元素（支援 composition 嵌套結構）
 */
export function parseTimelineElements(source: any): TimelineElement[] {
  try {
    if (!source.elements || !Array.isArray(source.elements)) {
      console.log('⚠️ 無效的elements陣列:', source.elements);
      return [];
    }

    // 遞歸解析元素（處理composition嵌套和自動時間軸）
    const parseElementsRecursively = (
      elements: any[], 
      parentTime: number = 0, 
      parentPath: string = '',
      parentDuration?: number  // 父 composition 的 duration
    ): TimelineElement[] => {
      const results: TimelineElement[] = [];

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

          // 計算持續時間（正確版本）
          let elementDuration: number;
          let compositionChildElements: TimelineElement[] = [];
          
          if (element.duration !== undefined) {
            // 1. 有明確 duration → 使用明確值
            elementDuration = parseTime(element.duration);
          } else if (parentDuration !== undefined) {
            // 2. 子元素繼承父 composition 的完整 duration
            elementDuration = parentDuration;
            console.log(`📏 子元素 ${element.name} 繼承父 duration: ${elementDuration.toFixed(1)}s`);
          } else if (element.type === 'composition' && element.elements && Array.isArray(element.elements)) {
            // 3. Composition 沒有 duration → 先遞歸解析子元素計算
            compositionChildElements = parseElementsRecursively(
              element.elements,
              0,
              elementPath,
              undefined  // 第一次遞歸不傳 parentDuration
            );
            const maxChildEndTime = Math.max(...compositionChildElements.map(child => 
              child.time + child.duration
            ));
            elementDuration = maxChildEndTime > 0 ? maxChildEndTime : estimateDuration(element);
            console.log(`📏 Composition ${element.name} 基於子元素計算 duration: ${elementDuration.toFixed(1)}s`);
          } else {
            // 4. 其他 → 使用預設估算
            elementDuration = estimateDuration(element);
          }
          
          // 如果是 composition 且有明確 duration，第二次遞歸傳入 duration
          if (element.type === 'composition' && element.elements && Array.isArray(element.elements) && element.duration !== undefined) {
            compositionChildElements = parseElementsRecursively(
              element.elements,
              0,
              elementPath,
              elementDuration  // 傳入 composition 的 duration
            );
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
          const baseElement: TimelineElement = {
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

          // 🔧 只加入實際元素，排除 composition 容器
          if (element.type !== 'composition') {
            results.push(baseElement);
          } else {
            console.log(`⏭️ 跳過 composition 容器: ${element.name} (只加入子元素)`);
          }

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
      .sort((a, b) => {
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
}

