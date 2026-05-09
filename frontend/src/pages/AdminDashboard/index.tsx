import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Table, Modal, Form, Input, Upload, Switch, message, Popconfirm, Typography, Space, Image } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { snakeApi } from '../../services/api';
import type { SnakeListItem, SnakeFormData } from '../../services/api';
import { useAuthStore } from '../../store/auth';
import ToxicBadge from '../../components/ToxicBadge';

const { Title, Text } = Typography;
const { TextArea } = Input;

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, checkAuth } = useAuthStore();
  const [snakes, setSnakes] = useState<SnakeListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form] = Form.useForm();
  const [imageUrl, setImageUrl] = useState<string>('');

  useEffect(() => {
    checkAuth();
    if (!isAuthenticated) {
      navigate('/dsnake/admin/login');
    } else {
      fetchSnakes();
    }
  }, [isAuthenticated, navigate]);

  const fetchSnakes = async () => {
    setLoading(true);
    try {
      const response = await snakeApi.getSnakes({ page_size: 100 });
      setSnakes(response.items);
    } catch (error) {
      message.error('获取蛇类列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    setImageUrl('');
    setModalVisible(true);
  };

  const handleEdit = (record: SnakeListItem) => {
    setEditingId(record.id);
    snakeApi.getSnake(record.id).then((data) => {
      form.setFieldsValue({
        name: data.name,
        scientific_name: data.scientific_name,
        description: data.description,
        temperament: data.temperament,
        treatment: data.treatment,
        is_venomous: data.is_venomous,
      });
      setImageUrl(data.image || '');
      setModalVisible(true);
    });
  };

  const handleDelete = async (id: number) => {
    try {
      await snakeApi.deleteSnake(id);
      message.success('删除成功');
      fetchSnakes();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      const data: SnakeFormData = {
        ...values,
        image: imageUrl || undefined,
      };

      if (editingId) {
        await snakeApi.updateSnake(editingId, data);
        message.success('更新成功');
      } else {
        await snakeApi.createSnake(data);
        message.success('添加成功');
      }

      setModalVisible(false);
      fetchSnakes();
    } catch (error) {
      message.error(editingId ? '更新失败' : '添加失败');
    }
  };

  const handleImageChange = (info: any) => {
    const file = info.file.originFileObj;
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImageUrl(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const columns = [
    {
      title: '图片',
      dataIndex: 'image',
      key: 'image',
      width: 80,
      render: (image: string | null) => (
        image ? (
          <Image src={image} alt="snake" width={60} height={60} style={{ objectFit: 'cover', borderRadius: '8px' }} />
        ) : (
          <span style={{ fontSize: '32px' }}>🐍</span>
        )
      ),
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: SnakeListItem) => (
        <Space direction="vertical" size={0}>
          <Text strong style={{ color: '#f5f5f5', fontSize: '16px' }}>{name}</Text>
          <ToxicBadge isVenomous={record.is_venomous} />
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: SnakeListItem) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            style={{ color: '#d4a853' }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这条记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #0d1f17 0%, #1a2f23 50%, #0d1f17 100%)',
        padding: '24px',
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/dsnake')}
            style={{ background: '#1a2f23', borderColor: '#d4a853', color: '#f5f5f5' }}
          >
            返回首页
          </Button>
          <Title
            level={3}
            style={{
              color: '#d4a853',
              margin: 0,
              fontFamily: '"Noto Serif SC", serif',
            }}
          >
            🐍 管理员控制台
          </Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAdd}
            style={{ background: '#d4a853', borderColor: '#d4a853', color: '#0d1f17', fontWeight: 600 }}
          >
            添加新蛇类
          </Button>
        </div>

        <div
          style={{
            background: 'rgba(26, 47, 35, 0.9)',
            borderRadius: '12px',
            padding: '24px',
            border: '2px solid #2d4a35',
          }}
        >
          <Text style={{ color: '#a8b5a0', marginBottom: '16px', display: 'block' }}>
            共有 {snakes.length} 条记录
          </Text>
          <Table
            columns={columns}
            dataSource={snakes}
            rowKey="id"
            loading={loading}
            pagination={false}
          />
        </div>

        <Modal
          title={editingId ? '编辑蛇类' : '添加新蛇类'}
          open={modalVisible}
          onCancel={() => setModalVisible(false)}
          footer={null}
          width={700}
        >
          <div style={{ background: '#1a2f23', padding: '20px 0' }}>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              initialValues={{ is_venomous: false }}
            >
              <Form.Item
                label={<span style={{ color: '#f5f5f5' }}>名称 *</span>}
                name="name"
                rules={[{ required: true, message: '请输入名称' }]}
              >
                <Input placeholder="请输入蛇类名称" />
              </Form.Item>

              <Form.Item
                label={<span style={{ color: '#f5f5f5' }}>学名</span>}
                name="scientific_name"
              >
                <Input placeholder="请输入学名" />
              </Form.Item>

              <Form.Item
                label={<span style={{ color: '#f5f5f5' }}>描述</span>}
                name="description"
              >
                <TextArea rows={3} placeholder="请输入描述" />
              </Form.Item>

              <Form.Item
                label={<span style={{ color: '#f5f5f5' }}>性格</span>}
                name="temperament"
              >
                <Input placeholder="请输入性格特征" />
              </Form.Item>

              <Form.Item
                label={<span style={{ color: '#f5f5f5' }}>咬伤处理</span>}
                name="treatment"
              >
                <TextArea rows={4} placeholder="请输入咬伤处理方法（支持HTML格式）" />
              </Form.Item>

              <Form.Item
                label={<span style={{ color: '#f5f5f5' }}>是否有毒</span>}
                name="is_venomous"
                valuePropName="checked"
              >
                <Switch checkedChildren="有毒" unCheckedChildren="无毒" />
              </Form.Item>

              <Form.Item label={<span style={{ color: '#f5f5f5' }}>图片</span>}>
                <Upload
                  name="avatar"
                  listType="picture-card"
                  showUploadList={false}
                  beforeUpload={() => false}
                  onChange={handleImageChange}
                >
                  {imageUrl ? (
                    <img src={imageUrl} alt="snake" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <div>
                      <PlusOutlined />
                      <div style={{ marginTop: 8 }}>上传图片</div>
                    </div>
                  )}
                </Upload>
              </Form.Item>

              <Form.Item style={{ marginBottom: 0 }}>
                <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                  <Button onClick={() => setModalVisible(false)}>取消</Button>
                  <Button type="primary" htmlType="submit" style={{ background: '#d4a853', borderColor: '#d4a853' }}>
                    {editingId ? '更新' : '添加'}
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </div>
        </Modal>
      </div>
    </div>
  );
};

export default AdminDashboard;
