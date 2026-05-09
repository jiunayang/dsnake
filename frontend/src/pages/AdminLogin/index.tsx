import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Form, Input, Button, Typography, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../store/auth';

const { Title, Link } = Typography;

const AdminLogin: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuthStore();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const success = await login(values.username, values.password);
      if (success) {
        message.success('登录成功');
        const from = (location.state as any)?.from?.pathname || '/dsnake/admin/dashboard';
        navigate(from);
      } else {
        message.error('用户名或密码错误');
      }
    } catch (error) {
      message.error('登录失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #0d1f17 0%, #1a2f23 50%, #0d1f17 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }}
    >
      <Card
        style={{
          width: '100%',
          maxWidth: '420px',
          background: 'rgba(26, 47, 35, 0.95)',
          border: '2px solid #d4a853',
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        }}
        styles={{
          body: { padding: '40px' }
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <span style={{ fontSize: '64px', display: 'block', marginBottom: '16px' }}>🐍</span>
          <Title
            level={2}
            style={{
              color: '#d4a853',
              margin: 0,
              fontFamily: '"Noto Serif SC", serif',
              letterSpacing: '4px',
            }}
          >
            管理员登录
          </Title>
          <div
            style={{
              width: '60px',
              height: '2px',
              background: '#d4a853',
              margin: '12px auto 0',
            }}
          />
        </div>

        <Form
          name="login"
          onFinish={onFinish}
          layout="vertical"
          requiredMark={false}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined style={{ color: '#d4a853' }} />}
              placeholder="用户名"
              size="large"
              style={{
                background: '#0d1f17',
                borderColor: '#2d4a35',
                color: '#f5f5f5',
              }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#d4a853' }} />}
              placeholder="密码"
              size="large"
              style={{
                background: '#0d1f17',
                borderColor: '#2d4a35',
                color: '#f5f5f5',
              }}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: '16px' }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
              style={{
                background: '#d4a853',
                borderColor: '#d4a853',
                color: '#0d1f17',
                fontWeight: 700,
                fontSize: '16px',
                height: '48px',
              }}
            >
              登 录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Link
              onClick={() => navigate('/dsnake')}
              style={{ color: '#a8b5a0' }}
            >
              ← 返回网站首页
            </Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default AdminLogin;
