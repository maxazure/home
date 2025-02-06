import React, { useState } from 'react';
import { exportData, importData } from '../utils/api';

const DataBackup = () => {
  const [importFile, setImportFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleExport = async () => {
    try {
      const response = await exportData();
      const blob = new Blob([JSON.stringify(response)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'backup.json';
      a.click();
      URL.revokeObjectURL(url);
      setMessage('数据导出成功');
    } catch (error) {
      setMessage('数据导出失败');
    }
  };

  const handleImport = async () => {
    if (!importFile) {
      setMessage('请选择一个文件');
      return;
    }

    const formData = new FormData();
    formData.append('file', importFile);

    try {
      await importData(formData);
      setMessage('数据导入成功');
    } catch (error) {
      setMessage('数据导入失败');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">数据备份</h1>
      <div className="mb-4">
        <button onClick={handleExport} className="bg-blue-500 text-white p-2 mr-2">导出数据</button>
        <input
          type="file"
          onChange={(e) => setImportFile(e.target.files[0])}
          className="border p-2 mr-2"
        />
        <button onClick={handleImport} className="bg-green-500 text-white p-2">导入数据</button>
      </div>
      {message && <p className="text-red-500">{message}</p>}
    </div>
  );
};

export default DataBackup;
