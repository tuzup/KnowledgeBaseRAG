import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post(
    `${API_URL}/api/v1/upload/file`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

export const processDocument = async (pdfPath, category, subcategory = '') => {
  const response = await api.post('/api/v1/documents/process', {
    pdf_path_or_url: pdfPath,
    category,
    subcategory,
  });
  return response.data;
};

export const getTaskStatus = async (taskId) => {
  const response = await api.get(`/api/v1/documents/task/${taskId}`);
  return response.data;
};

export const searchDocuments = async (queryText, nResults = 10, filters = {}) => {
  const response = await api.post('/api/v1/documents/search', {
    query_text: queryText,
    n_results: nResults,
    ...filters,
  });
  return response.data;
};

export const listChunks = async (documentId = null, limit = 100, offset = 0) => {
  const params = { limit, offset };
  if (documentId) {
    params.document_id = documentId;
  }
  const response = await api.get('/api/v1/documents/chunks', { params });
  return response.data;
};

export const listDocuments = async () => {
  const response = await api.get('/api/v1/documents/list');
  return response.data;
};

export default api;
