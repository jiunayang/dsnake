import React, { useEffect } from 'react';
import { Layout, Button, Dropdown, Space, Typography } from 'antd';
import { UserOutlined, LoginOutlined, DashboardOutlined, LogoutOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/auth';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, username, logout, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const userMenuItems = isAuthenticated
    ? [
        {
          key: 'greeting',
          label: <Text style={{ color: '#a8b5a0' }}>👋 你好, {username}</Text>,
          disabled: true,
        },
        { type: 'divider' as const },
        {
          key: 'dashboard',
          icon: <DashboardOutlined />,
          label: '进入管理页面',
          onClick: () => navigate('/admin/dashboard'),
        },
        { type: 'divider' as const },
        {
          key: 'logout',
          icon: <LogoutOutlined />,
          label: '退出登录',
          onClick: handleLogout,
        },
      ]
    : [];

  const isAdminPage = location.pathname.includes('/admin');

  return (
    <AntHeader
      style={{
        background: 'linear-gradient(180deg, #1a2f23 0%, #0d1f17 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        borderBottom: '1px solid #d4a853',
        boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
      }}
    >
      <div
        style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
        onClick={() => navigate('/')}
      >
        <span style={{ fontSize: '28px', marginRight: '8px' }}>🐍</span>
        <Text
          strong
          style={{
            fontSize: '20px',
            color: '#d4a853',
            fontFamily: '"Noto Serif SC", serif',
            letterSpacing: '2px',
          }}
        >
          蛇类百科
        </Text>
      </div>

      <div>
        {isAuthenticated ? (
          <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
            <Button
              type="text"
              icon={<UserOutlined />}
              style={{
                color: '#f5f5f5',
                fontSize: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <Space>
                管理员
                <span style={{ fontSize: '12px' }}>▼</span>
              </Space>
            </Button>
          </Dropdown>
        ) : (
          !isAdminPage && (
            <Button
              type="primary"
              icon={<LoginOutlined />}
              onClick={() => navigate('/admin/login')}
              style={{
                background: '#d4a853',
                borderColor: '#d4a853',
                color: '#0d1f17',
                fontWeight: 600,
              }}
            >
              管理员登录
            </Button>
          )
        )}
      </div>
    </AntHeader>
  );
};

export default Header;
