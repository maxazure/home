import React, { useState, useEffect } from 'react';
import { getPages, createPage, updatePage, deletePage } from '../utils/api';

const PageManagement = () => {
  const [pages, setPages] = useState([]);
  const [newPageName, setNewPageName] = useState('');
  const [editPageId, setEditPageId] = useState(null);
  const [editPageName, setEditPageName] = useState('');

  useEffect(() => {
    fetchPages();
  }, []);

  const fetchPages = async () => {
    const response = await getPages();
    setPages(response);
  };

  const handleCreatePage = async () => {
    if (newPageName.trim() === '') return;
    await createPage({ name: newPageName });
    setNewPageName('');
    fetchPages();
  };

  const handleUpdatePage = async (id) => {
    if (editPageName.trim() === '') return;
    await updatePage(id, { name: editPageName });
    setEditPageId(null);
    setEditPageName('');
    fetchPages();
  };

  const handleDeletePage = async (id) => {
    await deletePage(id);
    fetchPages();
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">页面管理</h1>
      <div className="mb-4">
        <input
          type="text"
          value={newPageName}
          onChange={(e) => setNewPageName(e.target.value)}
          placeholder="新页面名称"
          className="border p-2 mr-2"
        />
        <button onClick={handleCreatePage} className="bg-blue-500 text-white p-2">创建页面</button>
      </div>
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th className="py-2">ID</th>
            <th className="py-2">名称</th>
            <th className="py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          {pages.map((page) => (
            <tr key={page.id}>
              <td className="border px-4 py-2">{page.id}</td>
              <td className="border px-4 py-2">
                {editPageId === page.id ? (
                  <input
                    type="text"
                    value={editPageName}
                    onChange={(e) => setEditPageName(e.target.value)}
                    className="border p-2"
                  />
                ) : (
                  page.name
                )}
              </td>
              <td className="border px-4 py-2">
                {editPageId === page.id ? (
                  <button onClick={() => handleUpdatePage(page.id)} className="bg-green-500 text-white p-2 mr-2">保存</button>
                ) : (
                  <button onClick={() => { setEditPageId(page.id); setEditPageName(page.name); }} className="bg-yellow-500 text-white p-2 mr-2">编辑</button>
                )}
                <button onClick={() => handleDeletePage(page.id)} className="bg-red-500 text-white p-2">删除</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PageManagement;
