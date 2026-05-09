import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Spin, Typography, Row, Col, Divider, message } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import ToxicBadge from '../../components/ToxicBadge';
import { snakeApi } from '../../services/api';
import type { SnakeDetail } from '../../services/api';

const { Title, Text, Paragraph } = Typography;

const Detail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [snake, setSnake] = useState<SnakeDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchSnake(parseInt(id));
    }
  }, [id]);

  const fetchSnake = async (snakeId: number) => {
    setLoading(true);
    try {
      const data = await snakeApi.getSnake(snakeId);
      setSnake(data);
    } catch (error) {
      message.error('获取蛇类信息失败');
      navigate('/dsnake');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          background: 'linear-gradient(180deg, #0d1f17 0%, #1a2f23 50%, #0d1f17 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Spin size="large" />
      </div>
    );
  }

  if (!snake) {
    return null;
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #0d1f17 0%, #1a2f23 50%, #0d1f17 100%)',
        padding: '24px',
      }}
    >
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/dsnake')}
          style={{
            marginBottom: '24px',
            background: '#1a2f23',
            borderColor: '#d4a853',
            color: '#f5f5f5',
          }}
        >
          返回列表
        </Button>

        <div
          style={{
            background: 'rgba(26, 47, 35, 0.9)',
            borderRadius: '12px',
            padding: '32px',
            border: '2px solid #d4a853',
            boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
          }}
        >
          <Row gutter={[32, 32]}>
            <Col xs={24} md={10}>
              <div
                style={{
                  width: '100%',
                  height: '300px',
                  background: '#0d1f17',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                  border: '2px solid #2d4a35',
                }}
              >
                {snake.image ? (
                  <img
                    src={snake.image}
                    alt={snake.name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  <span style={{ fontSize: '96px' }}>🐍</span>
                )}
              </div>
            </Col>

            <Col xs={24} md={14}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <Title
                  level={2}
                  style={{
                    color: '#d4a853',
                    margin: 0,
                    fontFamily: '"Noto Serif SC", serif',
                  }}
                >
                  🐍 {snake.name}
                </Title>
                <ToxicBadge isVenomous={snake.is_venomous} />
              </div>

              {snake.scientific_name && (
                <div style={{ marginBottom: '16px' }}>
                  <Text strong style={{ color: '#d4a853', fontSize: '14px' }}>
                    📖 学名
                  </Text>
                  <Paragraph
                    style={{
                      color: '#f5f5f5',
                      fontSize: '16px',
                      marginBottom: '8px',
                      fontStyle: 'italic',
                    }}
                  >
                    {snake.scientific_name}
                  </Paragraph>
                </div>
              )}

              {snake.temperament && (
                <div style={{ marginBottom: '16px' }}>
                  <Text strong style={{ color: '#d4a853', fontSize: '14px' }}>
                    🐍 性格
                  </Text>
                  <Paragraph style={{ color: '#f5f5f5', fontSize: '16px', marginBottom: 0 }}>
                    {snake.temperament}
                  </Paragraph>
                </div>
              )}

              <Divider style={{ borderColor: '#2d4a35' }} />

              {snake.description && (
                <div style={{ marginBottom: '16px' }}>
                  <Text strong style={{ color: '#d4a853', fontSize: '14px' }}>
                    📝 描述
                  </Text>
                  <Paragraph style={{ color: '#f5f5f5', fontSize: '16px', marginBottom: 0 }}>
                    {snake.description}
                  </Paragraph>
                </div>
              )}

              {snake.treatment && (
                <div>
                  <Text strong style={{ color: '#d4a853', fontSize: '14px' }}>
                    🏥 咬伤处理
                  </Text>
                  <div
                    style={{
                      color: '#f5f5f5',
                      fontSize: '16px',
                      marginTop: '8px',
                      lineHeight: '1.8',
                    }}
                    dangerouslySetInnerHTML={{ __html: snake.treatment }}
                  />
                </div>
              )}
            </Col>
          </Row>
        </div>
      </div>
    </div>
  );
};

export default Detail;
