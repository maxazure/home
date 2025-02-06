import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import DataBackup from '../components/DataBackup';
import { exportData, importData } from '../utils/api';

jest.mock('../utils/api');

describe('DataBackup Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render DataBackup component', () => {
    const { getByText } = render(<DataBackup />);
    expect(getByText('数据备份')).toBeInTheDocument();
  });

  test('should export data successfully', async () => {
    exportData.mockResolvedValue({ data: 'mocked data' });

    const { getByText } = render(<DataBackup />);
    const exportButton = getByText('导出数据');

    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(exportData).toHaveBeenCalled();
      expect(getByText('数据导出成功')).toBeInTheDocument();
    });
  });

  test('should handle export data failure', async () => {
    exportData.mockRejectedValue(new Error('Export failed'));

    const { getByText } = render(<DataBackup />);
    const exportButton = getByText('导出数据');

    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(exportData).toHaveBeenCalled();
      expect(getByText('数据导出失败')).toBeInTheDocument();
    });
  });

  test('should import data successfully', async () => {
    importData.mockResolvedValue({ message: '数据导入成功' });

    const { getByText, getByPlaceholderText } = render(<DataBackup />);
    const importButton = getByText('导入数据');
    const fileInput = getByPlaceholderText('选择文件');

    fireEvent.change(fileInput, { target: { files: [new File(['mocked data'], 'mockedData.json', { type: 'application/json' })] } });
    fireEvent.click(importButton);

    await waitFor(() => {
      expect(importData).toHaveBeenCalled();
      expect(getByText('数据导入成功')).toBeInTheDocument();
    });
  });

  test('should handle import data failure', async () => {
    importData.mockRejectedValue(new Error('Import failed'));

    const { getByText, getByPlaceholderText } = render(<DataBackup />);
    const importButton = getByText('导入数据');
    const fileInput = getByPlaceholderText('选择文件');

    fireEvent.change(fileInput, { target: { files: [new File(['mocked data'], 'mockedData.json', { type: 'application/json' })] } });
    fireEvent.click(importButton);

    await waitFor(() => {
      expect(importData).toHaveBeenCalled();
      expect(getByText('数据导入失败')).toBeInTheDocument();
    });
  });
});
