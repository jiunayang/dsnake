# 🐍 蛇类百科 (Snake Encyclopedia)

一个优雅的蛇类信息查询网站，提供蛇类搜索、浏览和管理功能。采用自然野性的视觉风格，深绿色与琥珀金色调营造神秘的丛林氛围。

**[访问网站](http://localhost:5180/dsnake)** | **[管理后台](http://localhost:5180/dsnake/admin/login)**

---

## ✨ 功能特性

### 用户端
- 🔍 **智能搜索** - 支持按名称实时搜索蛇类信息
- 🎯 **分类筛选** - 快速筛选有毒/无毒蛇类
- 📖 **详细信息** - 查看蛇类完整资料、习性及咬伤处理方法
- 🖼️ **图片展示** - 直观展示蛇类图片
- 📱 **响应式设计** - 适配各种屏幕尺寸

### 管理端
- 🔐 **安全认证** - JWT Token 认证，24小时有效期
- ➕ **添加蛇类** - 上传蛇类信息及图片
- ✏️ **编辑信息** - 修改现有蛇类资料
- 🗑️ **删除管理** - 删除不需要的蛇类记录

### 安全特性
- 🚦 **请求限流** - 公开接口每分钟60次请求限制
- 🔒 **密码加密** - bcrypt 加密存储
- 🎫 **JWT 认证** - 标准 Token 认证机制

---

## 🛠️ 技术栈

### 前端
- **框架**: React 19
- **构建工具**: Vite
- **UI 库**: Ant Design 5
- **状态管理**: Zustand
- **路由**: React Router 6 (basename: /dsnake)
- **类型**: TypeScript

### 后端
- **框架**: FastAPI (Python 3.11)
- **数据库**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **认证**: JWT (PyJWT)
- **限流**: SlowAPI
- **密码加密**: bcrypt (passlib)

### 部署
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx
- **ASGI服务器**: Uvicorn

---

## 📁 项目结构

```
dsnake/
├── frontend/                      # React 前端应用
│   ├── src/
│   │   ├── components/           # 通用组件
│   │   │   ├── Header.tsx        # 顶部导航栏
│   │   │   ├── SnakeCard.tsx     # 蛇类卡片
│   │   │   └── ToxicBadge.tsx    # 毒性标签
│   │   ├── pages/                # 页面组件
│   │   │   ├── Home/             # 首页 - 蛇类列表
│   │   │   ├── Detail/           # 详情页
│   │   │   ├── AdminLogin/       # 管理员登录
│   │   │   └── AdminDashboard/   # 管理控制台
│   │   ├── services/
│   │   │   └── api.ts            # API 服务层
│   │   ├── store/
│   │   │   └── auth.ts           # 认证状态管理
│   │   ├── App.tsx               # 应用入口
│   │   └── main.tsx              # 渲染入口
│   ├── Dockerfile                # 前端 Docker 配置
│   ├── nginx.conf                # Nginx 配置
│   ├── vite.config.ts            # Vite 配置
│   └── package.json
│
├── backend/                      # FastAPI 后端应用
│   ├── app/
│   │   ├── core/                 # 核心模块
│   │   │   ├── config.py         # 应用配置
│   │   │   ├── database.py       # 数据库连接
│   │   │   ├── security.py       # 安全认证
│   │   │   └── limiter.py        # 限流器
│   │   ├── models/               # 数据模型
│   │   │   ├── snake.py          # 蛇类模型
│   │   │   └── admin.py          # 管理员模型
│   │   ├── schemas/              # Pydantic 模型
│   │   │   ├── snake.py          # 蛇类 Schema
│   │   │   └── auth.py           # 认证 Schema
│   │   ├── routers/              # API 路由
│   │   │   └── snakes.py         # 蛇类 CRUD 路由
│   │   └── main.py               # 应用入口
│   ├── Dockerfile                # 后端 Docker 配置
│   ├── requirements.txt          # Python 依赖
│   └── init.sql                  # 数据库初始化
│
├── docker-compose.yml            # Docker Compose 配置
└── README.md                     # 项目文档
```

---

## 🔗 API 文档

### 基础信息
- **API 基础路径**: `/api/v1`
- **内容类型**: `application/json`

### 公开接口 (限流保护: 60次/分钟)

#### 获取蛇类列表
```
GET /api/v1/snakes
```

**查询参数:**
| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| search | string | - | 搜索名称 |
| is_venomous | boolean | - | 过滤有毒/无毒 |
| page | integer | 1 | 页码 |
| page_size | integer | 20 | 每页数量 (最大100) |

**响应示例:**
```json
{
  "total": 5,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "name": "眼镜王蛇",
      "scientific_name": "Ophiophagus hannah",
      "is_venomous": true,
      "image": "data:image/png;base64,..."
    }
  ]
}
```

#### 获取蛇类详情
```
GET /api/v1/snakes/{id}
```

**响应示例:**
```json
{
  "id": 1,
  "name": "眼镜王蛇",
  "scientific_name": "Ophiophagus hannah",
  "description": "世界上最大的毒蛇...",
  "temperament": "领地意识强，攻击性强",
  "treatment": "1. 保持冷静\n2. 尽快就医",
  "is_venomous": true,
  "image": "data:image/png;base64,...",
  "created_at": "2026-05-09T00:00:00Z"
}
```

### 管理员接口 (需 JWT 认证)

#### 管理员登录
```
POST /api/v1/auth/login
```

**请求体:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### 添加蛇类
```
POST /api/v1/snakes
Authorization: Bearer {token}
```

**请求体:**
```json
{
  "name": "竹叶青",
  "scientific_name": "Trimeresurus stejnegeri",
  "description": "常见的绿色毒蛇...",
  "temperament": "领地意识强，受惊时易攻击",
  "treatment": "1. 保持冷静\n2. 尽快就医",
  "is_venomous": true,
  "image": "data:image/png;base64,..."
}
```

#### 更新蛇类
```
PUT /api/v1/snakes/{id}
Authorization: Bearer {token}
```

#### 删除蛇类
```
DELETE /api/v1/snakes/{id}
Authorization: Bearer {token}
```

### 错误响应

| 状态码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 (缺少或无效 Token) |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 (限流) |
| 500 | 服务器内部错误 |

---

## 🚀 快速开始

### 环境要求
- Docker & Docker Compose
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)

### Docker 部署 (推荐)

1. **克隆项目**
```bash
git clone https://github.com/jiunayang/dsnake.git
cd dsnake
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **访问网站**
- 前端: http://localhost/dsnake
- 后端 API: http://localhost/api/v1

### 本地开发

#### 前端开发
```bash
cd frontend
npm install
npm run dev
```
访问: http://localhost:5173/dsnake

#### 后端开发
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档: http://localhost:8000/docs

#### 数据库设置
```bash
# 使用 Docker 启动 PostgreSQL
docker run -d \
  --name dsnake-db \
  -e POSTGRES_DB=dsnake \
  -e POSTGRES_USER=dsnake \
  -e POSTGRES_PASSWORD=dsnake123 \
  -p 5432:5432 \
  postgres:15
```

---

## ⚙️ 配置说明

### 环境变量

#### 后端配置
| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| DATABASE_URL | postgresql://dsnake:dsnake123@db:5432/dsnake | 数据库连接 |
| SECRET_KEY | (随机生成) | JWT 签名密钥 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 1440 | Token 过期时间 (分钟) |
| RATE_LIMIT | 60/minute | 请求限流 |

#### 前端配置
| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| VITE_API_BASE_URL | /api/v1 | API 基础路径 |

### 默认管理员账号
- **用户名**: admin
- **密码**: admin123

⚠️ **重要**: 请在生产环境中修改默认密码！

---

## 🎨 设计规范

### 色彩系统
| 用途 | 颜色名称 | Hex |
|------|----------|-----|
| 主背景 | 深森林绿 | #0d1f17 |
| 次级背景 | 深墨绿 | #1a2f23 |
| 主色调 | 琥珀金 | #d4a853 |
| 点缀色 | 蛇鳞橙 | #e67e22 |
| 危险色 | 警示红 | #c0392b |
| 安全色 | 翠绿 | #27ae60 |
| 主文字 | 象牙白 | #f5f5f5 |
| 次级文字 | 浅灰绿 | #a8b5a0 |

### 路由清单
| 页面 | 路由 | 权限 |
|------|------|------|
| 蛇类列表 | /dsnake | 公开 |
| 蛇类详情 | /dsnake/:id | 公开 |
| 管理员登录 | /dsnake/admin/login | 公开 |
| 管理控制台 | /dsnake/admin/dashboard | 需登录 |
| 添加蛇类 | /dsnake/admin/add | 需登录 |
| 编辑蛇类 | /dsnake/admin/edit/:id | 需登录 |

---

## 📝 数据结构

### 蛇类 (Snake)
| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | integer | - | 主键 |
| name | string | ✅ | 名称 (中文名) |
| scientific_name | string | - | 学名 |
| description | text | - | 描述 |
| temperament | string | - | 性格/习性 |
| treatment | text | - | 咬伤处理方法 |
| is_venomous | boolean | - | 是否有毒 |
| image | text | - | Base64 编码图片 |
| created_at | datetime | - | 创建时间 |
| updated_at | datetime | - | 更新时间 |

### 管理员 (Admin)
| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | integer | - | 主键 |
| username | string | ✅ | 用户名 |
| password_hash | string | ✅ | 密码哈希 |
| created_at | datetime | - | 创建时间 |

---

## 🔧 故障排除

### 常见问题

**Q: Docker 容器启动失败**
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重建容器
docker-compose down
docker-compose up -d --build
```

**Q: 前端无法连接后端 API**
- 检查后端容器是否正常运行
- 确认 Nginx 代理配置正确
- 检查 CORS 配置

**Q: 数据库连接失败**
- 确认 PostgreSQL 容器运行正常
- 检查环境变量 DATABASE_URL
- 确认数据库初始化脚本已执行

---

## 📄 许可证

本项目仅供学习和参考使用。

---

## 🙏 致谢

- [React](https://react.dev/) - 前端框架
- [Ant Design](https://ant.design/) - UI 组件库
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [PostgreSQL](https://www.postgresql.org/) - 数据库
- [Docker](https://www.docker.com/) - 容器化技术
