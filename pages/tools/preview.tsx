import Head from 'next/head';
import Link from 'next/link';
import styled from 'styled-components';
import dynamic from 'next/dynamic';

// 動態載入 App 組件（即現有的預覽功能）
const PreviewApp = dynamic(() => import('../../components/App'), { ssr: false });

export default function PreviewTool() {
  return (
    <div>
      <Head>
        <title>視頻預覽工具</title>
        <link rel='icon' href='/favicon.ico' />
      </Head>

      <Header>
        <BackLink>
          <Link href="/tools">← 返回工具集</Link>
        </BackLink>
        <Title>視頻預覽工具</Title>
      </Header>

      <ContentWrapper>
        <PreviewApp />
      </ContentWrapper>
    </div>
  );
}

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

const ContentWrapper = styled.div`
  margin-top: 60px;
`; 