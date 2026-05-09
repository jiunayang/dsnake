# 蛇类查询网站 - 设计文档

**创建日期**: 2026-05-09
**项目名称**: Snake Encyclopedia (蛇类百科)
**版本**: v1.0

---

## 一、项目概述

### 1.1 目标
构建一个公开的蛇类信息查询网站，用户无需登录即可搜索和浏览蛇类信息，同时提供管理员功能用于管理蛇类数据。

### 1.2 技术栈
- **前端**: React 19 + Ant Design 5
- **后端**: Python 3.11 + FastAPI
- **数据库**: PostgreSQL 15
- **部署**: Docker + Docker Compose

---

## 二、系统架构

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────┐
│                     Docker Compose                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐         ┌─────────────────┐       │
│  │   Frontend      │         │    Backend      │       │
│  │   (React+Nginx) │◄───────►│  (FastAPI)      │       │
│  │   Port: 80      │  HTTP   │   Port: 8000    │       │
│  └─────────────────┘         └────────┬────────┘       │
│                                        │                 │
│                                        ▼                 │
│                               ┌─────────────────┐       │
│                               │   PostgreSQL    │       │
│                               │   Port: 5432    │       │
│                               └─────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 2.2 路由设计
所有路由统一使用 `/dsnake` 作为 base URL：

| 页面 | 路由 | 访问权限 |
|------|------|----------|
| 蛇类列表（首页） | `/dsnake` | 公开 |
| 蛇类详情 | `/dsnake/:id` | 公开 |
| 管理员登录 | `/dsnake/admin/login` | 公开 |
| 管理控制台 | `/dsnake/admin/dashboard` | 需管理员登录 |
| 添加蛇类 | `/dsnake/admin/add` | 需管理员登录 |
| 编辑蛇类 | `/dsnake/admin/edit/:id` | 需管理员登录 |

### 2.3 目录结构
```
snake-website/
├── frontend/                 # React 19 前端
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home/           # /dsnake - 蛇类列表
│   │   │   ├── Detail/         # /dsnake/:id - 详情页
│   │   │   ├── AdminLogin/     # /dsnake/admin/login
│   │   │   └── AdminDashboard/  # /dsnake/admin/*
│   │   ├── components/
│   │   │   ├── SnakeCard/      # 蛇类卡片
│   │   │   ├── SearchBar/      # 搜索栏
│   │   │   ├── Header/         # 顶部导航（含登录/用户菜单）
│   │   │   └── ToxicBadge/     # 毒性标签
│   │   ├── services/
│   │   │   └── api.ts          # API 调用
│   │   ├── store/
│   │   │   └── auth.ts        # 认证状态管理
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   └── nginx.conf
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── routers/
│   │   │   ├── snakes.py      # 蛇类 CRUD
│   │   │   ├── auth.py        # 认证
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── snake.py       # 蛇类模型
│   │   │   ├── admin.py       # 管理员模型
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── snake.py       # Pydantic 模型
│   │   │   ├── auth.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py      # 配置
│   │   │   ├── security.py    # JWT + 限流
│   │   │   └── database.py    # 数据库连接
│   │   ├── __init__.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml
```

---

## 三、数据库设计

### 3.1 表结构

#### snakes 表
```sql
CREATE TABLE snakes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,              -- 名称（中文名）
    scientific_name VARCHAR(200),             -- 学名
    description TEXT,                          -- 描述
    temperament VARCHAR(100),                  -- 性格
    treatment TEXT,                            -- 咬伤处理方法
    is_venomous BOOLEAN DEFAULT FALSE,         -- 是否有毒
    image TEXT,                                -- Base64编码的图片
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_snakes_name ON snakes(name);
CREATE INDEX idx_snakes_venomous ON snakes(is_venomous);
```

#### admins 表
```sql
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.2 初始数据
```sql
-- 默认管理员账号
INSERT INTO admins (username, password_hash) VALUES
('admin', '$2b$12$...'); -- 密码: admin123

-- 示例蛇类数据
INSERT INTO snakes (name, scientific_name, description, temperament, treatment, is_venomous, image) VALUES
('眼镜王蛇', 'Ophiophagus hannah', '世界上最大的毒蛇...', '领地意识强，攻击性强', '1. 保持冷静<br>2. 尽快就医<br>3. 避免剧烈运动', true, '...'),
('玉米蛇', 'Pantherophis guttatus', '最受欢迎的宠物蛇之一...', '性格温顺，较少主动攻击', '无毒，无需特殊处理', false, '...');
```

---

## 四、后端 API 设计

### 4.1 API 基础路径
```
/api/v1
```

### 4.2 公开接口（限流保护）

#### 获取蛇类列表
```
GET /api/v1/snakes
```
**查询参数:**
- `search`: string (可选) - 搜索名称
- `is_venomous`: boolean (可选) - 过滤有毒/无毒
- `page`: integer (默认: 1)
- `page_size`: integer (默认: 20, 最大: 100)

**响应:**
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "name": "眼镜王蛇",
      "is_venomous": true,
      "image": "..."
    }
  ]
}
```

#### 获取蛇类详情
```
GET /api/v1/snakes/{id}
```

**响应:**
```json
{
  "id": 1,
  "name": "眼镜王蛇",
  "scientific_name": "Ophiophagus hannah",
  "description": "...",
  "temperament": "...",
  "treatment": "...",
  "is_venomous": true,
  "image": "...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 4.3 管理员接口（需 JWT 认证）

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

**响应:**
```json
{
  "access_token": "eyJ...",
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
  "name": "新蛇类",
  "scientific_name": "...",
  "description": "...",
  "temperament": "...",
  "treatment": "...",
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

### 4.4 安全机制

#### 限流策略
```python
# 基于 IP 的限流
- 每分钟: 60 次请求
- 每小时: 500 次请求
- 超过限制返回 429 Too Many Requests
```

#### JWT 配置
```python
# Token 配置
- 过期时间: 24 小时
- 算法: HS256
- 密码加密: bcrypt
```

---

## 五、前端设计

### 5.1 视觉风格：自然野性风

#### 色彩系统
| 用途 | 颜色 | Hex |
|------|------|-----|
| 主背景 | 深森林绿 | #0d1f17 |
| 次级背景 | 深墨绿 | #1a2f23 |
| 主色调 | 琥珀金 | #d4a853 |
| 点缀色 | 蛇鳞橙 | #e67e22 |
| 危险色 | 警示红 | #c0392b |
| 安全色 | 翠绿 | #27ae60 |
| 主文字 | 象牙白 | #f5f5f5 |
| 次级文字 | 浅灰绿 | #a8b5a0 |

#### 字体
- 主字体: "Noto Sans SC", "PingFang SC", sans-serif
- 标题字体: "Noto Serif SC", serif

#### 视觉效果
- 蛇皮纹理边框装饰
- 藤蔓元素点缀
- 金色描边卡片
- 渐变阴影效果

### 5.2 页面设计

#### 5.2.1 蛇类列表页（首页 `/dsnake`）
```
┌─────────────────────────────────────────────────────────┐
│  🐍 蛇类百科              [管理员登录] / [👤 用户菜单 ▼] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 🔍 搜索蛇类名称...                                 │ │
│  │                                                    │ │
│  │ [●] 全部  [ ] 有毒  [ ] 无毒                      │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │         │  │         │  │         │  │         │  │
│  │  [图片] │  │  [图片] │  │  [图片] │  │  [图片] │  │
│  │         │  │         │  │         │  │         │  │
│  ├─────────┤  ├─────────┤  ├─────────┤  ├─────────┤  │
│  │ 眼镜王蛇 │  │ 玉米蛇  │  │ 竹叶青  │  │ 银环蛇  │  │
│  │ ⚠️ 有毒  │  │ ✅ 无毒  │  │ ⚠️ 有毒  │  │ ⚠️ 有毒  │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│                                                         │
│                    [加载更多...]                        │
└─────────────────────────────────────────────────────────┘
```

**交互细节:**
- 卡片悬停: 轻微上浮 + 金色边框发光
- 点击卡片: 跳转到详情页 `/dsnake/:id`
- 搜索: 输入时实时搜索（debounce 300ms）
- 过滤: 点击切换，有三种状态（全部/有毒/无毒）

#### 5.2.2 用户菜单（下拉组件）
```
未登录时显示:
[管理员登录]  ← 点击跳转到 /dsnake/admin/login

登录后显示:
[👤 管理员 ▼]  ← 点击展开菜单
  ├── 👋 你好, admin
  ├── ─────────
  ├── ⚙️ 进入管理页面    ← 跳转到 /dsnake/admin/dashboard
  ├── ─────────
  └── 🚪 退出登录
```

#### 5.2.3 蛇类详情页（`/dsnake/:id`）
```
┌─────────────────────────────────────────────────────────┐
│  ← 返回列表                    🐍 眼镜王蛇               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐                                  │
│  │                  │  ⚠️ 有毒 ⚠️                        │
│  │                  │  ──────────────────               │
│  │    [蛇类图片]    │  📖 学名:                          │
│  │                  │  Ophiophagus hannah              │
│  │                  │  ──────────────────               │
│  │                  │  🐍 性格:                          │
│  └──────────────────┘  领地意识强                        │
│                                                         │
│  ─────────────────────────────────────────────────     │
│                                                         │
│  📝 描述                                                │
│  世界上最大的毒蛇，体长可达5米...                         │
│                                                         │
│  ─────────────────────────────────────────────────     │
│                                                         │
│  🏥 咬伤处理                                            │
│  1. 保持冷静，避免恐慌                                  │
│  2. 尽快拨打急救电话                                    │
│  3. 保持伤口低于心脏位置                                │
│  4. 尽快就医                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 5.2.4 管理员登录页（`/dsnake/admin/login`）
```
┌─────────────────────────────────────────────────────────┐
│                    🐍 管理员登录                         │
│                  ─────────────────                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │   用户名                                         │   │
│  │   ┌─────────────────────────────────────────┐  │   │
│  │   │                                         │  │   │
│  │   └─────────────────────────────────────────┘  │   │
│  │                                                 │   │
│  │   密码                                           │   │
│  │   ┌─────────────────────────────────────────┐  │   │
│  │   │                                         │  │   │
│  │   └─────────────────────────────────────────┘  │   │
│  │                                                 │   │
│  │           [登 录]                              │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│              ← 返回网站首页                              │
└─────────────────────────────────────────────────────────┘
```

#### 5.2.5 管理控制台（`/dsnake/admin/dashboard`）
```
┌─────────────────────────────────────────────────────────┐
│  ← 返回首页          🐍 管理员控制台     [👤 admin ▼]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [+ 添加新蛇类]                    共有 XX 条记录       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  ┌────┐  眼镜王蛇     ⚠️ 有毒   [编辑] [删除]   │   │
│  │  │图片│  Ophiophagus hannah                    │   │
│  │  └────┘                                        │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  ┌────┐  玉米蛇       ✅ 无毒   [编辑] [删除]   │   │
│  │  │图片│  Pantherophis guttatus                 │   │
│  │  └────┘                                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.3 组件清单

| 组件 | 功能 | Props |
|------|------|-------|
| `Header` | 顶部导航栏 | - |
| `UserMenu` | 用户下拉菜单 | isLoggedIn, username, onLogin, onLogout |
| `SnakeCard` | 蛇类列表卡片 | snake: {id, name, image, isVenomous} |
| `SnakeDetail` | 详情展示组件 | snake: SnakeDetail |
| `SearchBar` | 搜索+过滤栏 | onSearch, onFilterChange |
| `ToxicBadge` | 毒性标签 | isVenomous: boolean |
| `SnakeForm` | 添加/编辑表单 | initialData?, onSubmit, onCancel |
| `LoadingSpinner` | 加载状态 | - |
| `EmptyState` | 空状态展示 | message |

### 5.4 状态管理

```typescript
// Auth Store
interface AuthState {
  isAuthenticated: boolean;
  username: string | null;
  token: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
}
```

---

## 六、实施计划

### 阶段 1：后端开发

1. **项目初始化**
   - 创建 FastAPI 项目结构
   - 配置 PostgreSQL 连接
   - 实现数据库迁移

2. **认证系统**
   - 实现 JWT Token 生成和验证
   - 实现管理员登录接口
   - 实现密码加密（bcrypt）

3. **蛇类管理 API**
   - 实现 CRUD 接口
   - 实现搜索和过滤
   - 添加限流中间件

4. **测试**
   - 编写单元测试
   - API 接口测试

### 阶段 2：前端开发

1. **项目初始化**
   - 创建 React 19 + Vite 项目
   - 配置 Ant Design 主题
   - 配置路由（base: `/dsnake`）

2. **基础组件**
   - Header + UserMenu
   - ToxicBadge
   - LoadingSpinner

3. **页面开发**
   - 蛇类列表页（Home）
   - 蛇类详情页（Detail）
   - 管理员登录页
   - 管理控制台

4. **状态管理**
   - Auth Store (Zustand)
   - API 服务层

5. **集成测试**
   - 功能测试
   - 响应式测试

### 阶段 3：部署

1. **Docker 配置**
   - 前端 Dockerfile (React build + Nginx)
   - 后端 Dockerfile (Python + uvicorn)
   - docker-compose.yml

2. **环境配置**
   - 环境变量配置
   - 数据库初始化脚本

3. **部署验证**
   - 容器启动测试
   - 数据验证
   - 性能测试

---

## 七、验收标准

### 功能验收
- [ ] 用户可以在首页搜索蛇类名称
- [ ] 用户可以过滤有毒/无毒蛇类
- [ ] 用户可以查看蛇类详情
- [ ] 管理员可以登录系统
- [ ] 登录后可以在用户菜单进入管理页面
- [ ] 管理员可以添加新的蛇类
- [ ] 管理员可以编辑现有的蛇类
- [ ] 管理员可以删除蛇类

### 安全验收
- [ ] 查询接口有请求限流保护
- [ ] 管理接口需要有效的 JWT Token
- [ ] 密码使用 bcrypt 加密

### 部署验收
- [ ] 可以通过 docker-compose 一键启动
- [ ] 前端通过 Nginx 提供服务
- [ ] 后端 API 正常响应

---

## 八、技术决策总结

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 数据库 | PostgreSQL | 用户选择，功能完整 |
| 认证方式 | JWT Token | 标准方案，支持过期 |
| 图片存储 | Base64 | 用户选择，实现简单 |
| 限流策略 | 简单限流 | 防止恶意请求 |
| 前端框架 | React 19 + Ant Design | 用户指定 |
| 后端框架 | FastAPI | 高性能，自动文档 |

---

**文档版本**: v1.0
**最后更新**: 2026-05-09
**状态**: 待用户确认后开始实施
