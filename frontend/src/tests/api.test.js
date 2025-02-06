import axios from 'axios';
import { login, getPages, createPage, updatePage, deletePage, getCategories, createCategory, updateCategory, deleteCategory, getLinks, createLink, updateLink, deleteLink, getUsers, addUser, updateUser, deleteUser, exportData, importData } from '../utils/api';

jest.mock('axios');

describe('API utility functions', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('login function', async () => {
    const mockResponse = { data: { success: true } };
    axios.post.mockResolvedValue(mockResponse);

    const response = await login('username', 'password');
    expect(response).toEqual(mockResponse.data);
    expect(axios.post).toHaveBeenCalledWith('/api/login', { username: 'username', password: 'password' });
  });

  test('getPages function', async () => {
    const mockResponse = { data: [{ id: 1, name: 'Page 1' }] };
    axios.get.mockResolvedValue(mockResponse);

    const response = await getPages();
    expect(response).toEqual(mockResponse.data);
    expect(axios.get).toHaveBeenCalledWith('/api/pages');
  });

  test('createPage function', async () => {
    const mockResponse = { data: { id: 1, name: 'Page 1' } };
    axios.post.mockResolvedValue(mockResponse);

    const response = await createPage({ name: 'Page 1' });
    expect(response).toEqual(mockResponse.data);
    expect(axios.post).toHaveBeenCalledWith('/api/pages', { name: 'Page 1' });
  });

  test('updatePage function', async () => {
    const mockResponse = { data: { id: 1, name: 'Updated Page 1' } };
    axios.put.mockResolvedValue(mockResponse);

    const response = await updatePage(1, { name: 'Updated Page 1' });
    expect(response).toEqual(mockResponse.data);
    expect(axios.put).toHaveBeenCalledWith('/api/pages/1', { name: 'Updated Page 1' });
  });

  test('deletePage function', async () => {
    const mockResponse = { data: {} };
    axios.delete.mockResolvedValue(mockResponse);

    const response = await deletePage(1);
    expect(response).toEqual(mockResponse.data);
    expect(axios.delete).toHaveBeenCalledWith('/api/pages/1');
  });

  test('getCategories function', async () => {
    const mockResponse = { data: [{ id: 1, title: 'Category 1' }] };
    axios.get.mockResolvedValue(mockResponse);

    const response = await getCategories();
    expect(response).toEqual(mockResponse.data);
    expect(axios.get).toHaveBeenCalledWith('/api/categories');
  });

  test('createCategory function', async () => {
    const mockResponse = { data: { id: 1, title: 'Category 1' } };
    axios.post.mockResolvedValue(mockResponse);

    const response = await createCategory({ title: 'Category 1' });
    expect(response).toEqual(mockResponse.data);
    expect(axios.post).toHaveBeenCalledWith('/api/categories', { title: 'Category 1' });
  });

  test('updateCategory function', async () => {
    const mockResponse = { data: { id: 1, title: 'Updated Category 1' } };
    axios.put.mockResolvedValue(mockResponse);

    const response = await updateCategory(1, { title: 'Updated Category 1' });
    expect(response).toEqual(mockResponse.data);
    expect(axios.put).toHaveBeenCalledWith('/api/categories/1', { title: 'Updated Category 1' });
  });

  test('deleteCategory function', async () => {
    const mockResponse = { data: {} };
    axios.delete.mockResolvedValue(mockResponse);

    const response = await deleteCategory(1);
    expect(response).toEqual(mockResponse.data);
    expect(axios.delete).toHaveBeenCalledWith('/api/categories/1');
  });

  test('getLinks function', async () => {
    const mockResponse = { data: [{ id: 1, name: 'Link 1', url: 'http://link1.com' }] };
    axios.get.mockResolvedValue(mockResponse);

    const response = await getLinks();
    expect(response).toEqual(mockResponse.data);
    expect(axios.get).toHaveBeenCalledWith('/api/links');
  });

  test('createLink function', async () => {
    const mockResponse = { data: { id: 1, name: 'Link 1', url: 'http://link1.com' } };
    axios.post.mockResolvedValue(mockResponse);

    const response = await createLink({ name: 'Link 1', url: 'http://link1.com' });
    expect(response).toEqual(mockResponse.data);
    expect(axios.post).toHaveBeenCalledWith('/api/links', { name: 'Link 1', url: 'http://link1.com' });
  });

  test('updateLink function', async () => {
    const mockResponse = { data: { id: 1, name: 'Updated Link 1', url: 'http://updatedlink1.com' } };
    axios.put.mockResolvedValue(mockResponse);

    const response = await updateLink(1, { name: 'Updated Link 1', url: 'http://updatedlink1.com' });
    expect(response).toEqual(mockResponse.data);
    expect(axios.put).toHaveBeenCalledWith('/api/links/1', { name: 'Updated Link 1', url: 'http://updatedlink1.com' });
  });

  test('deleteLink function', async () => {
    const mockResponse = { data: {} };
    axios.delete.mockResolvedValue(mockResponse);

    const response = await deleteLink(1);
    expect(response).toEqual(mockResponse.data);
    expect(axios.delete).toHaveBeenCalledWith('/api/links/1');
  });

  test('getUsers function', async () => {
    const mockResponse = { data: [{ id: 1, username: 'user1' }] };
    axios.get.mockResolvedValue(mockResponse);

    const response = await getUsers();
    expect(response).toEqual(mockResponse.data);
    expect(axios.get).toHaveBeenCalledWith('/api/admin/users');
  });

  test('addUser function', async () => {
    const mockResponse = { data: { id: 1, username: 'user1' } };
    axios.post.mockResolvedValue(mockResponse);

    const response = await addUser({ username: 'user1', password: 'password' });
    expect(response).toEqual(mockResponse.data);
    expect(axios.post).toHaveBeenCalledWith('/api/admin/users', { username: 'user1', password: 'password' });
  });

  test('updateUser function', async () => {
    const mockResponse = { data: { id: 1, username: 'updatedUser1' } };
    axios.put.mockResolvedValue(mockResponse);

    const response = await updateUser(1, { username: 'updatedUser1', password: 'newpassword' });
    expect(response).toEqual(mockResponse.data);
    expect(axios.put).toHaveBeenCalledWith('/api/admin/users/1', { username: 'updatedUser1', password: 'newpassword' });
  });

  test('deleteUser function', async () => {
    const mockResponse = { data: {} };
    axios.delete.mockResolvedValue(mockResponse);

    const response = await deleteUser(1);
    expect(response).toEqual(mockResponse.data);
    expect(axios.delete).toHaveBeenCalledWith('/api/admin/users/1');
  });

  test('exportData function', async () => {
    const mockResponse = { data: { pages: [], regions: [], categories: [], links: [] } };
    axios.get.mockResolvedValue(mockResponse);

    const response = await exportData();
    expect(response).toEqual(mockResponse.data);
    expect(axios.get).toHaveBeenCalledWith('/api/admin/backup/export');
  });

  test('importData function', async () => {
    const mockResponse = { data: { message: '数据导入成功' } };
    axios.post.mockResolvedValue(mockResponse);

    const formData = new FormData();
    formData.append('file', new Blob(['mocked data'], { type: 'application/json' }));

    const response = await importData(formData);
    expect(response).toEqual(mockResponse.data);
    expect(axios.post).toHaveBeenCalledWith('/api/admin/backup/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  });
});
