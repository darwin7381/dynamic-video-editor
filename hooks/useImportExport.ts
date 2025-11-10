/**
 * Import/Export Hook
 * 管理 JSON 匯入匯出相關的所有邏輯
 */

import { useState } from 'react';
import { convertToApiRequest, extractFromApiRequest, extractFromElementsInput, showCopyFeedback } from '../utility/apiRequestHelpers';

interface UseImportExportOptions {
  jsonInput: string;
  setJsonInput: (json: string) => void;
  setError: (error: string | null) => void;
}

export function useImportExport({
  jsonInput,
  setJsonInput,
  setError,
}: UseImportExportOptions) {
  const [showImportModal, setShowImportModal] = useState(false);
  const [importJsonInput, setImportJsonInput] = useState('');
  const [showElementsImportModal, setShowElementsImportModal] = useState(false);
  const [elementsImportInput, setElementsImportInput] = useState('');
  
  // 複製 API 請求格式
  const copyApiRequest = async () => {
    try {
      const inputSource = JSON.parse(jsonInput);
      const apiRequestString = convertToApiRequest(inputSource);
      await navigator.clipboard.writeText(apiRequestString);
      showCopyFeedback('[data-copy-api-button]');
      console.log('API 請求已複製到剪貼板');
    } catch (err) {
      console.error('複製 API 請求失敗:', err);
      if (err instanceof SyntaxError) {
        setError('JSON 格式錯誤，無法複製 API 請求');
      } else {
        setError('複製失敗，請重試');
      }
    }
  };
  
  // 打開匯入彈窗
  const openImportModal = () => {
    setShowImportModal(true);
    setImportJsonInput('');
  };
  
  // 處理匯入 JSON 請求
  const handleImportApiRequest = () => {
    try {
      const editorJsonString = extractFromApiRequest(importJsonInput);
      setJsonInput(editorJsonString);
      setShowImportModal(false);
      setImportJsonInput('');
      setError(null);
      console.log('API 請求已成功匯入到編輯器');
    } catch (err) {
      console.error('匯入 API 請求失敗:', err);
      setError(err instanceof Error ? err.message : '匯入失敗，請重試');
    }
  };
  
  // 打開 Elements 匯入彈窗
  const openElementsImportModal = () => {
    setShowElementsImportModal(true);
    setElementsImportInput('');
  };
  
  // 處理匯入 Elements
  const handleImportElements = () => {
    try {
      const editorJsonString = extractFromElementsInput(elementsImportInput);
      setJsonInput(editorJsonString);
      setShowElementsImportModal(false);
      setElementsImportInput('');
      setError(null);
      console.log('Elements 已成功匯入到編輯器');
    } catch (err) {
      console.error('匯入 Elements 失敗:', err);
      setError(err instanceof Error ? err.message : '匯入失敗，請重試');
    }
  };
  
  return {
    showImportModal,
    setShowImportModal,
    importJsonInput,
    setImportJsonInput,
    copyApiRequest,
    openImportModal,
    handleImportApiRequest,
    // Elements 匯入相關
    showElementsImportModal,
    setShowElementsImportModal,
    elementsImportInput,
    setElementsImportInput,
    openElementsImportModal,
    handleImportElements,
  };
}

