import React, { useRef, useState, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import styled from 'styled-components';
import { Preview, PreviewState } from '@creatomate/preview';

interface TextElement {
  id: string;
  text: string;
  fontSize: string;
  color: string;
  x: string;
  y: string;
  duration: string;
}

interface ImageElement {
  id: string;
  url: string;
  x: string;
  y: string;
  width: string;
  height: string;
  duration: string;
}

const GenerateTool: React.FC = () => {
  // 基本設置
  const [videoWidth, setVideoWidth] = useState('1920');
  const [videoHeight, setVideoHeight] = useState('1080');
  const [videoDuration, setVideoDuration] = useState('10');
  const [backgroundColor, setBackgroundColor] = useState('#000000');
  
  // 元素
  const [textElements, setTextElements] = useState<TextElement[]>([
    {
      id: '1',
      text: 'Hello World',
      fontSize: '8',
      color: '#ffffff',
      x: '50',
      y: '30',
      duration: '5'
    }
  ]);
  
  const [imageElements, setImageElements] = useState<ImageElement[]>([]);
  
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
        updateVideo();
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

  // 更新視頻
  const updateVideo = useCallback(async () => {
    if (!previewRef.current || !previewReady) return;

    try {
      setError(null);
      setIsLoading(true);
      
      const elements = [];

      // 添加背景
      elements.push({
        type: 'shape',
        track: 1,
        duration: `${videoDuration} s`,
        width: '100%',
        height: '100%',
        fill_color: backgroundColor,
        shape_type: 'rectangle'
      });

      // 添加文字元素
      textElements.forEach((textEl, index) => {
        elements.push({
          type: 'text',
          track: index + 2,
          time: '0 s',
          duration: `${textEl.duration} s`,
          text: textEl.text,
          font_family: 'Arial',
          font_size: `${textEl.fontSize} vh`,
          font_weight: '700',
          fill_color: textEl.color,
          x: `${textEl.x}%`,
          y: `${textEl.y}%`,
          x_alignment: '50%',
          y_alignment: '50%',
          animations: [
            {
              time: 'start',
              duration: 1,
              easing: 'quadratic-out',
              type: 'fade'
            }
          ]
        });
      });

      // 添加圖片元素
      imageElements.forEach((imgEl, index) => {
        elements.push({
          type: 'image',
          track: textElements.length + index + 2,
          time: '0 s',
          duration: `${imgEl.duration} s`,
          source: imgEl.url,
          x: `${imgEl.x}%`,
          y: `${imgEl.y}%`,
          width: `${imgEl.width}%`,
          height: `${imgEl.height}%`,
          x_alignment: '50%',
          y_alignment: '50%',
          animations: [
            {
              time: 'start',
              duration: 1,
              easing: 'quadratic-out',
              type: 'scale',
              start_scale: '80%',
              end_scale: '100%'
            }
          ]
        });
      });

      const source = {
        output_format: 'mp4',
        width: parseInt(videoWidth),
        height: parseInt(videoHeight),
        duration: `${videoDuration} s`,
        elements
      };

      await previewRef.current.setSource(source);
    } catch (err) {
      setError(`更新失敗: ${err instanceof Error ? err.message : '未知錯誤'}`);
    } finally {
      setIsLoading(false);
    }
  }, [videoWidth, videoHeight, videoDuration, backgroundColor, textElements, imageElements, previewReady]);

  // 當設置改變時更新視頻
  React.useEffect(() => {
    if (previewReady) {
      const timeoutId = setTimeout(updateVideo, 500);
      return () => clearTimeout(timeoutId);
    }
  }, [updateVideo, previewReady]);

  // 添加文字元素
  const addTextElement = () => {
    const newElement: TextElement = {
      id: Date.now().toString(),
      text: '新文字',
      fontSize: '6',
      color: '#ffffff',
      x: '50',
      y: '50',
      duration: '5'
    };
    setTextElements([...textElements, newElement]);
  };

  // 更新文字元素
  const updateTextElement = (id: string, updates: Partial<TextElement>) => {
    setTextElements(prev => prev.map(el => el.id === id ? { ...el, ...updates } : el));
  };

  // 刪除文字元素
  const removeTextElement = (id: string) => {
    setTextElements(prev => prev.filter(el => el.id !== id));
  };

  // 添加圖片元素
  const addImageElement = () => {
    const newElement: ImageElement = {
      id: Date.now().toString(),
      url: 'https://creatomate-static.s3.amazonaws.com/demo/image1.jpg',
      x: '50',
      y: '50',
      width: '30',
      height: '30',
      duration: '5'
    };
    setImageElements([...imageElements, newElement]);
  };

  // 更新圖片元素
  const updateImageElement = (id: string, updates: Partial<ImageElement>) => {
    setImageElements(prev => prev.map(el => el.id === id ? { ...el, ...updates } : el));
  };

  // 刪除圖片元素
  const removeImageElement = (id: string) => {
    setImageElements(prev => prev.filter(el => el.id !== id));
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

  return (
    <div>
      <Head>
        <title>生成基本視頻</title>
        <link rel='icon' href='/favicon.ico' />
      </Head>

      <Container>
        <Header>
          <BackLink>
            <Link href="/tools">← 返回工具集</Link>
          </BackLink>
          <Title>生成基本視頻</Title>
          <CreateButton onClick={createVideo} disabled={!previewReady || isLoading}>
            {isLoading ? '生成中...' : '創建視頻'}
          </CreateButton>
        </Header>

        <MainContent>
          <LeftPanel>
            {/* 基本設置 */}
            <Section>
              <SectionTitle>視頻設置</SectionTitle>
              <InputRow>
                <InputGroup>
                  <Label>寬度</Label>
                  <Input
                    type="number"
                    value={videoWidth}
                    onChange={(e) => setVideoWidth(e.target.value)}
                  />
                </InputGroup>
                <InputGroup>
                  <Label>高度</Label>
                  <Input
                    type="number"
                    value={videoHeight}
                    onChange={(e) => setVideoHeight(e.target.value)}
                  />
                </InputGroup>
              </InputRow>
              
              <InputGroup>
                <Label>時長 (秒)</Label>
                <Input
                  type="number"
                  value={videoDuration}
                  onChange={(e) => setVideoDuration(e.target.value)}
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
            </Section>

            {/* 文字元素 */}
            <Section>
              <SectionHeader>
                <SectionTitle>文字元素</SectionTitle>
                <AddButton onClick={addTextElement}>+ 添加文字</AddButton>
              </SectionHeader>
              
              {textElements.map((textEl) => (
                <ElementCard key={textEl.id}>
                  <ElementHeader>
                    <span>文字元素</span>
                    <DeleteButton onClick={() => removeTextElement(textEl.id)}>×</DeleteButton>
                  </ElementHeader>
                  
                  <InputGroup>
                    <Label>文字內容</Label>
                    <Input
                      value={textEl.text}
                      onChange={(e) => updateTextElement(textEl.id, { text: e.target.value })}
                    />
                  </InputGroup>

                  <InputRow>
                    <InputGroup>
                      <Label>字體大小</Label>
                      <Select
                        value={textEl.fontSize}
                        onChange={(e) => updateTextElement(textEl.id, { fontSize: e.target.value })}
                      >
                        <option value="4">小</option>
                        <option value="6">中</option>
                        <option value="8">大</option>
                        <option value="12">特大</option>
                      </Select>
                    </InputGroup>
                    <InputGroup>
                      <Label>顏色</Label>
                      <ColorInput
                        type="color"
                        value={textEl.color}
                        onChange={(e) => updateTextElement(textEl.id, { color: e.target.value })}
                      />
                    </InputGroup>
                  </InputRow>

                  <InputRow>
                    <InputGroup>
                      <Label>X位置 (%)</Label>
                      <Input
                        type="number"
                        value={textEl.x}
                        onChange={(e) => updateTextElement(textEl.id, { x: e.target.value })}
                        min="0"
                        max="100"
                      />
                    </InputGroup>
                    <InputGroup>
                      <Label>Y位置 (%)</Label>
                      <Input
                        type="number"
                        value={textEl.y}
                        onChange={(e) => updateTextElement(textEl.id, { y: e.target.value })}
                        min="0"
                        max="100"
                      />
                    </InputGroup>
                  </InputRow>

                  <InputGroup>
                    <Label>持續時間 (秒)</Label>
                    <Input
                      type="number"
                      value={textEl.duration}
                      onChange={(e) => updateTextElement(textEl.id, { duration: e.target.value })}
                    />
                  </InputGroup>
                </ElementCard>
              ))}
            </Section>

            {/* 圖片元素 */}
            <Section>
              <SectionHeader>
                <SectionTitle>圖片元素</SectionTitle>
                <AddButton onClick={addImageElement}>+ 添加圖片</AddButton>
              </SectionHeader>
              
              {imageElements.map((imgEl) => (
                <ElementCard key={imgEl.id}>
                  <ElementHeader>
                    <span>圖片元素</span>
                    <DeleteButton onClick={() => removeImageElement(imgEl.id)}>×</DeleteButton>
                  </ElementHeader>
                  
                  <InputGroup>
                    <Label>圖片URL</Label>
                    <Input
                      value={imgEl.url}
                      onChange={(e) => updateImageElement(imgEl.id, { url: e.target.value })}
                    />
                  </InputGroup>

                  <InputRow>
                    <InputGroup>
                      <Label>X位置 (%)</Label>
                      <Input
                        type="number"
                        value={imgEl.x}
                        onChange={(e) => updateImageElement(imgEl.id, { x: e.target.value })}
                        min="0"
                        max="100"
                      />
                    </InputGroup>
                    <InputGroup>
                      <Label>Y位置 (%)</Label>
                      <Input
                        type="number"
                        value={imgEl.y}
                        onChange={(e) => updateImageElement(imgEl.id, { y: e.target.value })}
                        min="0"
                        max="100"
                      />
                    </InputGroup>
                  </InputRow>

                  <InputRow>
                    <InputGroup>
                      <Label>寬度 (%)</Label>
                      <Input
                        type="number"
                        value={imgEl.width}
                        onChange={(e) => updateImageElement(imgEl.id, { width: e.target.value })}
                        min="1"
                        max="100"
                      />
                    </InputGroup>
                    <InputGroup>
                      <Label>高度 (%)</Label>
                      <Input
                        type="number"
                        value={imgEl.height}
                        onChange={(e) => updateImageElement(imgEl.id, { height: e.target.value })}
                        min="1"
                        max="100"
                      />
                    </InputGroup>
                  </InputRow>

                  <InputGroup>
                    <Label>持續時間 (秒)</Label>
                    <Input
                      type="number"
                      value={imgEl.duration}
                      onChange={(e) => updateImageElement(imgEl.id, { duration: e.target.value })}
                    />
                  </InputGroup>
                </ElementCard>
              ))}
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

export default GenerateTool;

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

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

const AddButton = styled.button`
  padding: 6px 12px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  
  &:hover {
    background: #1976d2;
  }
`;

const ElementCard = styled.div`
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
`;

const ElementHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: 500;
  color: #333;
`;

const DeleteButton = styled.button`
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: #d32f2f;
  }
`;

const InputGroup = styled.div`
  margin-bottom: 15px;
`;

const InputRow = styled.div`
  display: flex;
  gap: 10px;
  
  ${InputGroup} {
    flex: 1;
  }
`;

const Label = styled.label`
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
`;

const Input = styled.input`
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #2196f3;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 6px 8px;
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
  height: 32px;
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