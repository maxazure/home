import React, { useState, useEffect } from 'react';
import { getCategories, getLinks, createLink, updateLink, deleteLink } from '../utils/api';

const LinkManagement = () => {
  const [categories, setCategories] = useState([]);
  const [links, setLinks] = useState([]);
  const [newLink, setNewLink] = useState({ name: '', url: '', categoryId: '' });
  const [editLinkId, setEditLinkId] = useState(null);
  const [editLink, setEditLink] = useState({ name: '', url: '', categoryId: '' });

  useEffect(() => {
    fetchCategories();
    fetchLinks();
  }, []);

  const fetchCategories = async () => {
    const response = await getCategories();
    setCategories(response);
  };

  const fetchLinks = async () => {
    const response = await getLinks();
    setLinks(response);
  };

  const handleCreateLink = async () => {
    if (newLink.name.trim() === '' || newLink.url.trim() === '' || newLink.categoryId === '') return;
    await createLink(newLink);
    setNewLink({ name: '', url: '', categoryId: '' });
    fetchLinks();
  };

  const handleUpdateLink = async (id) => {
    if (editLink.name.trim() === '' || editLink.url.trim() === '' || editLink.categoryId === '') return;
    await updateLink(id, editLink);
    setEditLinkId(null);
    setEditLink({ name: '', url: '', categoryId: '' });
    fetchLinks();
  };

  const handleDeleteLink = async (id) => {
    await deleteLink(id);
    fetchLinks();
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">链接管理</h1>
      <div className="mb-4">
        <input
          type="text"
          value={newLink.name}
          onChange={(e) => setNewLink({ ...newLink, name: e.target.value })}
          placeholder="链接名称"
          className="border p-2 mr-2"
        />
        <input
          type="url"
          value={newLink.url}
          onChange={(e) => setNewLink({ ...newLink, url: e.target.value })}
          placeholder="链接URL"
          className="border p-2 mr-2"
        />
        <select
          value={newLink.categoryId}
          onChange={(e) => setNewLink({ ...newLink, categoryId: e.target.value })}
          className="border p-2 mr-2"
        >
          <option value="">选择分类</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.title}
            </option>
          ))}
        </select>
        <button onClick={handleCreateLink} className="bg-blue-500 text-white p-2">创建链接</button>
      </div>
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th className="py-2">ID</th>
            <th className="py-2">名称</th>
            <th className="py-2">URL</th>
            <th className="py-2">分类</th>
            <th className="py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          {links.map((link) => (
            <tr key={link.id}>
              <td className="border px-4 py-2">{link.id}</td>
              <td className="border px-4 py-2">
                {editLinkId === link.id ? (
                  <input
                    type="text"
                    value={editLink.name}
                    onChange={(e) => setEditLink({ ...editLink, name: e.target.value })}
                    className="border p-2"
                  />
                ) : (
                  link.name
                )}
              </td>
              <td className="border px-4 py-2">
                {editLinkId === link.id ? (
                  <input
                    type="url"
                    value={editLink.url}
                    onChange={(e) => setEditLink({ ...editLink, url: e.target.value })}
                    className="border p-2"
                  />
                ) : (
                  <a href={link.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                    {link.url}
                  </a>
                )}
              </td>
              <td className="border px-4 py-2">
                {editLinkId === link.id ? (
                  <select
                    value={editLink.categoryId}
                    onChange={(e) => setEditLink({ ...editLink, categoryId: e.target.value })}
                    className="border p-2"
                  >
                    <option value="">选择分类</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.title}
                      </option>
                    ))}
                  </select>
                ) : (
                  categories.find((category) => category.id === link.categoryId)?.title
                )}
              </td>
              <td className="border px-4 py-2">
                {editLinkId === link.id ? (
                  <button onClick={() => handleUpdateLink(link.id)} className="bg-green-500 text-white p-2 mr-2">保存</button>
                ) : (
                  <button onClick={() => { setEditLinkId(link.id); setEditLink({ name: link.name, url: link.url, categoryId: link.categoryId }); }} className="bg-yellow-500 text-white p-2 mr-2">编辑</button>
                )}
                <button onClick={() => handleDeleteLink(link.id)} className="bg-red-500 text-white p-2">删除</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LinkManagement;
