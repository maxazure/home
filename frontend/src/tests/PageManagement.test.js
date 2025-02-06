import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import PageManagement from '../components/PageManagement';
import { getPages, createPage, updatePage, deletePage } from '../utils/api';

jest.mock('../utils/api');

describe('PageManagement Component', () => {
  beforeEach(() => {
    getPages.mockResolvedValue([
      { id: 1, name: 'Page 1' },
      { id: 2, name: 'Page 2' },
    ]);
  });

  test('renders page management component', async () => {
    render(<PageManagement />);
    expect(screen.getByText('页面管理')).toBeInTheDocument();
    expect(await screen.findByText('Page 1')).toBeInTheDocument();
    expect(await screen.findByText('Page 2')).toBeInTheDocument();
  });

  test('creates a new page', async () => {
    createPage.mockResolvedValue({ id: 3, name: 'Page 3' });
    render(<PageManagement />);
    fireEvent.change(screen.getByPlaceholderText('新页面名称'), { target: { value: 'Page 3' } });
    fireEvent.click(screen.getByText('创建页面'));
    expect(await screen.findByText('Page 3')).toBeInTheDocument();
  });

  test('updates an existing page', async () => {
    updatePage.mockResolvedValue({ id: 1, name: 'Updated Page 1' });
    render(<PageManagement />);
    fireEvent.click(await screen.findByText('编辑'));
    fireEvent.change(screen.getByDisplayValue('Page 1'), { target: { value: 'Updated Page 1' } });
    fireEvent.click(screen.getByText('保存'));
    expect(await screen.findByText('Updated Page 1')).toBeInTheDocument();
  });

  test('deletes a page', async () => {
    deletePage.mockResolvedValue({});
    render(<PageManagement />);
    fireEvent.click(await screen.findByText('删除'));
    expect(screen.queryByText('Page 1')).not.toBeInTheDocument();
  });
});
