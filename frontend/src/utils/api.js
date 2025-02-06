import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const login = async (username, password) => {
  const response = await api.post('/login', { username, password });
  return response.data;
};

export const getPages = async () => {
  const response = await api.get('/pages');
  return response.data;
};

export const createPage = async (page) => {
  const response = await api.post('/pages', page);
  return response.data;
};

export const updatePage = async (id, page) => {
  const response = await api.put(`/pages/${id}`, page);
  return response.data;
};

export const deletePage = async (id) => {
  const response = await api.delete(`/pages/${id}`);
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get('/categories');
  return response.data;
};

export const createCategory = async (category) => {
  const response = await api.post('/categories', category);
  return response.data;
};

export const updateCategory = async (id, category) => {
  const response = await api.put(`/categories/${id}`, category);
  return response.data;
};

export const deleteCategory = async (id) => {
  const response = await api.delete(`/categories/${id}`);
  return response.data;
};

export const getLinks = async () => {
  const response = await api.get('/links');
  return response.data;
};

export const createLink = async (link) => {
  const response = await api.post('/links', link);
  return response.data;
};

export const updateLink = async (id, link) => {
  const response = await api.put(`/links/${id}`, link);
  return response.data;
};

export const deleteLink = async (id) => {
  const response = await api.delete(`/links/${id}`);
  return response.data;
};

export const getUsers = async () => {
  const response = await api.get('/admin/users');
  return response.data;
};

export const addUser = async (user) => {
  const response = await api.post('/admin/users', user);
  return response.data;
};

export const updateUser = async (id, user) => {
  const response = await api.put(`/admin/users/${id}`, user);
  return response.data;
};

export const deleteUser = async (id) => {
  const response = await api.delete(`/admin/users/${id}`);
  return response.data;
};

export const exportData = async () => {
  const response = await api.get('/admin/backup/export');
  return response.data;
};

export const importData = async (formData) => {
  const response = await api.post('/admin/backup/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
