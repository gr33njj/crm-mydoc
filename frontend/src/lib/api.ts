import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password })
    return response.data
  },
  
  register: async (data: any) => {
    const response = await api.post('/api/auth/register', data)
    return response.data
  },
  
  getMe: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },
}

// Tasks API
export const tasksApi = {
  getTasks: async (params?: any) => {
    const response = await api.get('/api/tasks', { params })
    return response.data
  },
  
  getTask: async (id: string) => {
    const response = await api.get(`/api/tasks/${id}`)
    return response.data
  },
  
  createTask: async (data: any) => {
    const response = await api.post('/api/tasks', data)
    return response.data
  },
  
  updateTask: async (id: string, data: any) => {
    const response = await api.patch(`/api/tasks/${id}`, data)
    return response.data
  },
  
  completeTask: async (id: string) => {
    const response = await api.post(`/api/tasks/${id}/complete`)
    return response.data
  },
  
  deleteTask: async (id: string) => {
    await api.delete(`/api/tasks/${id}`)
  },
  
  getComments: async (taskId: string) => {
    const response = await api.get(`/api/tasks/${taskId}/comments`)
    return response.data
  },
  
  addComment: async (taskId: string, content: string) => {
    const response = await api.post(`/api/tasks/${taskId}/comments`, { content })
    return response.data
  },
}

// Chat API
export const chatApi = {
  getRooms: async () => {
    const response = await api.get('/api/chat/rooms')
    return response.data
  },
  
  getMessages: async (roomId: string, params?: any) => {
    const response = await api.get(`/api/chat/rooms/${roomId}/messages`, { params })
    return response.data
  },
  
  sendMessage: async (roomId: string, content: string, replyToId?: string) => {
    const response = await api.post(`/api/chat/rooms/${roomId}/messages`, {
      content,
      reply_to_id: replyToId
    })
    return response.data
  },
  
  createRoom: async (data: any) => {
    const response = await api.post('/api/chat/rooms', data)
    return response.data
  },
}

// Reports API
export const reportsApi = {
  getReports: async (params?: any) => {
    const response = await api.get('/api/reports', { params })
    return response.data
  },
  
  generateReport: async (data: any) => {
    const response = await api.post('/api/reports', data)
    return response.data
  },
  
  getReport: async (id: string) => {
    const response = await api.get(`/api/reports/${id}`)
    return response.data
  },
  
  downloadReport: async (id: string) => {
    const response = await api.get(`/api/reports/${id}/download`, {
      responseType: 'blob'
    })
    return response.data
  },
}







