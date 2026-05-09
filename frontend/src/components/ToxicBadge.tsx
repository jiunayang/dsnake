import React from 'react';
import { Tag } from 'antd';

interface ToxicBadgeProps {
  isVenomous: boolean;
}

const ToxicBadge: React.FC<ToxicBadgeProps> = ({ isVenomous }) => {
  return isVenomous ? (
    <Tag color="error" style={{ fontWeight: 600 }}>
      ⚠️ 有毒
    </Tag>
  ) : (
    <Tag color="success" style={{ fontWeight: 600 }}>
      ✅ 无毒
    </Tag>
  );
};

export default ToxicBadge;
