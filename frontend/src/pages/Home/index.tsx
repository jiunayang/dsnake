import React, { useState, useEffect } from 'react';
import { Input, Radio, Row, Col, Spin, Empty, Pagination } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import SnakeCard from '../../components/SnakeCard';
import { snakeApi } from '../../services/api';
import type { SnakeListItem } from '../../services/api';

const { Search } = Input;

const Home: React.FC = () => {
  const [snakes, setSnakes] = useState<SnakeListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [venomousFilter, setVenomousFilter] = useState<boolean | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchSnakes();
  }, []);

  const fetchSnakes = async () => {
    setLoading(true);
    try {
      const response = await snakeApi.getSnakes({
        search: searchText || undefined,
        is_venomous: venomousFilter ?? undefined,
        page,
        page_size: pageSize,
      });
      setSnakes(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to fetch snakes:', error);
      setSnakes([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchText(value);
    setPage(1);
  };

  const handleVenomousChange = (e: any) => {
    const value = e.target.value;
    setVenomousFilter(value === 'all' ? null : value === 'venomous');
    setPage(1);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #0d1f17 0%, #1a2f23 50%, #0d1f17 100%)',
        padding: '24px',
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div
          style={{
            background: 'rgba(26, 47, 35, 0.8)',
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '24px',
            border: '1px solid #2d4a35',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          }}
        >
          <Search
            placeholder="搜索蛇类名称..."
            prefix={<SearchOutlined style={{ color: '#d4a853' }} />}
            size="large"
            onSearch={handleSearch}
            onChange={(e) => {
              if (!e.target.value) {
                setSearchText('');
                setPage(1);
              }
            }}
            style={{ marginBottom: '16px' }}
          />

          <Radio.Group
            value={venomousFilter === null ? 'all' : venomousFilter ? 'venomous' : 'non-venomous'}
            onChange={handleVenomousChange}
            style={{ width: '100%' }}
          >
            <Radio.Button value="all" style={{ background: '#1a2f23', borderColor: '#d4a853' }}>
              全部
            </Radio.Button>
            <Radio.Button value="venomous" style={{ background: '#1a2f23', borderColor: '#d4a853' }}>
              有毒
            </Radio.Button>
            <Radio.Button value="non-venomous" style={{ background: '#1a2f23', borderColor: '#d4a853' }}>
              无毒
            </Radio.Button>
          </Radio.Group>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '48px' }}>
            <Spin size="large" />
          </div>
        ) : snakes.length === 0 ? (
          <Empty
            description="暂无蛇类数据"
            style={{ color: '#f5f5f5', padding: '48px' }}
          />
        ) : (
          <>
            <Row gutter={[16, 16]}>
              {snakes.map((snake) => (
                <Col key={snake.id} xs={24} sm={12} md={8} lg={6}>
                  <SnakeCard
                    id={snake.id}
                    name={snake.name}
                    image={snake.image}
                    isVenomous={snake.is_venomous}
                  />
                </Col>
              ))}
            </Row>

            {total > pageSize && (
              <div style={{ textAlign: 'center', marginTop: '24px' }}>
                <Pagination
                  current={page}
                  pageSize={pageSize}
                  total={total}
                  onChange={(p, ps) => {
                    setPage(p);
                    setPageSize(ps);
                  }}
                  showSizeChanger
                  showTotal={(t) => `共 ${t} 条`}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Home;
