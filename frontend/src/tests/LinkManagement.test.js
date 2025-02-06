import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import LinkManagement from '../components/LinkManagement';
import { getCategories, getLinks, createLink, updateLink, deleteLink } from '../utils/api';

jest.mock('../utils/api');

describe('LinkManagement Component', () => {
  beforeEach(() => {
    getCategories.mockResolvedValue([
      { id: 1, title: 'Category 1' },
      { id: 2, title: 'Category 2' },
    ]);

    getLinks.mockResolvedValue([
      { id: 1, name: 'Link 1', url: 'http://link1.com', categoryId: 1 },
      { id: 2, name: 'Link 2', url: 'http://link2.com', categoryId: 2 },
    ]);
  });

  test('renders link management form', async () => {
    const { getByPlaceholderText, getByText } = render(<LinkManagement />);

    await waitFor(() => {
      expect(getByPlaceholderText(/链接名称/i)).toBeInTheDocument();
      expect(getByPlaceholderText(/链接URL/i)).toBeInTheDocument();
      expect(getByText(/选择分类/i)).toBeInTheDocument();
      expect(getByText(/创建链接/i)).toBeInTheDocument();
    });
  });

  test('creates a new link', async () => {
    createLink.mockResolvedValue({ id: 3, name: 'Link 3', url: 'http://link3.com', categoryId: 1 });

    const { getByPlaceholderText, getByText } = render(<LinkManagement />);

    fireEvent.change(getByPlaceholderText(/链接名称/i), { target: { value: 'Link 3' } });
    fireEvent.change(getByPlaceholderText(/链接URL/i), { target: { value: 'http://link3.com' } });
    fireEvent.change(getByText(/选择分类/i), { target: { value: 1 } });
    fireEvent.click(getByText(/创建链接/i));

    await waitFor(() => {
      expect(createLink).toHaveBeenCalledWith({ name: 'Link 3', url: 'http://link3.com', categoryId: 1 });
    });
  });

  test('updates an existing link', async () => {
    updateLink.mockResolvedValue({ id: 1, name: 'Updated Link 1', url: 'http://updatedlink1.com', categoryId: 1 });

    const { getByText, getByDisplayValue } = render(<LinkManagement />);

    await waitFor(() => {
      fireEvent.click(getByText(/编辑/i));
    });

    fireEvent.change(getByDisplayValue(/Link 1/i), { target: { value: 'Updated Link 1' } });
    fireEvent.change(getByDisplayValue(/http:\/\/link1.com/i), { target: { value: 'http://updatedlink1.com' } });
    fireEvent.click(getByText(/保存/i));

    await waitFor(() => {
      expect(updateLink).toHaveBeenCalledWith(1, { name: 'Updated Link 1', url: 'http://updatedlink1.com', categoryId: 1 });
    });
  });

  test('deletes a link', async () => {
    deleteLink.mockResolvedValue({});

    const { getByText } = render(<LinkManagement />);

    await waitFor(() => {
      fireEvent.click(getByText(/删除/i));
    });

    await waitFor(() => {
      expect(deleteLink).toHaveBeenCalledWith(1);
    });
  });
});
