import Head from 'next/head';
import Link from 'next/link';
import styled from 'styled-components';

export default function Tools() {
  return (
    <div>
      <Head>
        <title>Creatomate 視頻工具集</title>
        <link rel='icon' href='/favicon.ico' />
      </Head>

      <Container>
        <Header>
          <Title>Creatomate 視頻工具集</Title>
          <Subtitle>
            這個項目提供了一系列工具和腳本，用於使用Creatomate API生成和處理視頻，特別是添加字幕到視頻
            中。
          </Subtitle>
        </Header>

        <ToolsGrid>
          <ToolCard>
            <Link href="/tools/preview">
              <CardContent>
                <CardTitle>視頻預覽工具 →</CardTitle>
                <CardDescription>
                  使用我們的預覽工具來即時查看和編輯你的視頻JSON腳本。
                </CardDescription>
              </CardContent>
            </Link>
          </ToolCard>

          <ToolCard>
            <Link href="/tools/subtitle">
              <CardContent>
                <CardTitle>生成字幕視頻 →</CardTitle>
                <CardDescription>
                  為你的視頻即時添加專業字幕效果，支援多種樣式和位置設置。
                </CardDescription>
              </CardContent>
            </Link>
          </ToolCard>

          <ToolCard>
            <Link href="/tools/generate">
              <CardContent>
                <CardTitle>生成基本視頻 →</CardTitle>
                <CardDescription>
                  使用可視化編輯器創建包含文字、圖片的基本視頻內容。
                </CardDescription>
              </CardContent>
            </Link>
          </ToolCard>

          <ToolCard>
            <Link href="/tools/json-test">
              <CardContent>
                <CardTitle>JSON 直接導入編輯器 →</CardTitle>
                <CardDescription>
                  直接編輯JSON代碼來創建視頻，即時預覽，支援完整的Creatomate API格式。
                </CardDescription>
              </CardContent>
            </Link>
          </ToolCard>

          <ToolCard>
            <Link href="/tools/media-proxy-test">
              <CardContent>
                <CardTitle>媒體代理測試工具 →</CardTitle>
                <CardDescription>
                  測試媒體代理功能，解決外部圖片/影片在 Creatomate 預覽中的載入問題。
                </CardDescription>
              </CardContent>
            </Link>
          </ToolCard>
        </ToolsGrid>
      </Container>
    </div>
  );
}

const Container = styled.div`
  min-height: 100vh;
  padding: 40px 20px;
  background: #f8f9fa;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 60px;
`;

const Title = styled.h1`
  font-size: 48px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 20px;
`;

const Subtitle = styled.p`
  font-size: 18px;
  color: #7f8c8d;
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.6;
`;

const ToolsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
`;

const ToolCard = styled.div`
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  }

  a {
    text-decoration: none;
    color: inherit;
  }
`;

const CardContent = styled.div``;

const CardTitle = styled.h3`
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
`;

const CardDescription = styled.p`
  font-size: 16px;
  color: #7f8c8d;
  line-height: 1.5;
`; 