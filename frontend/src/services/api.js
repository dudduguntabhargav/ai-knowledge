import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/register', data),
  login: (data) => api.post('/login', data),
  logout: () => api.post('/logout'),
  getMe: () => api.get('/me'),
};

// RAG API (via Go gateway with authentication)
export const ragAPI = {
  uploadDocument: (userEmail, file) => {
    const formData = new FormData();
    formData.append('user_email', userEmail);
    formData.append('file', file);

    const token = localStorage.getItem('token');
    return axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  query: (userEmail, query) => {
    const token = localStorage.getItem('token');
    return axios.post(`${API_BASE_URL}/query`, {
      user_email: userEmail,
      query,
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  uploadAndQuery: (userEmail, file, query) => {
    const formData = new FormData();
    formData.append('user_email', userEmail);
    formData.append('file', file);
    formData.append('query', query);

    const token = localStorage.getItem('token');
    return axios.post(`${API_BASE_URL}/upload-and-query`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  getConversations: () => {
    const token = localStorage.getItem('token');
    return axios.get(`${API_BASE_URL}/conversations`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  getDocuments: () => {
    const token = localStorage.getItem('token');
    return axios.get(`${API_BASE_URL}/documents`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  clearConversations: () => {
    const token = localStorage.getItem('token');
    return axios.delete(`${API_BASE_URL}/conversations`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  queryStream: async (userEmail, query, onChunk, onDone, onError) => {
    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`${API_BASE_URL}/query-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_email: userEmail,
          query,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.error) {
                onError(data.error);
                return;
              }

              if (data.done) {
                onDone();
                return;
              }

              if (data.chunk) {
                onChunk(data.chunk);
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      onError(error.message);
    }
  },
};

export default api;
