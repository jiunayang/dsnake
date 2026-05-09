import React from 'react';
import { Card, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import ToxicBadge from './ToxicBadge';

const { Text } = Typography;

interface SnakeCardProps {
  id: number;
  name: string;
  image: string | null;
  isVenomous: boolean;
}

const SnakeCard: React.FC<SnakeCardProps> = ({ id, name, image, isVenomous }) => {
  const navigate = useNavigate();

  return (
    <Card
      hoverable
      onClick={() => navigate(`/dsnake/${id}`)}
      style={{
        background: 'linear-gradient(145deg, #1a2f23 0%, #0d1f17 100%)',
        border: '2px solid #2d4a35',
        borderRadius: '12px',
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
      }}
      styles={{
        body: { padding: '0' }
      }}
      className="snake-card"
    >
      <div
        style={{
          width: '100%',
          height: '180px',
          background: '#0d1f17',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        }}
      >
        {image ? (
          <img
            src={image}
            alt={name}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
        ) : (
          <span style={{ fontSize: '64px' }}>🐍</span>
        )}
      </div>
      <div style={{ padding: '12px', textAlign: 'center' }}>
        <Text
          strong
          style={{
            color: '#f5f5f5',
            fontSize: '16px',
            display: 'block',
            marginBottom: '8px',
          }}
        >
          {name}
        </Text>
        <ToxicBadge isVenomous={isVenomous} />
      </div>
    </Card>
  );
};

export default SnakeCard;
