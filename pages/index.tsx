import Head from 'next/head';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import styled from 'styled-components';

const App = dynamic(() => import('../components/App'), { ssr: false });

export default function Home() {
  return (
    <div>
      <Head>
        <title>Video Preview Demo</title>
        <link rel='icon' href='/favicon.ico' />
      </Head>

      <NavBar>
        <NavTitle>Video Preview Demo</NavTitle>
        <NavLink>
          <Link href="/tools">🛠️ 工具集</Link>
        </NavLink>
      </NavBar>

      <ContentWrapper>
      <App />
      </ContentWrapper>
    </div>
  );
}

const NavBar = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  z-index: 1000;
`;

const NavTitle = styled.h1`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

const NavLink = styled.div`
  a {
    color: #2196f3;
    text-decoration: none;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 6px;
    transition: background-color 0.2s ease;
    
    &:hover {
      background-color: rgba(33, 150, 243, 0.1);
    }
  }
`;

const ContentWrapper = styled.div`
  padding-top: 60px;
`;
