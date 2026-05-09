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

export const snakeApi = {
  getSnakes: async (params: {
    search?: string;
    is_venomous?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<SnakeListResponse> => {
    const response = await api.get<SnakeListResponse>('/snakes', { params });
    return response.data;
  },

  getSnake: async (id: number): Promise<SnakeDetail> => {
    const response = await api.get<SnakeDetail>(`/snakes/${id}`);
    return response.data;
  },

  createSnake: async (data: SnakeFormData): Promise<SnakeDetail> => {
    const response = await api.post<SnakeDetail>('/snakes', data);
    return response.data;
  },

  updateSnake: async (id: number, data: Partial<SnakeFormData>): Promise<SnakeDetail> => {
    const response = await api.put<SnakeDetail>(`/snakes/${id}`, data);
    return response.data;
  },

  deleteSnake: async (id: number): Promise<void> => {
    await api.delete(`/snakes/${id}`);
  },
};

export const authApi = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', { username, password });
    return response.data;
  },
};

export default api;
