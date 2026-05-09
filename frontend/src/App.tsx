import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import Header from './components/Header';
import Home from './pages/Home';
import Detail from './pages/Detail';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import { useAuthStore } from './store/auth';

const App: React.FC = () => {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#d4a853',
          colorBgContainer: '#1a2f23',
          colorBgLayout: '#0d1f17',
          colorText: '#f5f5f5',
          colorBorder: '#2d4a35',
          borderRadius: 8,
          fontFamily: '"Noto Sans SC", "PingFang SC", sans-serif',
        },
        components: {
          Layout: {
            headerBg: '#0d1f17',
            bodyBg: '#0d1f17',
          },
          Button: {
            primaryColor: '#0d1f17',
          },
          Input: {
            colorBgContainer: '#0d1f17',
          },
        },
      }}
    >
      <BrowserRouter basename="/dsnake">
        <div
          style={{
            minHeight: '100vh',
            background: 'linear-gradient(180deg, #0d1f17 0%, #1a2f23 50%, #0d1f17 100%)',
          }}
        >
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/:id" element={<Detail />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
