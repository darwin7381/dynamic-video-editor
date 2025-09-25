import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import styled from 'styled-components';
import { createMediaProxyUrl, processMediaUrl, detectMediaType, EXAMPLE_MEDIA_URLS } from '../../utility/mediaProxy';

const MediaProxyTest: React.FC = () => {
  const [testUrl, setTestUrl] = useState('https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg');
  const [proxyUrl, setProxyUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const testProxy = async () => {
    if (!testUrl.trim()) {
      setError('請輸入要測試的 URL');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const proxy = createMediaProxyUrl(testUrl);
      setProxyUrl(proxy);

      // 測試代理 API 是否正常工作
      const response = await fetch(proxy);
      
      if (response.ok) {
        setSuccess(true);
        setError(null);
      } else {
        const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
        setError(`代理失敗: ${errorData.error || response.statusText}`);
      }
    } catch (err) {
      setError(`錯誤: ${err instanceof Error ? err.message : '未知錯誤'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const loadExample = (url: string) => {
    setTestUrl(url);
    setProxyUrl('');
    setError(null);
    setSuccess(false);
  };

  const mediaType = testUrl ? detectMediaType(testUrl) : 'unknown';

  return (
    <div>
      <Head>
        <title>媒體代理測試工具</title>
        <link rel='icon' href='/favicon.ico' />
      </Head>

      <Header>
        <BackLink>
          <Link href="/tools">← 返回工具集</Link>
        </BackLink>
        <Title>媒體代理測試工具</Title>
      </Header>

      <Container>
        <Section>
          <SectionTitle>🧪 代理功能測試</SectionTitle>
          <Description>
            此工具用於測試媒體代理 API 是否能正確處理外部媒體資源。
            代理 API 會將外部 URL 轉換為相對路徑，繞過 Creatomate Preview SDK 的安全限制。
          </Description>

          <InputGroup>
            <Label>測試 URL：</Label>
            <Input
              type="url"
              value={testUrl}
              onChange={(e) => setTestUrl(e.target.value)}
              placeholder="https://example.com/image.jpg"
            />
            <MediaTypeTag type={mediaType}>
              {mediaType === 'image' && '🖼️ 圖片'}
              {mediaType === 'video' && '🎬 影片'}
              {mediaType === 'audio' && '🎵 音訊'}
              {mediaType === 'unknown' && '❓ 未知'}
            </MediaTypeTag>
          </InputGroup>

          <ButtonGroup>
            <TestButton onClick={testProxy} disabled={isLoading}>
              {isLoading ? '測試中...' : '🚀 測試代理'}
            </TestButton>
          </ButtonGroup>

          {proxyUrl && (
            <ResultGroup>
              <Label>代理 URL：</Label>
              <CodeBlock>{proxyUrl}</CodeBlock>
              
              {success && (
                <SuccessMessage>
                  ✅ 代理成功！媒體資源可以正常載入。
                </SuccessMessage>
              )}
              
              {error && (
                <ErrorMessage>
                  ❌ {error}
                </ErrorMessage>
              )}
            </ResultGroup>
          )}
        </Section>

        <Section>
          <SectionTitle>📝 範例 URL</SectionTitle>
          <Description>
            點擊下方的範例 URL 來快速測試不同類型的媒體資源：
          </Description>

          <ExampleGroup>
            <ExampleCategory>
              <CategoryTitle>🖼️ 圖片範例</CategoryTitle>
              {EXAMPLE_MEDIA_URLS.images.map((url, index) => (
                <ExampleButton key={index} onClick={() => loadExample(url)}>
                  {url}
                </ExampleButton>
              ))}
              <ExampleButton onClick={() => loadExample('https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg')}>
                https://files.blocktempo.ai/BlockTempo_Daily_v1.5/news_image.jpeg
              </ExampleButton>
            </ExampleCategory>

            <ExampleCategory>
              <CategoryTitle>🎬 影片範例</CategoryTitle>
              {EXAMPLE_MEDIA_URLS.videos.map((url, index) => (
                <ExampleButton key={index} onClick={() => loadExample(url)}>
                  {url}
                </ExampleButton>
              ))}
            </ExampleCategory>

            <ExampleCategory>
              <CategoryTitle>🎭 GIF 範例</CategoryTitle>
              {EXAMPLE_MEDIA_URLS.gifs.map((url, index) => (
                <ExampleButton key={index} onClick={() => loadExample(url)}>
                  {url}
                </ExampleButton>
              ))}
            </ExampleCategory>
          </ExampleGroup>
        </Section>

        <Section>
          <SectionTitle>📖 使用說明</SectionTitle>
          <InstructionList>
            <InstructionItem><strong>步驟 1</strong>：輸入要測試的外部媒體 URL</InstructionItem>
            <InstructionItem><strong>步驟 2</strong>：點擊「測試代理」按鈕</InstructionItem>
            <InstructionItem><strong>步驟 3</strong>：查看代理 URL 和測試結果</InstructionItem>
            <InstructionItem><strong>步驟 4</strong>：在 Creatomate JSON 中使用生成的代理 URL</InstructionItem>
          </InstructionList>

          <CodeExample>
            <h4>在 JSON 中使用代理 URL：</h4>
            <pre>{`{
  "type": "image",
  "source": "${proxyUrl || '/api/media-proxy?url=https%3A//example.com/image.jpg'}"
}`}</pre>
          </CodeExample>
        </Section>
      </Container>
    </div>
  );
};

export default MediaProxyTest;

// Styled Components
const Header = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  z-index: 1000;
`;

const BackLink = styled.div`
  margin-right: 20px;
  
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
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

const Container = styled.div`
  margin-top: 80px;
  padding: 20px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
`;

const Section = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
`;

const Description = styled.p`
  color: #666;
  line-height: 1.5;
  margin: 0 0 20px 0;
`;

const InputGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #2196f3;
  }
`;

const MediaTypeTag = styled.span<{ type: string }>`
  display: inline-block;
  margin-top: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  
  background: ${props => {
    switch (props.type) {
      case 'image': return '#e3f2fd';
      case 'video': return '#f3e5f5';
      case 'audio': return '#e8f5e8';
      default: return '#fafafa';
    }
  }};
  
  color: ${props => {
    switch (props.type) {
      case 'image': return '#1976d2';
      case 'video': return '#7b1fa2';
      case 'audio': return '#388e3c';
      default: return '#666';
    }
  }};
`;

const ButtonGroup = styled.div`
  margin-bottom: 20px;
`;

const TestButton = styled.button`
  background: #2196f3;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  
  &:hover:not(:disabled) {
    background: #1976d2;
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const ResultGroup = styled.div`
  margin-top: 20px;
`;

const CodeBlock = styled.div`
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  word-break: break-all;
  margin-bottom: 12px;
`;

const SuccessMessage = styled.div`
  color: #4caf50;
  font-weight: 500;
  padding: 8px 12px;
  background: #e8f5e8;
  border-radius: 4px;
`;

const ErrorMessage = styled.div`
  color: #f44336;
  font-weight: 500;
  padding: 8px 12px;
  background: #ffebee;
  border-radius: 4px;
`;

const ExampleGroup = styled.div`
  margin-top: 16px;
`;

const ExampleCategory = styled.div`
  margin-bottom: 20px;
`;

const CategoryTitle = styled.h4`
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
`;

const ExampleButton = styled.button`
  display: block;
  width: 100%;
  text-align: left;
  background: #f9f9f9;
  border: 1px solid #ddd;
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  word-break: break-all;
  
  &:hover {
    background: #f0f0f0;
    border-color: #2196f3;
  }
`;

const InstructionList = styled.ol`
  color: #666;
  line-height: 1.6;
  margin: 0;
  padding-left: 20px;
`;

const InstructionItem = styled.li`
  margin-bottom: 8px;
`;

const CodeExample = styled.div`
  margin-top: 20px;
  
  h4 {
    font-size: 14px;
    font-weight: 600;
    color: #333;
    margin: 0 0 8px 0;
  }
  
  pre {
    background: #f5f5f5;
    padding: 12px;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 12px;
    overflow-x: auto;
    margin: 0;
  }
`;
