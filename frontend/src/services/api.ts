import axios from 'axios';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface SnakeListItem {
  id: number;
  name: string;
  is_venomous: boolean;
  image: string | null;
}

export interface SnakeDetail {
  id: number;
  name: string;
  scientific_name: string | null;
  description: string | null;
  temperament: string | null;
  treatment: string | null;
  is_venomous: boolean;
  image: string | null;
  created_at: string | null;
}

export interface SnakeListResponse {
  total: number;
  page: number;
  page_size: number;
  items: SnakeListItem[];
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface SnakeFormData {
  name: string;
  scientific_name?: string;
  description?: string;
  temperament?: string;
  treatment?: string;
  is_venomous: boolean;
  image?: string;
}

const MOCK_SNAKES: SnakeListItem[] = [
  { id: 1, name: '眼镜王蛇', is_venomous: true, image: null },
  { id: 2, name: '玉米蛇', is_venomous: false, image: null },
  { id: 3, name: '竹叶青', is_venomous: true, image: null },
  { id: 4, name: '银环蛇', is_venomous: true, image: null },
  { id: 5, name: '球蟒', is_venomous: false, image: null },
];

const MOCK_SNAKE_DETAILS: Record<number, SnakeDetail> = {
  1: {
    id: 1,
    name: '眼镜王蛇',
    scientific_name: 'Ophiophagus hannah',
    description: '眼镜王蛇是世界上最大的毒蛇，体长可达5米。它们主要分布在南亚和东南亚地区。',
    temperament: '领地意识强，行动敏捷，遇到威胁时会立起身体前部并展开颈部的皮褶',
    treatment: '1. 保持冷静，避免恐慌<br>2. 尽快拨打急救电话<br>3. 保持伤口低于心脏位置<br>4. 避免剧烈运动<br>5. 尽快就医',
    is_venomous: true,
    image: null,
    created_at: new Date().toISOString(),
  },
  2: {
    id: 2,
    name: '玉米蛇',
    scientific_name: 'Pantherophis guttatus',
    description: '玉米蛇是最受欢迎的宠物蛇之一，原产于北美洲。它们性格温顺，体色丰富多变。',
    temperament: '性格温顺，很少主动攻击人类，适应能力强',
    treatment: '无毒，无需特殊处理。如有咬伤，清洁伤口即可。',
    is_venomous: false,
    image: null,
    created_at: new Date().toISOString(),
  },
  3: {
    id: 3,
    name: '竹叶青',
    scientific_name: 'Trimeresurus stejnegeri',
    description: '竹叶青是一种小型毒蛇，身体呈翠绿色，常栖息于树枝上。',
    temperament: '性格较神经质，容易被惊扰，有领域性',
    treatment: '1. 保持冷静<br>2. 尽快就医<br>3. 固定受伤部位<br>4. 避免使用止血带',
    is_venomous: true,
    image: null,
    created_at: new Date().toISOString(),
  },
  4: {
    id: 4,
    name: '银环蛇',
    scientific_name: 'Bungarus multicinctus',
    description: '银环蛇是中国常见的毒蛇之一，身上有银白色的环纹。虽然体型不大，但毒性很强。',
    temperament: '性格胆小，常在夜间活动，一般不主动攻击',
    treatment: '1. 立即就医<br>2. 保持静止<br>3. 不要使用止血带或吸毒<br>4. 记录蛇的外观特征',
    is_venomous: true,
    image: null,
    created_at: new Date().toISOString(),
  },
  5: {
    id: 5,
    name: '球蟒',
    scientific_name: 'Python regius',
    description: '球蟒是最小的蟒蛇之一，因受到惊吓时会缩成一团而得名。它们是非常适合初学者的宠物蛇。',
    temperament: '性格温和，较为害羞，喜欢温暖的环境',
    treatment: '无毒，非常温顺，一般不会咬人。',
    is_venomous: false,
    image: null,
    created_at: new Date().toISOString(),
  },
};

let useMockData = false;

export const snakeApi = {
  setMockMode: (mock: boolean) => {
    useMockData = mock;
  },

  getSnakes: async (params: {
    search?: string;
    is_venomous?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<SnakeListResponse> => {
    if (useMockData) {
      let items = [...MOCK_SNAKES];
      if (params.search) {
        items = items.filter(s => s.name.includes(params.search!));
      }
      if (params.is_venomous !== undefined) {
        items = items.filter(s => s.is_venomous === params.is_venomous);
      }
      return {
        total: items.length,
        page: params.page || 1,
        page_size: params.page_size || 20,
        items,
      };
    }
    const response = await api.get<SnakeListResponse>('/snakes', { params });
    return response.data;
  },

  getSnake: async (id: number): Promise<SnakeDetail> => {
    if (useMockData) {
      return MOCK_SNAKE_DETAILS[id] || MOCK_SNAKE_DETAILS[1];
    }
    const response = await api.get<SnakeDetail>(`/snakes/${id}`);
    return response.data;
  },

  createSnake: async (data: SnakeFormData): Promise<SnakeDetail> => {
    if (useMockData) {
      return { ...data, id: Date.now(), created_at: new Date().toISOString() } as SnakeDetail;
    }
    const response = await api.post<SnakeDetail>('/snakes', data);
    return response.data;
  },

  updateSnake: async (id: number, data: Partial<SnakeFormData>): Promise<SnakeDetail> => {
    if (useMockData) {
      return { ...MOCK_SNAKE_DETAILS[id], ...data } as SnakeDetail;
    }
    const response = await api.put<SnakeDetail>(`/snakes/${id}`, data);
    return response.data;
  },

  deleteSnake: async (id: number): Promise<void> => {
    if (useMockData) {
      return;
    }
    await api.delete(`/snakes/${id}`);
  },
};

export const authApi = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    if (useMockData) {
      if (username === 'admin' && password === 'admin123') {
        return {
          access_token: 'mock_token_' + Date.now(),
          token_type: 'bearer',
          expires_in: 86400,
        };
      }
      throw new Error('Invalid credentials');
    }
    const response = await api.post<LoginResponse>('/auth/login', { username, password });
    return response.data;
  },
};

export default api;
