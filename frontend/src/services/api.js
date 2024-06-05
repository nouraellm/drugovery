import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    return api.post('/auth/login', params.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  register: (data) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};

// Compounds API
export const compoundsAPI = {
  list: (params) => api.get('/compounds', { params }),
  get: (id) => api.get(`/compounds/${id}`),
  create: (data) => api.post('/compounds', data),
  update: (id, data) => api.put(`/compounds/${id}`, data),
  delete: (id) => api.delete(`/compounds/${id}`),
  getVersions: (id, params) => api.get(`/compounds/${id}/versions`, { params }),
  rollback: (id, version) => api.post(`/compounds/${id}/rollback/${version}`),
  importChembl: (chemblId) => api.post(`/compounds/import/chembl/${chemblId}`),
};

// Predictions API
export const predictionsAPI = {
  list: (params) => api.get('/predictions', { params }),
  get: (id) => api.get(`/predictions/${id}`),
  create: (data) => api.post('/predictions', data),
  batch: (data) => api.post('/predictions/batch', data),
  getByCompound: (id) => api.get(`/predictions/compound/${id}`),
};

// Experiments API
export const experimentsAPI = {
  list: (params) => api.get('/experiments', { params }),
  get: (id) => api.get(`/experiments/${id}`),
  create: (data) => api.post('/experiments', data),
  update: (id, data) => api.put(`/experiments/${id}`, data),
  logToMlflow: (id) => api.post(`/experiments/${id}/log-to-mlflow`),
};

// Reports API
export const reportsAPI = {
  exportCompoundsCSV: (params) =>
    api.get('/reports/compounds/csv', { params, responseType: 'blob' }),
  exportPredictionsCSV: (params) =>
    api.get('/reports/predictions/csv', { params, responseType: 'blob' }),
  exportExperimentPDF: (id) =>
    api.get(`/reports/experiment/${id}/pdf`, { responseType: 'blob' }),
};

export default api;
