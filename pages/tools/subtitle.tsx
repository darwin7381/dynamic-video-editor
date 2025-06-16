import React, { useRef, useState, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import styled from 'styled-components';
import { Preview, PreviewState } from '@creatomate/preview';

const SubtitleTool: React.FC = () => {
  const [videoUrl, setVideoUrl] = useState('https://creatomate-static.s3.amazonaws.com/demo/video1.mp4');
  const [subtitleText, setSubtitleText] = useState('Hello World\nThis is subtitle text\nYou can edit this');
  const [fontSize, setFontSize] = useState('6');
  const [fontColor, setFontColor] = useState('#ffffff');
  const [backgroundColor, setBackgroundColor] = useState('#000000');
  const [position, setPosition] = useState('bottom');
  
  const [previewReady, setPreviewReady] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const previewRef = useRef<Preview>();

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
      const preview = new Preview(htmlElement, 'player', process.env.NEXT_PUBLIC_CREATOMATE_PUBLIC_TOKEN);

      preview.onReady = () => {
        setPreviewReady(true);
        setError(null);
        updateVideo(); // 初始化時載入視頻
      };

      preview.onLoad = () => {
        setIsLoading(true);
      };

      preview.onLoadComplete = () => {
        setIsLoading(false);
      };

      previewRef.current = preview;
    } catch (err) {
      setError(`預覽初始化失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
    }
  }, []);

  // 更新視頻和字幕
  const updateVideo = useCallback(async () => {
    if (!previewRef.current || !previewReady) return;

    try {
      setError(null);
      setIsLoading(true);
      
      // 將字幕文字分割成行
      const lines = subtitleText.split('\n').filter(line => line.trim());
      const lineDuration = Math.max(2, 10 / lines.length); // 每行至少2秒
      
      const subtitleElements = lines.map((line, index) => ({
        type: 'text',
        track: 2,
        time: index * lineDuration,
        duration: lineDuration,
        text: line.trim(),
        font_family: 'Arial',
        font_size: `${fontSize} vh`,
        font_weight: '700',
        fill_color: fontColor,
        background_color: backgroundColor,
        background_x_padding: '20%',
        background_y_padding: '10%',
        x: '50%',
        y: position === 'bottom' ? '85%' : position === 'center' ? '50%' : '15%',
        x_alignment: '50%',
        y_alignment: '50%',
        animations: [
          {
            time: 'start',
            duration: 0.5,
            easing: 'quadratic-out',
            type: 'fade'
          }
        ]
      }));

      const source = {
        output_format: 'mp4',
        width: 1920,
        height: 1080,
        elements: [
          {
            type: 'video',
            track: 1,
            source: videoUrl
          },
          ...subtitleElements
        ]
      };

      await previewRef.current.setSource(source);
    } catch (err) {
      setError(`更新失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
    } finally {
      setIsLoading(false);
    }
  }, [videoUrl, subtitleText, fontSize, fontColor, backgroundColor, position, previewReady]);

  // 當設置改變時更新視頻
  React.useEffect(() => {
    if (previewReady) {
      const timeoutId = setTimeout(updateVideo, 500); // 防抖
      return () => clearTimeout(timeoutId);
    }
  }, [updateVideo, previewReady]);

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

  return (
    <div>
      <Head>
        <title>生成字幕視頻</title>
        <link rel='icon' href='/favicon.ico' />
      </Head>

      <Container>
        <Header>
          <BackLink>
            <Link href="/tools">← 返回工具集</Link>
          </BackLink>
          <Title>生成字幕視頻</Title>
          <CreateButton onClick={createVideo} disabled={!previewReady || isLoading}>
            {isLoading ? '生成中...' : '創建視頻'}
          </CreateButton>
        </Header>

        <MainContent>
          <LeftPanel>
            <Section>
              <SectionTitle>視頻設置</SectionTitle>
              <InputGroup>
                <Label>視頻URL</Label>
                <Input
                  type="text"
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  placeholder="輸入視頻URL..."
                />
              </InputGroup>
            </Section>

            <Section>
              <SectionTitle>字幕內容</SectionTitle>
              <TextArea
                value={subtitleText}
                onChange={(e) => setSubtitleText(e.target.value)}
                placeholder="輸入字幕文字，每行一句..."
                rows={8}
              />
            </Section>

            <Section>
              <SectionTitle>字幕樣式</SectionTitle>
              <InputGroup>
                <Label>字體大小</Label>
                <Select value={fontSize} onChange={(e) => setFontSize(e.target.value)}>
                  <option value="4">小</option>
                  <option value="6">中</option>
                  <option value="8">大</option>
                  <option value="10">特大</option>
                </Select>
              </InputGroup>

              <InputGroup>
                <Label>文字顏色</Label>
                <ColorInput
                  type="color"
                  value={fontColor}
                  onChange={(e) => setFontColor(e.target.value)}
                />
              </InputGroup>

              <InputGroup>
                <Label>背景顏色</Label>
                <ColorInput
                  type="color"
                  value={backgroundColor}
                  onChange={(e) => setBackgroundColor(e.target.value)}
                />
              </InputGroup>

              <InputGroup>
                <Label>位置</Label>
                <Select value={position} onChange={(e) => setPosition(e.target.value)}>
                  <option value="top">頂部</option>
                  <option value="center">中間</option>
                  <option value="bottom">底部</option>
                </Select>
              </InputGroup>
            </Section>
          </LeftPanel>

          <RightPanel>
            <SectionTitle>視頻預覽</SectionTitle>
            
            {error && <ErrorMessage>{error}</ErrorMessage>}
            
            <PreviewContainer
              ref={(element) => {
                if (element && element !== previewRef.current?.element) {
                  setUpPreview(element);
                }
              }}
            />
            
            {isLoading && <LoadingIndicator>處理中...</LoadingIndicator>}
          </RightPanel>
        </MainContent>
      </Container>
    </div>
  );
};

export default SubtitleTool;

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
  overflow-y: auto;
`;

const RightPanel = styled.div`
  flex: 1;
  padding: 20px;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
`;

const Section = styled.div`
  margin-bottom: 30px;
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;
`;

const InputGroup = styled.div`
  margin-bottom: 15px;
`;

const Label = styled.label`
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #2196f3;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: #2196f3;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  
  &:focus {
    outline: none;
    border-color: #2196f3;
  }
`;

const ColorInput = styled.input`
  width: 100%;
  height: 40px;
  padding: 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  
  &:focus {
    outline: none;
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